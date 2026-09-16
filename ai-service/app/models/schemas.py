from typing import Any, Optional

from pydantic import BaseModel, Field


class PageText(BaseModel):
    page_number: int
    text: str


class TextChunk(BaseModel):
    chunk_index: int
    content: str
    page_number: Optional[int] = None
    token_count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProcessDocumentRequest(BaseModel):
    document_id: str
    document_version_id: str
    organization_id: str
    file_path: Optional[str] = None


class ProcessDocumentResponse(BaseModel):
    document_id: str
    document_version_id: str
    page_count: int
    chunk_count: int
    embedding_model: str
    embedding_dimension: int
    status: str = "completed"


class EmbedRequest(BaseModel):
    texts: list[str] = Field(min_length=1)


class EmbedResponse(BaseModel):
    embeddings: list[list[float]]
    model: str
    dimensions: int


class RetrieveRequest(BaseModel):
    organization_id: str
    query: str = Field(min_length=1)
    document_ids: list[str] = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)


class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    document_version_id: str
    chunk_index: int
    content: str
    page_number: Optional[int] = None
    relevance_score: float


class RetrieveResponse(BaseModel):
    chunks: list[RetrievedChunk]
    model: str
    dimensions: int


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    organization_id: str
    query: str = Field(min_length=1)
    document_ids: list[str] = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    conversation_history: list[ChatMessage] = Field(default_factory=list)


class Citation(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    relevance_score: float
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    model: str
