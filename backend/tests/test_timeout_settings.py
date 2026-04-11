"""OpenAI APIタイムアウト設定のユニットテスト"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock  # noqa: E402

import httpx  # noqa: E402


class TestRagServiceTimeout:
    """rag_service の OpenAI クライアントタイムアウト設定テスト"""

    def setup_method(self):
        """各テストの前にクライアントキャッシュをリセット"""
        import services.rag_service as mod
        mod._client = None

    @patch("services.rag_service.OpenAI")
    def test_rag_client_has_timeout(self, mock_openai_cls):
        """rag_service の _get_client が httpx.Timeout を設定して OpenAI を初期化する"""
        mock_openai_cls.return_value = MagicMock()

        from services.rag_service import _get_client
        _get_client()

        mock_openai_cls.assert_called_once()
        call_kwargs = mock_openai_cls.call_args[1]
        assert "timeout" in call_kwargs
        timeout = call_kwargs["timeout"]
        assert isinstance(timeout, httpx.Timeout)
        assert timeout.read == 30.0
        assert timeout.connect == 10.0

    @patch("services.rag_service.OpenAI")
    def test_rag_client_uses_config_values(self, mock_openai_cls):
        """rag_service が config の設定値を使用してタイムアウトを設定する"""
        mock_openai_cls.return_value = MagicMock()

        with patch("services.rag_service.settings") as mock_settings:
            mock_settings.openai_api_key = "test-key"
            mock_settings.openai_timeout = 60.0
            mock_settings.openai_connect_timeout = 20.0

            import services.rag_service as mod
            mod._client = None

            from services.rag_service import _get_client
            _get_client()

            call_kwargs = mock_openai_cls.call_args[1]
            timeout = call_kwargs["timeout"]
            assert timeout.read == 60.0
            assert timeout.connect == 20.0


class TestEmbeddingServiceTimeout:
    """embedding_service の OpenAI クライアントタイムアウト設定テスト"""

    def setup_method(self):
        """各テストの前にクライアントキャッシュをリセット"""
        import services.embedding_service as mod
        mod._client = None

    @patch("services.embedding_service.OpenAI")
    def test_embedding_client_has_timeout(self, mock_openai_cls):
        """embedding_service の _get_client が httpx.Timeout を設定して OpenAI を初期化する"""
        mock_openai_cls.return_value = MagicMock()

        from services.embedding_service import _get_client
        _get_client()

        mock_openai_cls.assert_called_once()
        call_kwargs = mock_openai_cls.call_args[1]
        assert "timeout" in call_kwargs
        timeout = call_kwargs["timeout"]
        assert isinstance(timeout, httpx.Timeout)
        assert timeout.read == 30.0
        assert timeout.connect == 10.0

    @patch("services.embedding_service.OpenAI")
    def test_embedding_client_uses_config_values(self, mock_openai_cls):
        """embedding_service が config の設定値を使用してタイムアウトを設定する"""
        mock_openai_cls.return_value = MagicMock()

        with patch("services.embedding_service.settings") as mock_settings:
            mock_settings.openai_api_key = "test-key"
            mock_settings.openai_timeout = 45.0
            mock_settings.openai_connect_timeout = 15.0

            import services.embedding_service as mod
            mod._client = None

            from services.embedding_service import _get_client
            _get_client()

            call_kwargs = mock_openai_cls.call_args[1]
            timeout = call_kwargs["timeout"]
            assert timeout.read == 45.0
            assert timeout.connect == 15.0


class TestConfigTimeoutDefaults:
    """config.py のタイムアウトデフォルト値テスト"""

    def test_default_timeout_values(self):
        """デフォルトのタイムアウト値が正しく設定されている"""
        from config import Settings
        s = Settings(openai_api_key="test")
        assert s.openai_timeout == 30.0
        assert s.openai_connect_timeout == 10.0
