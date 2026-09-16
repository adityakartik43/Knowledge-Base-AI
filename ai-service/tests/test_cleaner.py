from app.ingestion.cleaner import clean_page_text


def test_clean_page_text_normalizes_whitespace() -> None:
    raw = "Hello   world\n\n\n\nTest\t\ttext"
    cleaned = clean_page_text(raw)
    assert cleaned == "Hello world\n\nTest text"


def test_clean_page_text_removes_null_bytes() -> None:
    assert clean_page_text("hello\x00world") == "hello world"
