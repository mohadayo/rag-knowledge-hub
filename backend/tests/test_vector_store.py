"""services/vector_store.py のユニットテスト"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock, patch  # noqa: E402


class TestGetCollection:
    """get_collection 関数のテスト"""

    def setup_method(self):
        import services.vector_store as vs
        vs._client = None

    @patch("services.vector_store.chromadb")
    def test_get_collection_creates_client_on_first_call(self, mock_chromadb):
        """初回呼び出しでPersistentClientが生成される"""
        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection

        from services.vector_store import get_collection
        result = get_collection()

        mock_chromadb.PersistentClient.assert_called_once()
        mock_client.get_or_create_collection.assert_called_once_with(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"},
        )
        assert result == mock_collection

    @patch("services.vector_store.chromadb")
    def test_get_collection_reuses_client(self, mock_chromadb):
        """2回目以降はキャッシュされたクライアントを使用する"""
        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client

        import services.vector_store as vs
        vs._client = None

        from services.vector_store import get_collection
        get_collection()
        get_collection()

        mock_chromadb.PersistentClient.assert_called_once()


class TestAddChunks:
    """add_chunks 関数のテスト"""

    @patch("services.vector_store.get_collection")
    def test_add_chunks_creates_correct_ids_and_metadatas(self, mock_get_collection):
        """チャンク追加時に正しいID・メタデータが生成される"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        from services.vector_store import add_chunks

        chunks = ["チャンク1", "チャンク2", "チャンク3"]
        embeddings = [[0.1] * 10, [0.2] * 10, [0.3] * 10]

        add_chunks(42, "report.pdf", chunks, embeddings)

        mock_collection.add.assert_called_once()
        call_kwargs = mock_collection.add.call_args[1]

        assert call_kwargs["ids"] == ["doc42_chunk0", "doc42_chunk1", "doc42_chunk2"]
        assert call_kwargs["documents"] == chunks
        assert call_kwargs["embeddings"] == embeddings
        assert len(call_kwargs["metadatas"]) == 3
        assert call_kwargs["metadatas"][0] == {
            "document_id": 42,
            "filename": "report.pdf",
            "chunk_index": 0,
        }
        assert call_kwargs["metadatas"][2]["chunk_index"] == 2

    @patch("services.vector_store.get_collection")
    def test_add_chunks_single_chunk(self, mock_get_collection):
        """1チャンクの場合も正しく動作する"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        from services.vector_store import add_chunks

        add_chunks(1, "test.txt", ["テキスト"], [[0.5] * 10])

        call_kwargs = mock_collection.add.call_args[1]
        assert call_kwargs["ids"] == ["doc1_chunk0"]
        assert len(call_kwargs["metadatas"]) == 1


class TestSearch:
    """search 関数のテスト"""

    @patch("services.vector_store.get_collection")
    def test_search_returns_results(self, mock_get_collection):
        """ベクトル検索が正常にresultsを返す"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.count.return_value = 10

        expected_results = {
            "documents": [["doc1", "doc2"]],
            "metadatas": [[{"filename": "a.txt"}, {"filename": "b.txt"}]],
            "distances": [[0.1, 0.3]],
        }
        mock_collection.query.return_value = expected_results

        from services.vector_store import search

        query_embedding = [0.1] * 10
        results = search(query_embedding, n_results=5)

        assert results == expected_results
        mock_collection.query.assert_called_once_with(
            query_embeddings=[query_embedding],
            n_results=5,
            include=["documents", "metadatas", "distances"],
        )

    @patch("services.vector_store.get_collection")
    def test_search_empty_collection_returns_empty(self, mock_get_collection):
        """空のコレクションの場合、空の結果を返す"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.count.return_value = 0

        from services.vector_store import search

        results = search([0.1] * 10, n_results=5)

        assert results == {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        mock_collection.query.assert_not_called()

    @patch("services.vector_store.get_collection")
    def test_search_limits_n_results_to_total(self, mock_get_collection):
        """n_resultsがコレクション件数を超える場合、件数に制限される"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.count.return_value = 3
        mock_collection.query.return_value = {
            "documents": [["doc1", "doc2", "doc3"]],
            "metadatas": [[{}, {}, {}]],
            "distances": [[0.1, 0.2, 0.3]],
        }

        from services.vector_store import search

        search([0.1] * 10, n_results=10)

        call_kwargs = mock_collection.query.call_args[1]
        assert call_kwargs["n_results"] == 3


class TestDeleteByDocumentId:
    """delete_by_document_id 関数のテスト"""

    @patch("services.vector_store.get_collection")
    def test_delete_existing_document(self, mock_get_collection):
        """既存ドキュメントのチャンクが削除される"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.get.return_value = {
            "ids": ["doc5_chunk0", "doc5_chunk1", "doc5_chunk2"],
        }

        from services.vector_store import delete_by_document_id

        delete_by_document_id(5)

        mock_collection.get.assert_called_once_with(
            where={"document_id": 5},
            include=[],
        )
        mock_collection.delete.assert_called_once_with(
            ids=["doc5_chunk0", "doc5_chunk1", "doc5_chunk2"],
        )

    @patch("services.vector_store.get_collection")
    def test_delete_nonexistent_document(self, mock_get_collection):
        """存在しないドキュメントの削除はdeleteを呼ばない"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.get.return_value = {"ids": []}

        from services.vector_store import delete_by_document_id

        delete_by_document_id(999)

        mock_collection.get.assert_called_once()
        mock_collection.delete.assert_not_called()
