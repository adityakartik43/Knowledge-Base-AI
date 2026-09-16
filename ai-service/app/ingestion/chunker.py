from typing import Optional

import tiktoken

from app.config import get_settings
from app.logging_config import get_logger
from app.models.schemas import PageText, TextChunk

logger = get_logger(__name__)

ENCODING_NAME = "cl100k_base"


def _get_encoding() -> tiktoken.Encoding:
    return tiktoken.get_encoding(ENCODING_NAME)


def count_tokens(text: str) -> int:
    return len(_get_encoding().encode(text))


def _split_text_by_tokens(
    text: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:
    encoding = _get_encoding()
    tokens = encoding.encode(text)

    if not tokens:
        return []

    if len(tokens) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(encoding.decode(chunk_tokens))

        if end >= len(tokens):
            break

        start = max(end - overlap, start + 1)

    return chunks


def chunk_pages(pages: list[PageText]) -> list[TextChunk]:
    """
    Page-aware, token-based chunking with overlap.

    Each chunk retains the page number of its source page.
    """
    settings = get_settings()
    chunk_size = settings.chunk_size_tokens
    overlap = settings.chunk_overlap_tokens

    chunks: list[TextChunk] = []
    chunk_index = 0

    for page in pages:
        page_text = page.text.strip()
        if not page_text:
            continue

        page_chunks = _split_text_by_tokens(page_text, chunk_size, overlap)

        for part in page_chunks:
            token_count = count_tokens(part)
            chunks.append(
                TextChunk(
                    chunk_index=chunk_index,
                    content=part,
                    page_number=page.page_number,
                    token_count=token_count,
                    metadata={"source_page": page.page_number},
                )
            )
            chunk_index += 1

    logger.info("[CHUNKING] Created %s chunks", len(chunks))
    return chunks
