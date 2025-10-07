"""
Utilities for fetching live job postings from the Adzuna API.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

import requests

from app.config import Settings
from app.data_models import JobPosting

logger = logging.getLogger(__name__)

ADZUNA_ENDPOINT_TEMPLATE = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"


def _build_params(
    *,
    settings: Settings,
    page: int,
) -> Dict[str, str]:
    params: Dict[str, str] = {
        "app_id": settings.adzuna_app_id or "",
        "app_key": settings.adzuna_app_key or "",
        "results_per_page": str(settings.adzuna_results_per_page),
    }
    if settings.adzuna_query:
        params["what"] = settings.adzuna_query
    if settings.adzuna_location:
        params["where"] = settings.adzuna_location
    if settings.adzuna_filters:
        params["what_and"] = settings.adzuna_filters
    return params


def _extract_skills(result: dict) -> str:
    """
    Derive a semicolon-delimited skills string from Adzuna tags and metadata.
    """
    tags = []
    tag_entries = result.get("tags") or []
    for tag in tag_entries:
        label = tag.get("tag") or tag.get("label")
        if label:
            tags.append(label.strip())

    category = (result.get("category") or {}).get("label")
    if category:
        tags.append(category.strip())

    # Remove duplicates while preserving order.
    seen = set()
    deduped = []
    for tag in tags:
        lowered = tag.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        deduped.append(tag)
    return ";".join(deduped)


def _as_job_posting(result: dict) -> Optional[JobPosting]:
    job_id = result.get("id")
    if job_id is None:
        return None

    company = (result.get("company") or {}).get("display_name", "Unknown company")
    location = (result.get("location") or {}).get("display_name", "Remote/Unspecified")
    description = result.get("description") or ""
    title = result.get("title") or "Untitled role"

    skills = _extract_skills(result)

    return JobPosting(
        job_id=str(job_id),
        job_title=title,
        company=company,
        location=location,
        description=description,
        skills=skills,
    )


def fetch_adzuna_jobs(settings: Settings) -> List[JobPosting]:
    """
    Retrieve live job postings using the Adzuna REST API.

    Raises:
        ValueError: If credentials are missing or no jobs are fetched.
        requests.HTTPError: For non-successful responses.
    """
    if not settings.adzuna_app_id or not settings.adzuna_app_key:
        raise ValueError(
            "Adzuna credentials missing. Set ADZUNA_APP_ID and ADZUNA_APP_KEY."
        )

    max_pages = max(1, settings.adzuna_max_pages)
    postings: List[JobPosting] = []

    for page in range(1, max_pages + 1):
        params = _build_params(settings=settings, page=page)
        endpoint = ADZUNA_ENDPOINT_TEMPLATE.format(
            country=settings.adzuna_country,
            page=page,
        )
        try:
            response = requests.get(endpoint, params=params, timeout=20)
            response.raise_for_status()
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response else "unknown"
            detail = ""
            try:
                payload = exc.response.json() if exc.response else {}
                detail = payload.get("error") or payload.get("message") or ""
            except Exception:
                detail = exc.response.text if exc.response else ""
            raise ValueError(
                f"Adzuna request failed (status {status}). {detail}".strip()
            ) from exc
        payload = response.json()
        results = payload.get("results") or []
        for result in results:
            job = _as_job_posting(result)
            if job:
                postings.append(job)
        # Stop early if this page returned fewer results than requested.
        if len(results) < settings.adzuna_results_per_page:
            break

    if not postings:
        raise ValueError("No jobs retrieved from Adzuna. Adjust query parameters.")

    logger.info("Fetched %s jobs from Adzuna.", len(postings))
    return postings
