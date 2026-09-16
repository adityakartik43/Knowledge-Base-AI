import re

from app.config import get_settings
from app.db.connection import get_connection, get_raw_connection
from app.logging_config import get_logger

logger = get_logger(__name__)

_VECTOR_DIMENSION_PATTERN = re.compile(r"vector\((\d+)\)")


def _parse_vector_dimension(column_type: str) -> int | None:
    match = _VECTOR_DIMENSION_PATTERN.search(column_type)
    if match is None:
        return None
    return int(match.group(1))


def ensure_pgvector_setup() -> None:
    """Ensure pgvector extension and embedding column exist."""
    settings = get_settings()

    with get_raw_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT format_type(a.atttypid, a.atttypmod) AS column_type
                FROM pg_attribute a
                JOIN pg_class c ON a.attrelid = c.oid
                WHERE c.relname = 'document_chunks'
                  AND a.attname = 'embedding'
                  AND NOT a.attisdropped
                """
            )
            row = cur.fetchone()

            if row is None:
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
            else:
                existing_dimension = _parse_vector_dimension(row[0])
                if existing_dimension is None:
                    raise RuntimeError(
                        "document_chunks.embedding exists but its vector dimension "
                        "could not be determined"
                    )
                if existing_dimension != settings.embedding_dimension:
                    raise RuntimeError(
                        f"document_chunks.embedding is vector({existing_dimension}) but "
                        f"EMBEDDING_DIMENSION={settings.embedding_dimension}. "
                        "Run an explicit schema migration before changing the dimension."
                    )

            cur.execute("SAVEPOINT document_chunks_embedding_idx")
            try:
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx
                    ON document_chunks
                    USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100)
                    """
                )
                cur.execute("RELEASE SAVEPOINT document_chunks_embedding_idx")
            except Exception as exc:
                cur.execute("ROLLBACK TO SAVEPOINT document_chunks_embedding_idx")
                logger.warning(
                    "[DATABASE] Could not create ivfflat index yet: %s", exc
                )

        conn.commit()
