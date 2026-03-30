import logging

from fastapi import APIRouter, HTTPException

from schemas import ChatRequest, ChatResponse
from services.rag_service import ask

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """質問に対してRAGで回答する"""
    if not request.question.strip():
        return ChatResponse(
            answer="質問を入力してください。",
            sources=[],
            confidence="unknown",
        )
    try:
        return ask(request.question)
    except Exception as e:
        logger.error("チャット処理中にエラーが発生: %s", e, exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="回答の生成に失敗しました。しばらくしてから再度お試しください。",
        )
