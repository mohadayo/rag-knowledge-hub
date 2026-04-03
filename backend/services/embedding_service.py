import logging

from openai import OpenAI, OpenAIError

from config import settings

logger = logging.getLogger(__name__)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """テキストリストからEmbeddingを生成する"""
    logger.info("Embedding生成を開始 (テキスト数=%d, モデル=%s)", len(texts), settings.openai_embedding_model)
    client = _get_client()
    try:
        response = client.embeddings.create(
            model=settings.openai_embedding_model,
            input=texts,
        )
    except OpenAIError as e:
        logger.error("OpenAI Embedding APIの呼び出しに失敗: %s", e)
        raise
    logger.info("Embedding生成完了 (件数=%d)", len(response.data))
    return [item.embedding for item in response.data]


def generate_embedding(text: str) -> list[float]:
    """単一テキストからEmbeddingを生成する"""
    return generate_embeddings([text])[0]
