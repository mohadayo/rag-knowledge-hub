from fastapi import APIRouter

from schemas import ChatRequest, ChatResponse
from services.rag_service import ask

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
    return ask(request.question)
