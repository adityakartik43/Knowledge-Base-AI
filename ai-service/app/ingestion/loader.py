from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.logging_config import get_logger
from app.models.schemas import PageText

logger = get_logger(__name__)


def extract_pdf_pages(file_path: str | Path) -> list[PageText]:
    """Extract page-aware text from a PDF file."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {path.suffix}")

    try:
        reader = PdfReader(str(path))
    except PdfReadError as exc:
        raise ValueError(f"Invalid or corrupted PDF: {exc}") from exc

    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not supported in V1")

    pages: list[PageText] = []

    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(PageText(page_number=index, text=text))

    if not any(page.text.strip() for page in pages):
        raise ValueError("PDF contains no extractable text")

    logger.info("[EXTRACTION] Extracted %s pages", len(pages))
    return pages
