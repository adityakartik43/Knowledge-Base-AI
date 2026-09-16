import tempfile
from pathlib import Path

from fastapi import UploadFile

from app.db.chunks import ChunkRepository
from app.embeddings.service import EmbeddingService, get_embedding_service
from app.ingestion.chunker import chunk_pages
from app.ingestion.cleaner import clean_pages
from app.ingestion.loader import extract_pdf_pages
from app.logging_config import get_logger
from app.models.schemas import ProcessDocumentResponse

logger = get_logger(__name__)


class DocumentProcessor:
    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        chunk_repository: ChunkRepository | None = None,
    ) -> None:
        self.embedding_service = embedding_service or get_embedding_service()
        self.chunk_repository = chunk_repository or ChunkRepository()

    def process_pdf_file(
        self,
        file_path: str | Path,
        document_id: str,
        document_version_id: str,
        organization_id: str,
    ) -> ProcessDocumentResponse:
        logger.info("[INGESTION] Document received document_id=%s", document_id)

        self.chunk_repository.verify_document_access(
            document_id=document_id,
            document_version_id=document_version_id,
            organization_id=organization_id,
        )

        self.chunk_repository.set_document_processing_status(
            document_id=document_id,
            processing_status="PROCESSING",
            version_status="PROCESSING",
            document_version_id=document_version_id,
        )

        try:
            pages = extract_pdf_pages(file_path)
            cleaned_pages = clean_pages(pages)
            chunks = chunk_pages(cleaned_pages)

            if not chunks:
                raise ValueError("No chunks were produced from the PDF")

            self.embedding_service.verify_dimension()

            texts = [chunk.content for chunk in chunks]
            embeddings = self.embedding_service.create_embeddings(texts)

            self.chunk_repository.delete_chunks_for_version(document_version_id)
            self.chunk_repository.insert_chunks(
                document_version_id=document_version_id,
                chunks=chunks,
                embeddings=embeddings,
                embedding_model=self.embedding_service.model_name,
                embedding_version=self.embedding_service.embedding_version,
            )

            self.chunk_repository.set_document_processing_status(
                document_id=document_id,
                processing_status="COMPLETED",
                version_status="READY",
                document_version_id=document_version_id,
            )

            logger.info("[PROCESSING] Document completed document_id=%s", document_id)

            return ProcessDocumentResponse(
                document_id=document_id,
                document_version_id=document_version_id,
                page_count=len(pages),
                chunk_count=len(chunks),
                embedding_model=self.embedding_service.model_name,
                embedding_dimension=len(embeddings[0]),
                status="completed",
            )
        except Exception as exc:
            logger.exception(
                "[PROCESSING] FAILED document_id=%s stage=processing error=%s",
                document_id,
                exc,
            )
            self.chunk_repository.set_document_processing_status(
                document_id=document_id,
                processing_status="FAILED",
                version_status="FAILED",
                document_version_id=document_version_id,
            )
            raise

    async def process_upload(
        self,
        upload: UploadFile,
        document_id: str,
        document_version_id: str,
        organization_id: str,
    ) -> ProcessDocumentResponse:
        suffix = Path(upload.filename or "document.pdf").suffix or ".pdf"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await upload.read()
            tmp.write(contents)
            tmp_path = tmp.name

        try:
            return self.process_pdf_file(
                file_path=tmp_path,
                document_id=document_id,
                document_version_id=document_version_id,
                organization_id=organization_id,
            )
        finally:
            Path(tmp_path).unlink(missing_ok=True)
