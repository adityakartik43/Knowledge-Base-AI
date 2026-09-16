from app.config import get_settings
from app.db.chunks import ChunkRepository
from app.embeddings.service import EmbeddingService, get_embedding_service
from app.logging_config import get_logger
from app.models.schemas import RetrievedChunk

logger = get_logger(__name__)


class RetrievalService:
    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        chunk_repository: ChunkRepository | None = None,
    ) -> None:
        self.embedding_service = embedding_service or get_embedding_service()
        self.chunk_repository = chunk_repository or ChunkRepository()
        self.settings = get_settings()

    def retrieve(
        self,
        organization_id: str,
        query: str,
        document_ids: list[str],
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        if not document_ids:
            raise ValueError("document_ids must not be empty")

        limit = top_k or self.settings.default_top_k

        logger.info(
            "[RETRIEVAL] Searching org=%s documents=%s top_k=%s",
            organization_id,
            len(document_ids),
            limit,
        )

        query_embedding = self.embedding_service.create_embedding(query)

        return self.chunk_repository.search_similar(
            organization_id=organization_id,
            document_ids=document_ids,
            query_embedding=query_embedding,
            top_k=limit,
            embedding_model=self.embedding_service.model_name,
            embedding_version=self.embedding_service.embedding_version,
        )
