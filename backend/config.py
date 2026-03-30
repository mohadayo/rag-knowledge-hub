from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    chroma_persist_dir: str = "./chroma_data"
    database_url: str = "sqlite+aiosqlite:///./knowledge.db"
    upload_dir: str = "./uploads"
    chunk_size: int = 500
    chunk_overlap: int = 50
    max_retrieval_results: int = 5
    similarity_threshold: float = 0.3

    model_config = {"env_file": ".env"}


settings = Settings()
