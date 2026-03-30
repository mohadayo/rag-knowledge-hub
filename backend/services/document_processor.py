import csv
import io
import re

import chardet
import PyPDF2

from config import settings


def extract_text(file_bytes: bytes, filename: str) -> str:
    """ファイルからテキストを抽出する"""
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext == "pdf":
        return _extract_pdf(file_bytes)
    elif ext == "csv":
        return _extract_csv(file_bytes)
    elif ext in ("txt", "md", "markdown"):
        return _extract_text(file_bytes)
    else:
        raise ValueError(f"未対応のファイル形式です: {ext}")


def _extract_pdf(file_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    texts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            texts.append(text)
    return "\n".join(texts)


def _extract_csv(file_bytes: bytes) -> str:
    encoding = chardet.detect(file_bytes)["encoding"] or "utf-8"
    text = file_bytes.decode(encoding)
    reader = csv.reader(io.StringIO(text))
    rows = []
    for row in reader:
        rows.append(" | ".join(row))
    return "\n".join(rows)


def _extract_text(file_bytes: bytes) -> str:
    encoding = chardet.detect(file_bytes)["encoding"] or "utf-8"
    return file_bytes.decode(encoding)


def split_into_chunks(text: str) -> list[str]:
    """テキストをチャンクに分割する"""
    # 空行・改行の正規化
    text = re.sub(r"\n{3,}", "\n\n", text.strip())

    chunk_size = settings.chunk_size
    overlap = settings.chunk_overlap

    # まず段落単位で分割
    paragraphs = text.split("\n\n")

    chunks: list[str] = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) + 1 <= chunk_size:
            current_chunk = f"{current_chunk}\n{para}" if current_chunk else para
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # 段落自体がchunk_sizeを超える場合は文字数で分割
            if len(para) > chunk_size:
                for i in range(0, len(para), chunk_size - overlap):
                    chunks.append(para[i : i + chunk_size].strip())
                current_chunk = ""
            else:
                current_chunk = para

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks
