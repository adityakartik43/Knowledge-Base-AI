from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pypdf.errors import PdfReadError

from app.ingestion.loader import extract_pdf_pages


def test_extract_pdf_pages_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        extract_pdf_pages(tmp_path / "missing.pdf")


def test_extract_pdf_pages_rejects_non_pdf(tmp_path: Path) -> None:
    file_path = tmp_path / "notes.txt"
    file_path.write_text("not a pdf", encoding="utf-8")

    with pytest.raises(ValueError, match="Expected a PDF file"):
        extract_pdf_pages(file_path)


def test_extract_pdf_pages_rejects_corrupted_pdf(tmp_path: Path) -> None:
    file_path = tmp_path / "broken.pdf"
    file_path.write_bytes(b"not-a-real-pdf")

    with patch("app.ingestion.loader.PdfReader", side_effect=PdfReadError("bad pdf")):
        with pytest.raises(ValueError, match="Invalid or corrupted PDF"):
            extract_pdf_pages(file_path)


def test_extract_pdf_pages_extracts_text(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.pdf"
    file_path.write_bytes(b"%PDF-1.4")

    page_one = MagicMock()
    page_one.extract_text.return_value = "Page one content"
    page_two = MagicMock()
    page_two.extract_text.return_value = "Page two content"

    reader = MagicMock()
    reader.is_encrypted = False
    reader.pages = [page_one, page_two]

    with patch("app.ingestion.loader.PdfReader", return_value=reader):
        pages = extract_pdf_pages(file_path)

    assert len(pages) == 2
    assert pages[0].page_number == 1
    assert pages[0].text == "Page one content"
    assert pages[1].page_number == 2
    assert pages[1].text == "Page two content"
