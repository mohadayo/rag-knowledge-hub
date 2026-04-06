import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from database import init_db, async_session
from routers import chat, documents

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("アプリケーションを起動中...")
    await init_db()
    logger.info("データベース初期化完了")
    yield
    logger.info("アプリケーションをシャットダウン中...")


app = FastAPI(
    title="RAG Knowledge Hub API",
    description="社内ナレッジ検索AI バックエンドAPI",
    version="0.1.0",
    lifespan=lifespan,
)

# CORSオリジンを環境変数で設定可能（デフォルト: localhost:3000）
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000
        logger.info(
            "%s %s %d %.1fms",
            request.method, request.url.path, response.status_code, duration_ms,
        )
        return response


app.add_middleware(RequestLoggingMiddleware)

app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/api/health")
async def health():
    """ヘルスチェック（DB・ベクトルDB接続確認付き）"""
    status = {"status": "ok", "db": "unknown", "vector_db": "unknown"}

    # DB接続確認
    try:
        async with async_session() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
        status["db"] = "connected"
    except Exception:
        logger.exception("DB接続エラー")
        status["db"] = "disconnected"
        status["status"] = "degraded"

    # ベクトルDB接続確認
    try:
        from services.vector_store import get_collection
        collection = get_collection()
        doc_count = collection.count()
        status["vector_db"] = "connected"
        status["chunk_count"] = doc_count
    except Exception:
        logger.exception("ベクトルDB接続エラー")
        status["vector_db"] = "disconnected"
        status["status"] = "degraded"

    return status
