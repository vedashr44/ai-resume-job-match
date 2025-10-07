"""
Resume ingestion helpers for plain text and PDF uploads.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from PyPDF2 import PdfReader


def extract_text_from_pdf(file_obj: BinaryIO) -> str:
    """
    Extract raw text from a PDF file-like object.
    """
    reader = PdfReader(file_obj)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages)


def load_resume_text(file_bytes: bytes, filename: str | None = None) -> str:
    """
    Attempt to extract text from the provided resume payload.
    """
    if not file_bytes:
        return ""

    suffix = Path(filename or "").suffix.lower()
    stream = BytesIO(file_bytes)

    if suffix == ".pdf":
        return extract_text_from_pdf(stream)

    return file_bytes.decode("utf-8", errors="ignore")
