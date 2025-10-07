"""
Simple CLI for running the recommender against a resume snippet.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from app.recommender import JobRecommender
from app.resume_parser import load_resume_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Resume-Job Match Recommender")
    parser.add_argument(
        "--resume-file",
        type=Path,
        help="Path to a resume text or PDF file.",
    )
    parser.add_argument(
        "--resume-text",
        type=str,
        help="Raw resume text to evaluate.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=None,
        help="Number of recommendations to return.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.resume_file:
        if not args.resume_file.exists():
            raise FileNotFoundError(f"Resume file not found: {args.resume_file}")
        resume_text = load_resume_text(
            args.resume_file.read_bytes(), args.resume_file.name
        )
    elif args.resume_text:
        resume_text = args.resume_text
    else:
        raise SystemExit("Provide --resume-file or --resume-text.")

    recommender = JobRecommender()
    recommendations = recommender.recommend(resume_text, top_k=args.top_k)

    if not recommendations:
        print("No matching jobs found.")
        return

    for idx, rec in enumerate(recommendations, start=1):
        job = rec.job
        print(
            f"{idx}. {job.job_title} @ {job.company} ({job.location}) "
            f"- similarity {rec.similarity:.3f}"
        )
        if rec.matched_skills:
            print(f"   matched skills: {', '.join(rec.matched_skills)}")
        if rec.missing_skills:
            print(f"   potential gaps: {', '.join(rec.missing_skills)}")
        print()


if __name__ == "__main__":
    main()
