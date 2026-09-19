"""PDF text extraction using PyMuPDF. Owned by Safa."""

import re

import fitz  # PyMuPDF


class PageText:
    def __init__(self, page_number: int, text: str):
        self.page_number = page_number
        self.text = text

    def to_dict(self) -> dict:
        return {"page_number": self.page_number, "text": self.text}


def extract_pages(file_path: str) -> list[PageText]:
    """Extract text page-by-page, preserving page numbers."""
    pages: list[PageText] = []
    with fitz.open(file_path) as doc:
        for i, page in enumerate(doc):
            text = page.get_text("text")
            pages.append(PageText(page_number=i + 1, text=text))
    return pages


def extract_text_from_pdf(file_path: str) -> str:
    """Extract full concatenated text from a PDF (page breaks preserved as markers)."""
    pages = extract_pages(file_path)
    return "\n\n".join(f"[PAGE {p.page_number}]\n{p.text}" for p in pages)


SECTION_HEADER_PATTERN = re.compile(
    r"^\s*(\d+(?:\.\d+)*)\s+([A-Z][A-Za-z0-9 ,'&/-]{2,80})\s*$", re.MULTILINE
)


def extract_sections(pages: list[PageText]) -> list[dict]:
    """Best-effort detection of numbered section headers (e.g. '10.1 Renewal').

    Returns a list of {"section": "10.1", "title": "Renewal", "page": 6}.
    This is heuristic — not guaranteed for every contract layout, and is meant
    to give source-traceability hints, not a formal document outline.
    """
    sections: list[dict] = []
    for page in pages:
        for match in SECTION_HEADER_PATTERN.finditer(page.text):
            sections.append(
                {
                    "section": match.group(1),
                    "title": match.group(2).strip(),
                    "page": page.page_number,
                }
            )
    return sections
