"""
Basic text normalization helpers.
"""

import re
from typing import Iterable


WHITESPACE_RE = re.compile(r"\s+")
PUNCT_NUM_RE = re.compile(r"[^a-zA-Z\s]")


def normalize_text(text: str) -> str:
    """
    Normalize raw text for vectorization.
    """
    if not isinstance(text, str):
        return ""
    lowered = text.lower()
    stripped = PUNCT_NUM_RE.sub(" ", lowered)
    normalized = WHITESPACE_RE.sub(" ", stripped).strip()
    return normalized


def normalize_corpus(texts: Iterable[str]) -> list[str]:
    """
    Apply `normalize_text` across a corpus.
    """
    return [normalize_text(text) for text in texts]
