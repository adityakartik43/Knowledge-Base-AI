from functools import lru_cache

from openai import OpenAI

from app.config import Settings, get_settings
from app.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self._verified_dimension: int | None = None

    def verify_dimension(self) -> int:
        if self._verified_dimension is not None:
            return self._verified_dimension

        probe = self.create_embeddings(["dimension probe"])[0]
        actual = len(probe)

        if actual != self.settings.embedding_dimension:
            raise ValueError(
                f"Configured EMBEDDING_DIMENSION={self.settings.embedding_dimension} "
                f"but model returned dimension {actual}. "
                "Update EMBEDDING_DIMENSION to match the model output."
            )

        self._verified_dimension = actual
        logger.info("[EMBEDDING] Verified embedding dimension: %s", actual)
        return actual

    def create_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        response = self.client.embeddings.create(
            model=self.settings.openai_embedding_model,
            input=texts,
        )

        embeddings = [item.embedding for item in response.data]
        logger.info("[EMBEDDING] Generated %s embeddings", len(embeddings))
        return embeddings

    def create_embedding(self, text: str) -> list[float]:
        return self.create_embeddings([text])[0]

    @property
    def model_name(self) -> str:
        return self.settings.openai_embedding_model

    @property
    def embedding_version(self) -> str:
        return self.settings.embedding_version


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
