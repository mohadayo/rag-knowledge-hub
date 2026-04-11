import logging

import httpx
from openai import OpenAI

from config import settings

logger = logging.getLogger(__name__)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=httpx.Timeout(
                settings.openai_timeout,
                connect=settings.openai_connect_timeout,
            ),
        )
    return _client


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """テキストリストからEmbeddingを生成する"""
    client = _get_client()
    logger.info("Embedding生成開始: %d件のテキスト, model=%s", len(texts), settings.openai_embedding_model)
    response = client.embeddings.create(
        model=settings.openai_embedding_model,
        input=texts,
    )
    logger.info(
        "Embedding生成完了: %d件, usage=%d tokens",
        len(response.data), response.usage.total_tokens,
    )
    return [item.embedding for item in response.data]


def generate_embedding(text: str) -> list[float]:
    """単一テキストからEmbeddingを生成する"""
    return generate_embeddings([text])[0]
