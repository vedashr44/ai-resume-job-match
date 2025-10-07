"""
Data loading utilities for the job dataset.
"""

from pathlib import Path
from typing import List

import pandas as pd

from app.config import Settings
from app.data_models import JobPosting
from app.job_sources import fetch_adzuna_jobs

REQUIRED_COLUMNS = {
    "job_id",
    "job_title",
    "company",
    "location",
    "description",
    "skills",
}


def load_job_dataframe(csv_path: Path) -> pd.DataFrame:
    """
    Load a job dataset CSV into a DataFrame, validating required columns.
    """
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Job dataset not found at {csv_path}. Update JOB_DATASET_PATH or add the file."
        )

    df = pd.read_csv(csv_path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    return df


def job_dataframe_to_models(df: pd.DataFrame) -> List[JobPosting]:
    """
    Convert a dataframe into a list of JobPosting objects.
    """
    jobs: List[JobPosting] = [
        JobPosting(
            job_id=str(row.job_id),
            job_title=row.job_title,
            company=row.company,
            location=row.location,
            description=row.description,
            skills=row.skills,
        )
        for row in df.itertuples(index=False)
    ]
    return jobs


def load_job_postings(csv_path: Path) -> List[JobPosting]:
    """
    Convenience wrapper to load and convert the dataset.
    """
    df = load_job_dataframe(csv_path)
    return job_dataframe_to_models(df)


def load_job_postings_from_settings(settings: Settings) -> List[JobPosting]:
    """
    Load job postings based on the configured data source.
    """
    source = settings.job_data_source.lower()
    if source == "adzuna":
        return fetch_adzuna_jobs(settings)
    if source == "csv":
        return load_job_postings(settings.job_dataset_path)
    raise ValueError(f"Unsupported JOB_DATA_SOURCE '{settings.job_data_source}'.")
