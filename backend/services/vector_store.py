import chromadb

from config import settings

_client: chromadb.PersistentClient | None = None
COLLECTION_NAME = "knowledge_base"


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return _client


def get_collection() -> chromadb.Collection:
    client = _get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(
    document_id: int,
    filename: str,
    chunks: list[str],
    embeddings: list[list[float]],
):
    """チャンクをベクトルDBに保存する"""
    collection = get_collection()
    ids = [f"doc{document_id}_chunk{i}" for i in range(len(chunks))]
    metadatas = [
        {"document_id": document_id, "filename": filename, "chunk_index": i}
        for i in range(len(chunks))
    ]
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def search(query_embedding: list[float], n_results: int = 5) -> dict:
    """類似チャンクを検索する"""
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
    return results


def delete_by_document_id(document_id: int):
    """指定ドキュメントのチャンクをすべて削除する"""
    collection = get_collection()
    # ChromaDBではwhere句でフィルタして取得→削除
    results = collection.get(
        where={"document_id": document_id},
        include=[],
    )
    if results["ids"]:
        collection.delete(ids=results["ids"])
