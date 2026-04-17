"""routers/documents.py のエンドポイントテスト"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from io import BytesIO  # noqa: E402

from routers.documents import router  # noqa: E402


class FakeDocument:
    """テスト用のDocumentモデル代替"""
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", 1)
        self.filename = kwargs.get("filename", "test.txt")
        self.file_type = kwargs.get("file_type", "txt")
        self.file_size = kwargs.get("file_size", 100)
        self.chunk_count = kwargs.get("chunk_count", 0)
        self.status = kwargs.get("status", "processing")
        self.uploaded_at = kwargs.get("uploaded_at", "2026-01-01T00:00:00")


class FakeScalarResult:
    """scalar_one_or_none の返り値を模倣"""
    def __init__(self, value=None):
        self._value = value

    def scalar_one_or_none(self):
        return self._value

    def scalar_one(self):
        return self._value if self._value is not None else 0

    def scalars(self):
        return self

    def all(self):
        return self._value if self._value else []

    def one(self):
        return self._value


class FakeDBSession:
    """テスト用の非同期DBセッション"""
    def __init__(self, existing_doc=None):
        self._existing_doc = existing_doc
        self._added = []
        self._deleted = []
        self._committed = False

    async def execute(self, stmt):
        return FakeScalarResult(self._existing_doc)

    def add(self, obj):
        self._added.append(obj)

    async def commit(self):
        self._committed = True

    async def refresh(self, obj):
        if not hasattr(obj, "id") or obj.id is None:
            obj.id = 1
        if not hasattr(obj, "uploaded_at") or obj.uploaded_at is None:
            obj.uploaded_at = "2026-01-01T00:00:00"

    async def delete(self, obj):
        self._deleted.append(obj)


def create_test_app(existing_doc=None):
    """テスト用アプリケーション生成"""
    test_app = FastAPI()
    test_app.include_router(router)

    db_session = FakeDBSession(existing_doc=existing_doc)

    async def override_get_db():
        yield db_session

    from database import get_db
    test_app.dependency_overrides[get_db] = override_get_db

    return test_app, db_session


class TestUploadDuplicateDetection:
    """重複ドキュメント検知のテスト"""

    def test_duplicate_filename_returns_409(self):
        """同名ファイルが既に存在する場合、409を返す"""
        existing = FakeDocument(filename="test.txt", status="ready")
        app, _ = create_test_app(existing_doc=existing)
        client = TestClient(app)

        file_content = b"test content"
        response = client.post(
            "/api/documents/upload",
            files={"file": ("test.txt", BytesIO(file_content), "text/plain")},
        )

        assert response.status_code == 409
        data = response.json()
        assert "既に登録済み" in data["detail"]

    @patch("routers.documents.generate_embeddings")
    @patch("routers.documents.add_chunks")
    @patch("routers.documents.extract_text")
    @patch("routers.documents.split_into_chunks")
    def test_duplicate_with_force_allows_upload(
        self, mock_split, mock_extract, mock_add, mock_embed
    ):
        """force=trueの場合、重複でもアップロードを許可する"""
        existing = FakeDocument(filename="test.txt", status="ready")
        app, _ = create_test_app(existing_doc=existing)
        client = TestClient(app)

        mock_extract.return_value = "テストコンテンツ"
        mock_split.return_value = ["チャンク1"]
        mock_embed.return_value = [[0.1] * 10]

        file_content = b"test content"
        response = client.post(
            "/api/documents/upload?force=true",
            files={"file": ("test.txt", BytesIO(file_content), "text/plain")},
        )

        assert response.status_code == 200

    @patch("routers.documents.generate_embeddings")
    @patch("routers.documents.add_chunks")
    @patch("routers.documents.extract_text")
    @patch("routers.documents.split_into_chunks")
    def test_new_filename_allows_upload(
        self, mock_split, mock_extract, mock_add, mock_embed
    ):
        """新規ファイル名の場合、正常にアップロードできる"""
        app, _ = create_test_app(existing_doc=None)
        client = TestClient(app)

        mock_extract.return_value = "テストコンテンツ"
        mock_split.return_value = ["チャンク1"]
        mock_embed.return_value = [[0.1] * 10]

        file_content = b"new document content"
        response = client.post(
            "/api/documents/upload",
            files={"file": ("new_doc.txt", BytesIO(file_content), "text/plain")},
        )

        assert response.status_code == 200


class TestUploadValidation:
    """アップロードバリデーションのテスト"""

    def test_no_filename_returns_error(self):
        """ファイル名なしの場合にエラーを返す"""
        app, _ = create_test_app()
        client = TestClient(app)

        response = client.post(
            "/api/documents/upload",
            files={"file": ("", BytesIO(b"content"), "text/plain")},
        )

        assert response.status_code in (400, 422)

    def test_unsupported_extension_returns_400(self):
        """未対応の拡張子の場合に400を返す"""
        app, _ = create_test_app()
        client = TestClient(app)

        response = client.post(
            "/api/documents/upload",
            files={"file": ("test.exe", BytesIO(b"content"), "application/octet-stream")},
        )

        assert response.status_code == 400
        assert "未対応" in response.json()["detail"]

    def test_file_too_large_returns_400(self):
        """ファイルサイズ上限超過で400を返す"""
        app, _ = create_test_app()
        client = TestClient(app)

        from config import settings
        large_content = b"x" * (settings.max_file_size + 1)
        response = client.post(
            "/api/documents/upload",
            files={"file": ("large.txt", BytesIO(large_content), "text/plain")},
        )

        assert response.status_code == 400
        assert "上限" in response.json()["detail"]


class TestListDocumentsPagination:
    """ドキュメント一覧ページネーションのテスト"""

    def test_list_returns_paginated_response(self):
        """ページネーション形式で一覧を返す"""
        app, _ = create_test_app()
        client = TestClient(app)

        response = client.get("/api/documents")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "offset" in data
        assert "limit" in data
        assert data["offset"] == 0
        assert data["limit"] == 20

    def test_list_with_custom_offset_and_limit(self):
        """offset/limitパラメータが反映される"""
        app, _ = create_test_app()
        client = TestClient(app)

        response = client.get("/api/documents?offset=5&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["offset"] == 5
        assert data["limit"] == 10

    def test_list_limit_capped_at_100(self):
        """limitの上限は100"""
        app, _ = create_test_app()
        client = TestClient(app)

        response = client.get("/api/documents?limit=200")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 100
