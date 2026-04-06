"""schemas.py のバリデーションテスト"""

import pytest
from pydantic import ValidationError

from schemas import ChatRequest, ChatResponse, SourceInfo, DocumentResponse, DocumentStats


class TestChatRequest:
    """ChatRequest モデルのバリデーションテスト"""

    def test_valid_question(self):
        """有効な質問は正常に作成される"""
        req = ChatRequest(question="社内の有給休暇ポリシーについて教えてください")
        assert req.question == "社内の有給休暇ポリシーについて教えてください"

    def test_empty_question_raises_validation_error(self):
        """空文字列の質問はバリデーションエラー"""
        with pytest.raises(ValidationError):
            ChatRequest(question="")

    def test_whitespace_only_question_raises_validation_error(self):
        """空白のみの質問はバリデーションエラー"""
        with pytest.raises(ValidationError):
            ChatRequest(question="   \n\t  ")

    def test_question_is_stripped(self):
        """質問の前後の空白は除去される"""
        req = ChatRequest(question="  テスト質問  ")
        assert req.question == "テスト質問"

    def test_question_too_long_raises_validation_error(self):
        """10000文字を超える質問はバリデーションエラー"""
        with pytest.raises(ValidationError):
            ChatRequest(question="あ" * 10001)

    def test_question_at_max_length(self):
        """10000文字の質問は有効"""
        req = ChatRequest(question="あ" * 10000)
        assert len(req.question) == 10000

    def test_question_with_newlines(self):
        """改行を含む質問は有効"""
        question = "質問1\n質問2\n質問3"
        req = ChatRequest(question=question)
        assert req.question == question


class TestChatResponse:
    """ChatResponse モデルのテスト"""

    def test_valid_chat_response(self):
        """有効な回答レスポンスは正常に作成される"""
        source = SourceInfo(filename="test.pdf", excerpt="テスト抜粋", score=0.85)
        resp = ChatResponse(
            answer="テスト回答です。",
            sources=[source],
            confidence="high",
        )
        assert resp.answer == "テスト回答です。"
        assert len(resp.sources) == 1
        assert resp.confidence == "high"

    def test_empty_sources(self):
        """ソースなしの回答も有効"""
        resp = ChatResponse(
            answer="情報が見つかりませんでした。",
            sources=[],
            confidence="unknown",
        )
        assert resp.sources == []
        assert resp.confidence == "unknown"
