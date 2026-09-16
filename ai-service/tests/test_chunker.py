from app.ingestion.chunker import chunk_pages, count_tokens
from app.models.schemas import PageText


def test_count_tokens() -> None:
    assert count_tokens("hello world") > 0


def test_chunk_pages_preserves_page_numbers() -> None:
    pages = [
        PageText(page_number=1, text="Introduction to the employee handbook."),
        PageText(
            page_number=2,
            text=(
                "Employees receive 24 paid leaves every year. "
                "Leave requests must be submitted through the HR portal."
            ),
        ),
    ]

    chunks = chunk_pages(pages)

    assert len(chunks) >= 2
    assert chunks[0].page_number == 1
    assert all(chunk.token_count > 0 for chunk in chunks)
    assert chunks[0].chunk_index == 0


def test_chunk_pages_empty_input() -> None:
    assert chunk_pages([]) == []
