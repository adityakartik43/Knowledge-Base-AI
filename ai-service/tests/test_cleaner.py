from app.ingestion.cleaner import clean_page_text, clean_pages
from app.models.schemas import PageText


def test_clean_page_text_normalizes_whitespace() -> None:
    raw = "Hello   world\n\n\n\nTest\t\ttext"
    cleaned = clean_page_text(raw)
    assert cleaned == "Hello world\n\nTest text"


def test_clean_page_text_removes_null_bytes() -> None:
    assert clean_page_text("hello\x00world") == "hello world"


def test_clean_pages_drops_empty_pages() -> None:
    pages = [
        PageText(page_number=1, text="   "),
        PageText(page_number=2, text="Useful content"),
    ]

    cleaned = clean_pages(pages)

    assert len(cleaned) == 1
    assert cleaned[0].page_number == 2
    assert cleaned[0].text == "Useful content"
