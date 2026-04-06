from datetime import datetime

from pydantic import BaseModel, field_validator


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

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("質問を入力してください")
        if len(v) > 10000:
            raise ValueError("質問は10000文字以内で入力してください")
        return v.strip()


class SourceInfo(BaseModel):
    filename: str
    excerpt: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]
    confidence: str  # "high" | "medium" | "low" | "unknown"


class FileTypeCount(BaseModel):
    file_type: str
    count: int


class DocumentStats(BaseModel):
    total_documents: int
    total_chunks: int
    total_size: int
    file_type_breakdown: list[FileTypeCount]
