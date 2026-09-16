from pathlib import Path

import pytest
from pypdf import PdfWriter

from app.ingestion.loader import extract_pdf_pages


def _create_sample_pdf(path: Path, pages: list[str]) -> None:
    writer = PdfWriter()
    for text in pages:
        writer.add_blank_page(width=612, height=792)
    with path.open("wb") as file:
        writer.write(file)


def test_extract_pdf_pages_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        extract_pdf_pages(tmp_path / "missing.pdf")


def test_extract_pdf_pages_rejects_non_pdf(tmp_path: Path) -> None:
    file_path = tmp_path / "notes.txt"
    file_path.write_text("not a pdf", encoding="utf-8")

    with pytest.raises(ValueError, match="Expected a PDF file"):
        extract_pdf_pages(file_path)
