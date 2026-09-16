from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.auth import verify_service_api_key
from app.config import get_settings
from app.db.setup import ensure_pgvector_setup
from app.embeddings.service import get_embedding_service
from app.logging_config import get_logger, setup_logging
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    EmbedRequest,
    EmbedResponse,
    ProcessDocumentResponse,
    RetrieveRequest,
    RetrieveResponse,
)
from app.rag.pipeline import RagPipeline
from app.retrieval.search import RetrievalService
from app.services.document_processor import DocumentProcessor

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    ensure_pgvector_setup()
    embedding_service = get_embedding_service()
    embedding_service.verify_dimension()
    logger.info("[STARTUP] AI service ready")
    yield


app = FastAPI(
    title="KnowBase AI Service",
    description="Internal Python service for PDF ingestion, embeddings, retrieval, and RAG.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/process-document",
    response_model=ProcessDocumentResponse,
    dependencies=[Depends(verify_service_api_key)],
)
async def process_document(
    document_id: str = Form(...),
    document_version_id: str = Form(...),
    organization_id: str = Form(...),
    file: UploadFile = File(...),
) -> ProcessDocumentResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported in V1")

    processor = DocumentProcessor()

    try:
        return await processor.process_upload(
            upload=file,
            document_id=document_id,
            document_version_id=document_version_id,
            organization_id=organization_id,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Document processing failed") from exc


@app.post(
    "/embed",
    response_model=EmbedResponse,
    dependencies=[Depends(verify_service_api_key)],
)
def embed_texts(payload: EmbedRequest) -> EmbedResponse:
    service = get_embedding_service()

    try:
        embeddings = service.create_embeddings(payload.texts)
        dimension = service.verify_dimension()

        return EmbedResponse(
            embeddings=embeddings,
            model=service.model_name,
            dimensions=dimension,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Embedding generation failed") from exc


@app.post(
    "/retrieve",
    response_model=RetrieveResponse,
    dependencies=[Depends(verify_service_api_key)],
)
def retrieve_chunks(payload: RetrieveRequest) -> RetrieveResponse:
    service = RetrievalService()
    embedding_service = get_embedding_service()

    try:
        chunks = service.retrieve(
            organization_id=payload.organization_id,
            query=payload.query,
            document_ids=payload.document_ids,
            top_k=payload.top_k,
        )

        return RetrieveResponse(
            chunks=chunks,
            model=embedding_service.model_name,
            dimensions=embedding_service.verify_dimension(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Retrieval failed") from exc


@app.post(
    "/chat",
    response_model=ChatResponse,
    dependencies=[Depends(verify_service_api_key)],
)
def chat(payload: ChatRequest) -> ChatResponse:
    pipeline = RagPipeline()

    try:
        return pipeline.chat(
            organization_id=payload.organization_id,
            query=payload.query,
            document_ids=payload.document_ids,
            top_k=payload.top_k,
            conversation_history=payload.conversation_history,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Chat generation failed") from exc


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


def run() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    run()
