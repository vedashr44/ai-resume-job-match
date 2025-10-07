"""
Application configuration helpers.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import os

# The dependency is optional; gracefully skip if unavailable.
try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    def load_dotenv(*_args, **_kwargs):  # type: ignore
        return False

# Load environment variables from a local .env file when present.
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Container for runtime configuration."""

    job_dataset_path: Path = Path(
        os.getenv("JOB_DATASET_PATH", "data/jobs_sample.csv")
    )
    job_data_source: str = os.getenv("JOB_DATA_SOURCE", "csv").lower()
    top_k_results: int = int(os.getenv("TOP_K_RESULTS", "5"))
    min_similarity_threshold: float = float(os.getenv("MIN_SIMILARITY_THRESHOLD", "0.05"))
    cache_dir: Optional[Path] = (
        Path(os.getenv("MODEL_CACHE_DIR")) if os.getenv("MODEL_CACHE_DIR") else None
    )
    adzuna_app_id: Optional[str] = os.getenv("ADZUNA_APP_ID")
    adzuna_app_key: Optional[str] = os.getenv("ADZUNA_APP_KEY")
    adzuna_country: str = os.getenv("ADZUNA_COUNTRY", "us")
    adzuna_results_per_page: int = int(os.getenv("ADZUNA_RESULTS_PER_PAGE", "50"))
    adzuna_max_pages: int = int(os.getenv("ADZUNA_MAX_PAGES", "2"))
    adzuna_query: Optional[str] = os.getenv("ADZUNA_QUERY")
    adzuna_location: Optional[str] = os.getenv("ADZUNA_LOCATION")
    adzuna_filters: Optional[str] = os.getenv("ADZUNA_FILTERS")


settings = Settings()
