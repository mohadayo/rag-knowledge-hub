from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    chroma_persist_dir: str = "./chroma_data"
    database_url: str = "sqlite+aiosqlite:///./knowledge.db"
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    chunk_size: int = 500
    chunk_overlap: int = 50
    max_retrieval_results: int = 5
    similarity_threshold: float = 0.3
    openai_timeout: float = 30.0
    openai_connect_timeout: float = 10.0

    model_config = {"env_file": ".env"}


settings = Settings()
