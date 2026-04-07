"""routers/chat.py のエンドポイントテスト"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from routers.chat import router
from schemas import ChatResponse, SourceInfo


@pytest.fixture
def app():
    """テスト用FastAPIアプリケーション"""
    test_app = FastAPI()
    test_app.include_router(router)
    return test_app


@pytest.fixture
def client(app):
    """テスト用クライアント"""
    return TestClient(app)


class TestChatEndpoint:
    """POST /api/chat エンドポイントのテスト"""

    @patch("routers.chat.ask")
    def test_valid_question_returns_200(self, mock_ask, client):
        """有効な質問に対して200レスポンスを返す"""
        mock_ask.return_value = ChatResponse(
            answer="テスト回答です。",
            sources=[
                SourceInfo(filename="doc.txt", excerpt="テスト抜粋", score=0.85)
            ],
            confidence="high",
        )

        response = client.post("/api/chat", json={"question": "テスト質問"})

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "テスト回答です。"
        assert data["confidence"] == "high"
        assert len(data["sources"]) == 1
        assert data["sources"][0]["filename"] == "doc.txt"

    @patch("routers.chat.ask")
    def test_empty_question_returns_422(self, mock_ask, client):
        """空の質問に対して422バリデーションエラーを返す"""
        response = client.post("/api/chat", json={"question": ""})

        assert response.status_code == 422
        mock_ask.assert_not_called()

    @patch("routers.chat.ask")
    def test_whitespace_question_returns_422(self, mock_ask, client):
        """空白のみの質問に対して422バリデーションエラーを返す"""
        response = client.post("/api/chat", json={"question": "   \n  "})

        assert response.status_code == 422
        mock_ask.assert_not_called()

    @patch("routers.chat.ask")
    def test_too_long_question_returns_422(self, mock_ask, client):
        """10000文字を超える質問に対して422バリデーションエラーを返す"""
        response = client.post("/api/chat", json={"question": "あ" * 10001})

        assert response.status_code == 422
        mock_ask.assert_not_called()

    @patch("routers.chat.ask")
    def test_service_error_returns_503(self, mock_ask, client):
        """サービスエラー時に503レスポンスを返す"""
        mock_ask.side_effect = Exception("OpenAI APIエラー")

        response = client.post("/api/chat", json={"question": "テスト質問"})

        assert response.status_code == 503
        data = response.json()
        assert "detail" in data

    @patch("routers.chat.ask")
    def test_empty_sources_response(self, mock_ask, client):
        """ソースなし（unknown confidence）の回答も正常に返す"""
        mock_ask.return_value = ChatResponse(
            answer="情報が見つかりませんでした。",
            sources=[],
            confidence="unknown",
        )

        response = client.post("/api/chat", json={"question": "存在しない情報の質問"})

        assert response.status_code == 200
        data = response.json()
        assert data["confidence"] == "unknown"
        assert data["sources"] == []

    @patch("routers.chat.ask")
    def test_missing_question_field_returns_422(self, mock_ask, client):
        """questionフィールドが欠落している場合に422を返す"""
        response = client.post("/api/chat", json={})

        assert response.status_code == 422
        mock_ask.assert_not_called()

    @patch("routers.chat.ask")
    def test_ask_called_with_stripped_question(self, mock_ask, client):
        """前後の空白が除去された質問でaskが呼ばれる"""
        mock_ask.return_value = ChatResponse(
            answer="回答です。",
            sources=[],
            confidence="low",
        )

        response = client.post("/api/chat", json={"question": "  テスト質問  "})

        assert response.status_code == 200
        # バリデーターでstripされてから呼ばれる
        mock_ask.assert_called_once_with("テスト質問")
