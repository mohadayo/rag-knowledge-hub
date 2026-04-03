import logging

import chromadb

from config import settings

logger = logging.getLogger(__name__)

_client: chromadb.PersistentClient | None = None
COLLECTION_NAME = "knowledge_base"


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        logger.info("ChromaDBクライアントを初期化 (path=%s)", settings.chroma_persist_dir)
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
    logger.info("ベクトルDB保存を開始 (doc_id=%d, filename=%s, chunks=%d)", document_id, filename, len(chunks))
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
    logger.info("ベクトルDB保存完了 (doc_id=%d, チャンク数=%d)", document_id, len(chunks))


def search(query_embedding: list[float], n_results: int = 5) -> dict:
    """類似チャンクを検索する"""
    logger.info("ベクトル検索を実行 (n_results=%d)", n_results)
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
    hit_count = len(results.get("documents", [[]])[0])
    logger.info("ベクトル検索完了 (ヒット数=%d)", hit_count)
    return results


def delete_by_document_id(document_id: int):
    """指定ドキュメントのチャンクをすべて削除する"""
    logger.info("ベクトルDB削除を開始 (doc_id=%d)", document_id)
    collection = get_collection()
    # ChromaDBではwhere句でフィルタして取得→削除
    results = collection.get(
        where={"document_id": document_id},
        include=[],
    )
    if results["ids"]:
        collection.delete(ids=results["ids"])
        logger.info("ベクトルDB削除完了 (doc_id=%d, 削除数=%d)", document_id, len(results["ids"]))
    else:
        logger.info("ベクトルDB削除: 対象チャンクなし (doc_id=%d)", document_id)
