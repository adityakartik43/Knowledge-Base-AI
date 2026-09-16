from app.config import get_settings
from app.db.connection import get_connection
from app.logging_config import get_logger

logger = get_logger(__name__)


def ensure_pgvector_setup() -> None:
    """Ensure pgvector extension and embedding column exist."""
    settings = get_settings()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

            cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'document_chunks'
                  AND column_name = 'embedding'
                """
            )
            if cur.fetchone() is None:
                cur.execute(
                    f"""
                    ALTER TABLE document_chunks
                    ADD COLUMN embedding vector({settings.embedding_dimension})
                    """
                )
                logger.info(
                    "[DATABASE] Added embedding vector(%s) column to document_chunks",
                    settings.embedding_dimension,
                )

            try:
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx
                    ON document_chunks
                    USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100)
                    """
                )
            except Exception as exc:
                logger.warning(
                    "[DATABASE] Could not create ivfflat index yet: %s", exc
                )

        conn.commit()
