"""
Vectorization utilities for representing text.
"""

from __future__ import annotations

from typing import Iterable, Optional, Sequence

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.preprocessing import normalize_corpus


class TfidfEmbeddingModel:
    """
    Wrapper around scikit-learn's TF-IDF vectorizer with corpus normalization.
    """

    def __init__(
        self,
        *,
        max_features: Optional[int] = 5000,
        ngram_range: tuple[int, int] = (1, 2),
        stop_words: str | None = "english",
    ) -> None:
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            stop_words=stop_words,
        )
        self._fitted = False

    def fit(self, documents: Sequence[str]) -> csr_matrix:
        normalized = normalize_corpus(documents)
        matrix = self.vectorizer.fit_transform(normalized)
        self._fitted = True
        return matrix

    def fit_transform(self, documents: Sequence[str]) -> csr_matrix:
        normalized = normalize_corpus(documents)
        matrix = self.vectorizer.fit_transform(normalized)
        self._fitted = True
        return matrix

    def transform(self, documents: Sequence[str]) -> csr_matrix:
        if not self._fitted:
            raise RuntimeError("Vectorizer must be fitted before calling transform().")
        normalized = normalize_corpus(documents)
        return self.vectorizer.transform(normalized)

    def similarity(self, query_vec: csr_matrix, corpus_matrix: csr_matrix) -> np.ndarray:
        """
        Compute cosine similarity between a query vector and corpus matrix.
        """
        return cosine_similarity(query_vec, corpus_matrix, dense_output=True)[0]
