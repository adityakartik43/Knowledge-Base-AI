import re

from app.models.schemas import PageText


def clean_page_text(text: str) -> str:
    """Normalize whitespace and remove common PDF extraction artifacts."""
    if not text:
        return ""

    cleaned = text.replace("\x00", " ")
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r" *\n *", "\n", cleaned)

    return cleaned.strip()


def clean_pages(pages: list[PageText]) -> list[PageText]:
    cleaned_pages: list[PageText] = []

    for page in pages:
        cleaned_text = clean_page_text(page.text)
        if cleaned_text:
            cleaned_pages.append(
                PageText(page_number=page.page_number, text=cleaned_text)
            )

    return cleaned_pages
