import math
from functools import lru_cache

from openai import OpenAI

from app.config import Settings, get_settings
from app.logging_config import get_logger

logger = get_logger(__name__)


def _normalize_embedding(embedding: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(value * value for value in embedding))
    if magnitude == 0:
        return embedding
    return [value / magnitude for value in embedding]


class EmbeddingService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.client = OpenAI(
            api_key=self.settings.gemini_api_key,
            base_url=self.settings.gemini_base_url,
        )
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

    def _post_process_embedding(self, embedding: list[float]) -> list[float]:
        if len(embedding) != self.settings.embedding_dimension:
            raise ValueError(
                f"Embedding dimension {len(embedding)} does not match "
                f"configured dimension {self.settings.embedding_dimension}"
            )

        if self.settings.embedding_dimension < 3072:
            return _normalize_embedding(embedding)

        return embedding

    def create_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        batch_size = self.settings.embedding_batch_size
        embeddings: list[list[float]] = []

        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            response = self.client.embeddings.create(
                model=self.settings.gemini_embedding_model,
                input=batch,
                dimensions=self.settings.embedding_dimension,
            )

            batch_embeddings = [item.embedding for item in response.data]
            if len(batch_embeddings) != len(batch):
                raise ValueError(
                    "Embedding provider returned a different number of vectors "
                    "than requested"
                )

            embeddings.extend(
                self._post_process_embedding(embedding)
                for embedding in batch_embeddings
            )

        logger.info("[EMBEDDING] Generated %s embeddings", len(embeddings))
        return embeddings

    def create_embedding(self, text: str) -> list[float]:
        return self.create_embeddings([text])[0]

    @property
    def model_name(self) -> str:
        return self.settings.gemini_embedding_model

    @property
    def embedding_version(self) -> str:
        return self.settings.embedding_version


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
