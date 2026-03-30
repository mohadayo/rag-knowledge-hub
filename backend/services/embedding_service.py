from openai import OpenAI

from config import settings

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """テキストリストからEmbeddingを生成する"""
    client = _get_client()
    response = client.embeddings.create(
        model=settings.openai_embedding_model,
        input=texts,
    )
    return [item.embedding for item in response.data]


def generate_embedding(text: str) -> list[float]:
    """単一テキストからEmbeddingを生成する"""
    return generate_embeddings([text])[0]
