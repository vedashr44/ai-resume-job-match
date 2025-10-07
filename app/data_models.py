"""
Dataclasses used by the recommender pipeline.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class JobPosting:
    """
    Lightweight container for job posting information.
    """

    job_id: str
    job_title: str
    company: str
    location: str
    description: str
    skills: str

    def as_dict(self) -> Dict[str, str]:
        """Return a serializable representation for UI layers."""
        return {
            "job_id": self.job_id,
            "job_title": self.job_title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "skills": self.skills,
        }

    @property
    def full_text(self) -> str:
        """
        Concatenate relevant text fields to represent the posting.
        """
        parts: List[str] = [
            self.job_title,
            self.company,
            self.location,
            self.description,
            self.skills,
        ]
        return " ".join(part for part in parts if part)
