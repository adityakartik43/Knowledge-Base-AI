from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "0.0.0.0"
    port: int = 8001

    database_url: str

    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"

    embedding_dimension: int = 1536
    embedding_version: str = "v1"

    chunk_size_tokens: int = 700
    chunk_overlap_tokens: int = 75

    default_top_k: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
