import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_rejects_invalid_chunk_overlap() -> None:
    with pytest.raises(ValidationError, match="CHUNK_OVERLAP_TOKENS"):
        Settings(
            database_url="postgresql://localhost/test",
            service_api_key="secret",
            gemini_api_key="test-key",
            chunk_size_tokens=100,
            chunk_overlap_tokens=100,
        )


def test_settings_rejects_non_positive_chunk_size() -> None:
    with pytest.raises(ValidationError, match="CHUNK_SIZE_TOKENS"):
        Settings(
            database_url="postgresql://localhost/test",
            service_api_key="secret",
            gemini_api_key="test-key",
            chunk_size_tokens=0,
        )


def test_settings_default_gemini_models() -> None:
    settings = Settings(
        database_url="postgresql://localhost/test",
        service_api_key="secret",
        gemini_api_key="test-key",
    )

    assert settings.gemini_embedding_model == "gemini-embedding-001"
    assert settings.gemini_chat_model == "gemini-2.5-flash"
    assert settings.embedding_dimension == 1536
