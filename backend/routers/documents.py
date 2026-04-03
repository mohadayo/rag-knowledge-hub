import logging
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings

logger = logging.getLogger(__name__)

from database import get_db
from models import Document
from schemas import DocumentResponse, DocumentStats, FileTypeCount
from services.document_processor import extract_text, split_into_chunks
from services.embedding_service import generate_embeddings
from services.vector_store import add_chunks, delete_by_document_id

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {"pdf", "csv", "txt", "md", "markdown"}


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile, db: AsyncSession = Depends(get_db)):
    """文書をアップロードし、チャンク分割・Embedding・ベクトルDB保存を行う"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="ファイル名がありません")

    # パストラバーサル防止: ファイル名からディレクトリ部分を除去
    safe_filename = os.path.basename(file.filename)
    if not safe_filename:
        raise HTTPException(status_code=400, detail="無効なファイル名です")

    ext = safe_filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"未対応のファイル形式です。対応形式: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    file_bytes = await file.read()
    file_size = len(file_bytes)

    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"ファイルサイズが上限（{settings.max_file_size // (1024 * 1024)}MB）を超えています",
        )

    # DBにメタデータ保存
    doc = Document(
        filename=safe_filename,
        file_type=ext,
        file_size=file_size,
        status="processing",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    try:
        # ファイル保存
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / f"{doc.id}_{safe_filename}"
        file_path.write_bytes(file_bytes)

        # テキスト抽出 → チャンク分割
        text = extract_text(file_bytes, safe_filename)
        chunks = split_into_chunks(text)

        if not chunks:
            raise ValueError("テキストを抽出できませんでした")

        # Embedding生成
        embeddings = generate_embeddings(chunks)

        # ベクトルDB保存
        add_chunks(doc.id, safe_filename, chunks, embeddings)

        # ステータス更新
        doc.chunk_count = len(chunks)
        doc.status = "ready"
        await db.commit()
        await db.refresh(doc)

    except Exception as e:
        logger.error("文書処理に失敗 (doc_id=%s): %s", doc.id, e, exc_info=True)
        doc.status = "error"
        await db.commit()
        raise HTTPException(status_code=500, detail=f"処理に失敗しました: {str(e)}")

    return doc


@router.get("", response_model=list[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)):
    """登録済み文書一覧を取得する"""
    result = await db.execute(
        select(Document).order_by(Document.uploaded_at.desc())
    )
    return result.scalars().all()


@router.get("/stats", response_model=DocumentStats)
async def document_stats(db: AsyncSession = Depends(get_db)):
    """文書の統計情報を取得する"""
    # 全体集計
    result = await db.execute(
        select(
            func.count(Document.id),
            func.coalesce(func.sum(Document.chunk_count), 0),
            func.coalesce(func.sum(Document.file_size), 0),
        ).where(Document.status == "ready")
    )
    row = result.one()
    total_documents, total_chunks, total_size = int(row[0]), int(row[1]), int(row[2])

    # ファイル種別ごとの件数
    type_result = await db.execute(
        select(Document.file_type, func.count(Document.id))
        .where(Document.status == "ready")
        .group_by(Document.file_type)
    )
    file_type_breakdown = [
        FileTypeCount(file_type=ft, count=cnt) for ft, cnt in type_result.all()
    ]

    return DocumentStats(
        total_documents=total_documents,
        total_chunks=total_chunks,
        total_size=total_size,
        file_type_breakdown=file_type_breakdown,
    )


@router.delete("/{document_id}")
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db)):
    """文書を削除する"""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文書が見つかりません")

    # ベクトルDBから削除
    delete_by_document_id(document_id)

    # ファイル削除
    file_path = Path(settings.upload_dir) / f"{doc.id}_{doc.filename}"
    if file_path.exists():
        os.remove(file_path)

    # DB削除
    await db.delete(doc)
    await db.commit()

    return {"message": "削除しました"}
