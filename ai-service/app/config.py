from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

GEMINI_OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "0.0.0.0"
    port: int = 8001

    database_url: str

    service_api_key: str

    gemini_api_key: str
    gemini_base_url: str = GEMINI_OPENAI_BASE_URL
    gemini_embedding_model: str = "gemini-embedding-001"
    gemini_chat_model: str = "gemini-2.5-flash"

    embedding_dimension: int = 1536
    embedding_version: str = "v1"
    embedding_batch_size: int = 100

    chunk_size_tokens: int = 700
    chunk_overlap_tokens: int = 75

    default_top_k: int = 5
    max_upload_bytes: int = 50 * 1024 * 1024

    @model_validator(mode="after")
    def validate_chunk_settings(self) -> "Settings":
        if self.chunk_size_tokens <= 0:
            raise ValueError("CHUNK_SIZE_TOKENS must be greater than 0")
        if self.chunk_overlap_tokens < 0:
            raise ValueError("CHUNK_OVERLAP_TOKENS must be non-negative")
        if self.chunk_overlap_tokens >= self.chunk_size_tokens:
            raise ValueError(
                "CHUNK_OVERLAP_TOKENS must be less than CHUNK_SIZE_TOKENS"
            )
        if self.embedding_batch_size <= 0:
            raise ValueError("EMBEDDING_BATCH_SIZE must be greater than 0")
        if self.max_upload_bytes <= 0:
            raise ValueError("MAX_UPLOAD_BYTES must be greater than 0")
        if self.embedding_dimension <= 0:
            raise ValueError("EMBEDDING_DIMENSION must be greater than 0")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
