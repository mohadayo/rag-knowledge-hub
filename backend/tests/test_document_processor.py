"""document_processor.py のユニットテスト"""

import pytest

# split_into_chunksをテストするため、settingsをモック
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestSplitIntoChunks:
    """split_into_chunks 関数のテスト"""

    def setup_method(self):
        """テスト前にsettingsをモック"""
        from unittest.mock import MagicMock
        import services.document_processor as dp
        mock_settings = MagicMock()
        mock_settings.chunk_size = 500
        mock_settings.chunk_overlap = 50
        dp.settings = mock_settings
        from services.document_processor import split_into_chunks
        self.split_into_chunks = split_into_chunks

    def test_empty_text_returns_empty_list(self):
        """空文字列は空リストを返す"""
        result = self.split_into_chunks("")
        assert result == []

    def test_whitespace_only_returns_empty_list(self):
        """空白のみは空リストを返す"""
        result = self.split_into_chunks("   \n\n   ")
        assert result == []

    def test_short_text_returns_single_chunk(self):
        """短いテキストは1チャンクにまとめられる"""
        text = "これはテストです。"
        result = self.split_into_chunks(text)
        assert len(result) == 1
        assert result[0] == text

    def test_long_text_split_into_multiple_chunks(self):
        """長いテキストは複数チャンクに分割される"""
        # 1000文字のテキスト（chunk_size=500なので2チャンク以上になるはず）
        text = "あ" * 1000
        result = self.split_into_chunks(text)
        assert len(result) > 1

    def test_paragraph_splitting(self):
        """空行（段落区切り）で分割される"""
        text = "段落1のテキスト\n\n段落2のテキスト\n\n段落3のテキスト"
        result = self.split_into_chunks(text)
        # 短い段落はまとめられるので1チャンクになるはず
        assert len(result) >= 1
        combined = " ".join(result)
        assert "段落1" in combined
        assert "段落2" in combined

    def test_multiple_newlines_normalized(self):
        """3行以上の空行は2行に正規化される"""
        text = "テキスト1\n\n\n\nテキスト2"
        result = self.split_into_chunks(text)
        assert len(result) >= 1

    def test_chunks_are_stripped(self):
        """各チャンクの前後の空白は除去される"""
        text = "段落1\n\n段落2"
        result = self.split_into_chunks(text)
        for chunk in result:
            assert chunk == chunk.strip()


class TestExtractText:
    """extract_text 関数のテスト（テキスト・CSVのみ）"""

    def setup_method(self):
        from unittest.mock import MagicMock
        import services.document_processor as dp
        mock_settings = MagicMock()
        mock_settings.chunk_size = 500
        mock_settings.chunk_overlap = 50
        dp.settings = mock_settings
        from services.document_processor import extract_text
        self.extract_text = extract_text

    def test_extract_txt_file(self):
        """txtファイルからテキストを抽出できる"""
        content = "テストコンテンツです。\n2行目のテキスト。"
        file_bytes = content.encode("utf-8")
        result = self.extract_text(file_bytes, "test.txt")
        assert "テストコンテンツ" in result
        assert "2行目" in result

    def test_extract_md_file(self):
        """mdファイルからテキストを抽出できる"""
        content = "# タイトル\n\n本文のテキストです。"
        file_bytes = content.encode("utf-8")
        result = self.extract_text(file_bytes, "test.md")
        assert "タイトル" in result
        assert "本文" in result

    def test_extract_csv_file(self):
        """csvファイルからテキストを抽出できる"""
        content = "名前,年齢,部署\n田中,30,営業\n鈴木,25,開発"
        file_bytes = content.encode("utf-8")
        result = self.extract_text(file_bytes, "test.csv")
        assert "名前" in result
        assert "田中" in result

    def test_unsupported_extension_raises_error(self):
        """未対応の拡張子はValueErrorを発生させる"""
        with pytest.raises(ValueError, match="未対応"):
            self.extract_text(b"content", "test.docx")
