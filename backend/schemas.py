from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    status: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    question: str


class SourceInfo(BaseModel):
    filename: str
    excerpt: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]
    confidence: str  # "high" | "medium" | "low" | "unknown"
