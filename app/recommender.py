"""
Core recommendation logic for matching resumes to job postings.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

import numpy as np

from app.config import Settings, settings
from app.data_loader import load_job_postings_from_settings
from app.data_models import JobPosting
from app.embedding import TfidfEmbeddingModel
from app.preprocessing import normalize_text


@dataclass
class Recommendation:
    job: JobPosting
    similarity: float
    matched_skills: List[str]
    missing_skills: List[str]

    def as_dict(self) -> dict:
        return {
            "job_id": self.job.job_id,
            "job_title": self.job.job_title,
            "company": self.job.company,
            "location": self.job.location,
            "similarity": round(self.similarity, 3),
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "description": self.job.description,
            "skills": self.job.skills,
        }


class JobRecommender:
    """
    Engine that surfaces relevant job roles for a given resume text.
    """

    def __init__(
        self,
        *,
        config: Settings = settings,
        embedding_model: Optional[TfidfEmbeddingModel] = None,
    ) -> None:
        self.config = config
        self.embedding_model = embedding_model or TfidfEmbeddingModel()

        self._job_postings: List[JobPosting] = load_job_postings_from_settings(self.config)
        self._job_matrix = self.embedding_model.fit_transform(
            [posting.full_text for posting in self._job_postings]
        )

    @staticmethod
    def _parse_skills(skills_blob: str) -> List[str]:
        """
        Convert a delimited skills field into a clean list.
        """
        if not isinstance(skills_blob, str):
            return []
        raw_skills = [
            skill.strip()
            for chunk in skills_blob.split(";")
            for skill in chunk.split(",")
        ]
        return [skill for skill in raw_skills if skill]

    def _skill_overlap(self, resume_text: str, job: JobPosting) -> tuple[list[str], list[str]]:
        resume_normalized = normalize_text(resume_text)
        resume_tokens = set(resume_normalized.split())

        job_skills = self._parse_skills(job.skills)
        matched = []
        missing = []
        for skill in job_skills:
            tokens = [token.lower() for token in skill.split()]
            if all(token in resume_tokens for token in tokens):
                matched.append(skill)
            else:
                missing.append(skill)
        return matched, missing

    def recommend(
        self,
        resume_text: str,
        *,
        top_k: Optional[int] = None,
        min_similarity: Optional[float] = None,
    ) -> List[Recommendation]:
        """
        Rank job postings for the provided resume text.
        """
        if not resume_text.strip():
            return []

        k = top_k or self.config.top_k_results
        threshold = (
            min_similarity
            if min_similarity is not None
            else self.config.min_similarity_threshold
        )

        resume_vec = self.embedding_model.transform([resume_text])
        similarities = self.embedding_model.similarity(resume_vec, self._job_matrix)
        ranked_indices = np.argsort(similarities)[::-1]

        recommendations: List[Recommendation] = []
        for idx in ranked_indices:
            score = float(similarities[idx])
            if score < threshold and len(recommendations) >= k:
                break
            job = self._job_postings[idx]
            matched_skills, missing_skills = self._skill_overlap(resume_text, job)
            recommendations.append(
                Recommendation(
                    job=job,
                    similarity=score,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                )
            )
            if len(recommendations) >= k:
                break
        return recommendations

    def list_jobs(self) -> List[JobPosting]:
        """
        Convenience accessor for underlying job postings.
        """
        return list(self._job_postings)
