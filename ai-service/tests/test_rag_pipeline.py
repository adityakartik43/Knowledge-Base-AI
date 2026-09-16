from app.models.schemas import RetrievedChunk
from app.rag.pipeline import RagPipeline


def test_build_context_formats_sources() -> None:
    pipeline = RagPipeline(retrieval_service=None)
    chunks = [
        RetrievedChunk(
            chunk_id="chunk-1",
            document_id="doc-1",
            document_name="Employee Handbook",
            document_version_id="version-1",
            chunk_index=0,
            content="Employees receive 24 paid leaves every year.",
            page_number=14,
            relevance_score=0.92,
        )
    ]

    context = pipeline.build_context(chunks)

    assert "SOURCE 1" in context
    assert "Employee Handbook" in context
    assert "Page: 14" in context
    assert "24 paid leaves" in context


def test_build_context_handles_empty_chunks() -> None:
    pipeline = RagPipeline(retrieval_service=None)
    assert "No relevant source context" in pipeline.build_context([])
