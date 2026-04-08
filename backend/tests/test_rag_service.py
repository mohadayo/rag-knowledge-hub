"""rag_service.py のユニットテスト"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock, patch  # noqa: E402


class TestAskNoResults:
    """根拠なしの回答テスト"""

    @patch("services.rag_service.search")
    @patch("services.rag_service.generate_embedding")
    def test_empty_vector_results_returns_unknown_confidence(
        self, mock_embedding, mock_search
    ):
        """ベクトル検索結果が空の場合はconfidence=unknownを返す"""
        mock_embedding.return_value = [0.1] * 1536
        mock_search.return_value = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        from services.rag_service import ask

        result = ask("テスト質問")

        assert result.confidence == "unknown"
        assert result.sources == []
        assert "見つかりませんでした" in result.answer

    @patch("services.rag_service.search")
    @patch("services.rag_service.generate_embedding")
    def test_all_below_threshold_returns_unknown_confidence(
        self, mock_embedding, mock_search
    ):
        """類似度が閾値以下の場合はconfidence=unknownを返す"""
        mock_embedding.return_value = [0.1] * 1536
        # distance=0.8 → similarity=0.2, threshold=0.3なのでフィルタされる
        mock_search.return_value = {
            "documents": [["テスト文書"]],
            "metadatas": [[{"filename": "test.txt", "document_id": 1, "chunk_index": 0}]],
            "distances": [[0.8]],
        }

        from services.rag_service import ask

        result = ask("テスト質問")

        assert result.confidence == "unknown"
        assert result.sources == []


class TestAskWithResults:
    """回答あり・信頼度判定テスト"""

    def _make_mock_openai_response(self, content: str):
        """OpenAI APIレスポンスのモックを作成する"""
        mock_message = MagicMock()
        mock_message.content = content
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage = MagicMock()
        mock_response.usage.__str__ = lambda self: "usage"
        return mock_response

    @patch("services.rag_service._get_client")
    @patch("services.rag_service.search")
    @patch("services.rag_service.generate_embedding")
    def test_high_similarity_returns_high_confidence(
        self, mock_embedding, mock_search, mock_get_client
    ):
        """平均類似度 >= 0.7 の場合はconfidence=highを返す"""
        mock_embedding.return_value = [0.1] * 1536
        # distance=0.1 → similarity=0.9
        mock_search.return_value = {
            "documents": [["高品質な文書コンテンツ"]],
            "metadatas": [[{"filename": "doc.txt", "document_id": 1, "chunk_index": 0}]],
            "distances": [[0.1]],
        }

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._make_mock_openai_response(
            "高品質な回答です。"
        )
        mock_get_client.return_value = mock_client

        from services.rag_service import ask

        result = ask("テスト質問")

        assert result.confidence == "high"
        assert len(result.sources) == 1
        assert result.sources[0].filename == "doc.txt"
        assert result.answer == "高品質な回答です。"

    @patch("services.rag_service._get_client")
    @patch("services.rag_service.search")
    @patch("services.rag_service.generate_embedding")
    def test_medium_similarity_returns_medium_confidence(
        self, mock_embedding, mock_search, mock_get_client
    ):
        """平均類似度 0.5 <= x < 0.7 の場合はconfidence=mediumを返す"""
        mock_embedding.return_value = [0.1] * 1536
        # distance=0.4 → similarity=0.6
        mock_search.return_value = {
            "documents": [["中程度の品質の文書"]],
            "metadatas": [[{"filename": "medium.txt", "document_id": 2, "chunk_index": 0}]],
            "distances": [[0.4]],
        }

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._make_mock_openai_response(
            "中程度の回答です。"
        )
        mock_get_client.return_value = mock_client

        from services.rag_service import ask

        result = ask("テスト質問")

        assert result.confidence == "medium"
        assert len(result.sources) == 1

    @patch("services.rag_service._get_client")
    @patch("services.rag_service.search")
    @patch("services.rag_service.generate_embedding")
    def test_low_similarity_returns_low_confidence(
        self, mock_embedding, mock_search, mock_get_client
    ):
        """平均類似度 < 0.5 の場合はconfidence=lowを返す"""
        mock_embedding.return_value = [0.1] * 1536
        # distance=0.65 → similarity=0.35, threshold=0.3を超えるがsimilarity < 0.5
        mock_search.return_value = {
            "documents": [["低品質の文書"]],
            "metadatas": [[{"filename": "low.txt", "document_id": 3, "chunk_index": 0}]],
            "distances": [[0.65]],
        }

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._make_mock_openai_response(
            "低品質の回答です。"
        )
        mock_get_client.return_value = mock_client

        from services.rag_service import ask

        result = ask("テスト質問")

        assert result.confidence == "low"

    @patch("services.rag_service._get_client")
    @patch("services.rag_service.search")
    @patch("services.rag_service.generate_embedding")
    def test_source_excerpt_truncated_at_200_chars(
        self, mock_embedding, mock_search, mock_get_client
    ):
        """200文字を超えるチャンクはexcerptが省略される"""
        long_text = "あ" * 300
        mock_embedding.return_value = [0.1] * 1536
        mock_search.return_value = {
            "documents": [[long_text]],
            "metadatas": [[{"filename": "long.txt", "document_id": 4, "chunk_index": 0}]],
            "distances": [[0.1]],
        }

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._make_mock_openai_response(
            "回答です。"
        )
        mock_get_client.return_value = mock_client

        from services.rag_service import ask

        result = ask("テスト質問")

        assert len(result.sources) == 1
        assert result.sources[0].excerpt.endswith("...")
        assert len(result.sources[0].excerpt) == 203  # 200文字 + "..."

    @patch("services.rag_service._get_client")
    @patch("services.rag_service.search")
    @patch("services.rag_service.generate_embedding")
    def test_multiple_sources_averaged_for_confidence(
        self, mock_embedding, mock_search, mock_get_client
    ):
        """複数ソースの平均類似度でconfidenceが決定される"""
        mock_embedding.return_value = [0.1] * 1536
        # distance=[0.1, 0.5] → similarity=[0.9, 0.5] → avg=0.7 → high
        mock_search.return_value = {
            "documents": [["文書1", "文書2"]],
            "metadatas": [
                [
                    {"filename": "doc1.txt", "document_id": 1, "chunk_index": 0},
                    {"filename": "doc2.txt", "document_id": 2, "chunk_index": 0},
                ]
            ],
            "distances": [[0.1, 0.5]],
        }

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._make_mock_openai_response(
            "複数ソースからの回答。"
        )
        mock_get_client.return_value = mock_client

        from services.rag_service import ask

        result = ask("テスト質問")

        assert len(result.sources) == 2
        assert result.confidence == "high"

    @patch("services.rag_service._get_client")
    @patch("services.rag_service.search")
    @patch("services.rag_service.generate_embedding")
    def test_source_score_rounded_to_3_decimals(
        self, mock_embedding, mock_search, mock_get_client
    ):
        """ソースのscoreが小数点3桁に丸められる"""
        mock_embedding.return_value = [0.1] * 1536
        mock_search.return_value = {
            "documents": [["テスト文書"]],
            "metadatas": [[{"filename": "test.txt", "document_id": 1, "chunk_index": 0}]],
            "distances": [[0.12345678]],
        }

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._make_mock_openai_response(
            "回答。"
        )
        mock_get_client.return_value = mock_client

        from services.rag_service import ask

        result = ask("テスト質問")

        assert len(result.sources) == 1
        score = result.sources[0].score
        # scoreは小数点3桁以内
        assert score == round(score, 3)
