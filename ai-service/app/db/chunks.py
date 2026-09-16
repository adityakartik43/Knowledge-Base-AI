import json
import uuid
from typing import Optional

from app.config import get_settings
from app.db.connection import get_connection
from app.logging_config import get_logger
from app.models.schemas import RetrievedChunk, TextChunk

logger = get_logger(__name__)


class ChunkRepository:
    def verify_document_access(
        self,
        document_id: str,
        document_version_id: str,
        organization_id: str,
    ) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT d.id
                    FROM documents d
                    JOIN document_versions dv ON dv."documentId" = d.id
                    WHERE d.id = %s::uuid
                      AND dv.id = %s::uuid
                      AND d."organizationId" = %s::uuid
                    """,
                    (document_id, document_version_id, organization_id),
                )
                if cur.fetchone() is None:
                    raise ValueError(
                        "Document/version does not belong to the specified organization"
                    )

    def set_document_processing_status(
        self,
        document_id: str,
        processing_status: str,
        version_status: Optional[str] = None,
        document_version_id: Optional[str] = None,
    ) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE documents
                    SET "processingStatus" = %s::"DocumentProcessingStatus",
                        "updatedAt" = NOW()
                    WHERE id = %s::uuid
                    """,
                    (processing_status, document_id),
                )
                if version_status and document_version_id:
                    cur.execute(
                        """
                        UPDATE document_versions
                        SET status = %s::"DocumentVersionStatus",
                            "updatedAt" = NOW()
                        WHERE id = %s::uuid
                        """,
                        (version_status, document_version_id),
                    )
            conn.commit()

    def replace_chunks_for_version(
        self,
        document_version_id: str,
        chunks: list[TextChunk],
        embeddings: list[list[float]],
        embedding_model: str,
        embedding_version: str,
    ) -> int:
        settings = get_settings()

        if len(chunks) != len(embeddings):
            raise ValueError("Chunk and embedding counts must match")

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1
                    FROM message_citations mc
                    JOIN document_chunks dc ON dc.id = mc."documentChunkId"
                    WHERE dc."documentVersionId" = %s::uuid
                    LIMIT 1
                    """,
                    (document_version_id,),
                )
                if cur.fetchone() is not None:
                    raise ValueError(
                        "Cannot reprocess a document version that has chat citations. "
                        "Upload a new version instead."
                    )

                cur.execute(
                    """
                    DELETE FROM document_chunks
                    WHERE "documentVersionId" = %s::uuid
                    """,
                    (document_version_id,),
                )

                for chunk, embedding in zip(chunks, embeddings):
                    if len(embedding) != settings.embedding_dimension:
                        raise ValueError(
                            f"Embedding dimension {len(embedding)} does not match "
                            f"configured dimension {settings.embedding_dimension}"
                        )

                    cur.execute(
                        """
                        INSERT INTO document_chunks (
                            id,
                            "documentVersionId",
                            "chunkIndex",
                            content,
                            "pageNumber",
                            "tokenCount",
                            metadata,
                            embedding,
                            "embeddingModel",
                            "embeddingVersion",
                            "createdAt"
                        ) VALUES (
                            %s::uuid,
                            %s::uuid,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s::jsonb,
                            %s,
                            %s,
                            %s,
                            NOW()
                        )
                        """,
                        (
                            str(uuid.uuid4()),
                            document_version_id,
                            chunk.chunk_index,
                            chunk.content,
                            chunk.page_number,
                            chunk.token_count,
                            json.dumps(chunk.metadata),
                            embedding,
                            embedding_model,
                            embedding_version,
                        ),
                    )

            conn.commit()

        logger.info("[DATABASE] Stored %s chunks", len(chunks))
        return len(chunks)

    def search_similar(
        self,
        organization_id: str,
        document_ids: list[str],
        query_embedding: list[float],
        top_k: int,
        embedding_model: str,
        embedding_version: str,
    ) -> list[RetrievedChunk]:
        settings = get_settings()

        if len(query_embedding) != settings.embedding_dimension:
            raise ValueError(
                f"Query embedding dimension {len(query_embedding)} does not match "
                f"configured dimension {settings.embedding_dimension}"
            )

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        dc.id,
                        d.id,
                        d.name,
                        dc."documentVersionId",
                        dc."chunkIndex",
                        dc.content,
                        dc."pageNumber",
                        1 - (dc.embedding <=> %s::vector) AS relevance_score
                    FROM document_chunks dc
                    JOIN document_versions dv
                        ON dc."documentVersionId" = dv.id
                    JOIN documents d
                        ON dv."documentId" = d.id
                    WHERE d."organizationId" = %s::uuid
                      AND d.id = ANY(%s::uuid[])
                      AND dv.id = d."currentVersionId"
                      AND dv.status = 'READY'
                      AND dc.embedding IS NOT NULL
                      AND dc."embeddingModel" = %s
                      AND dc."embeddingVersion" = %s
                    ORDER BY dc.embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (
                        query_embedding,
                        organization_id,
                        document_ids,
                        embedding_model,
                        embedding_version,
                        query_embedding,
                        top_k,
                    ),
                )
                rows = cur.fetchall()

        return [
            RetrievedChunk(
                chunk_id=str(row[0]),
                document_id=str(row[1]),
                document_name=row[2],
                document_version_id=str(row[3]),
                chunk_index=row[4],
                content=row[5],
                page_number=row[6],
                relevance_score=float(row[7]),
            )
            for row in rows
        ]

    def get_document_names(self, document_ids: list[str]) -> dict[str, str]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name
                    FROM documents
                    WHERE id = ANY(%s::uuid[])
                    """,
                    (document_ids,),
                )
                rows = cur.fetchall()

        return {str(row[0]): row[1] for row in rows}
