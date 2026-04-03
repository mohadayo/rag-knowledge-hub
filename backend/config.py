from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 1024
    chroma_persist_dir: str = "./chroma_data"
    database_url: str = "sqlite+aiosqlite:///./knowledge.db"
    upload_dir: str = "./uploads"
    chunk_size: int = 500
    chunk_overlap: int = 50
    max_retrieval_results: int = 5
    similarity_threshold: float = 0.3
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env"}

    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_api_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("openai_api_key は必須です。環境変数または .env ファイルで設定してください。")
        return v


settings = Settings()
