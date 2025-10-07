"""
Streamlit UI for the AI Resume-Job Match Recommender System.
"""

from __future__ import annotations

from dataclasses import replace
from typing import List, Optional

import streamlit as st

from app.config import settings
from app.recommender import JobRecommender, Recommendation
from app.resume_parser import load_resume_text


@st.cache_resource
def load_engine(
    data_source: str,
    job_query: Optional[str],
    job_location: Optional[str],
) -> JobRecommender:
    if data_source == "adzuna":
        config_override = replace(
            settings,
            job_data_source="adzuna",
            adzuna_query=job_query or None,
            adzuna_location=job_location or None,
        )
        return JobRecommender(config=config_override)
    if data_source == "csv":
        return JobRecommender(config=replace(settings, job_data_source="csv"))
    return JobRecommender()


def render_recommendations(recommendations: List[Recommendation]) -> None:
    for rec in recommendations:
        job = rec.job
        header = f"{job.job_title} - {job.company} - {job.location}"
        with st.expander(header, expanded=False):
            st.markdown(f"**Similarity:** {rec.similarity:.3f}")
            if rec.matched_skills:
                st.markdown("**Strong alignment:** " + ", ".join(rec.matched_skills))
            if rec.missing_skills:
                st.markdown("**Suggested improvements:** " + ", ".join(rec.missing_skills))
            st.markdown("**Description**")
            st.write(job.description)
            st.markdown("**Skills (dataset)**")
            st.write(job.skills)


def main() -> None:
    st.set_page_config(
        page_title="AI Resume - Job Match Recommender",
        page_icon="AI",
        layout="wide",
    )
    st.title("Resume to Job Match Recommender")
    st.markdown(
        "Upload your resume or paste the text to discover roles that best match your skills."
    )

    with st.sidebar:
        st.header("Configuration")
        top_k = st.slider("Number of recommendations", min_value=3, max_value=10, value=settings.top_k_results)
        threshold = st.slider(
            "Minimum similarity",
            min_value=0.0,
            max_value=1.0,
            value=float(settings.min_similarity_threshold),
            step=0.01,
        )
        selected_role = settings.adzuna_query or "Any role"
        selected_location = settings.adzuna_location or "Anywhere"
        if settings.job_data_source == "adzuna":
            st.caption(
                "Using live job postings from Adzuna. "
                "Select the focus role and location for each search."
            )
            role_options = [
                "Any role",
                "Machine Learning Engineer",
                "Data Scientist",
                "AI Researcher",
                "MLOps Engineer",
                "Software Engineer",
                "Product Manager",
                "UX Designer",
                "Business Analyst",
            ]
            if selected_role not in role_options:
                role_options.insert(0, selected_role)
            role_choice = st.selectbox("Role focus", role_options, index=role_options.index(selected_role))

            location_options = [
                "Anywhere",
                "Remote",
                "San Francisco",
                "New York",
                "Seattle",
                "Los Angeles",
                "Austin",
                "Boston",
                "Chicago",
                "London",
            ]
            if selected_location not in location_options:
                location_options.insert(0, selected_location)
            location_choice = st.selectbox(
                "Location",
                location_options,
                index=location_options.index(selected_location),
            )
        else:
            st.caption(
                f"Using dataset: `{settings.job_dataset_path}`. "
                "Replace this file or point JOB_DATASET_PATH to your own file."
            )
            role_choice = None
            location_choice = None

    uploaded_file = st.file_uploader("Upload a resume (PDF or TXT)", type=["pdf", "txt"])
    resume_text_input = st.text_area(
        "Or paste resume text",
        height=220,
        placeholder="Paste your resume summary, experience, and skills here...",
    )

    resume_text = ""
    if uploaded_file:
        resume_text = load_resume_text(uploaded_file.read(), uploaded_file.name)
    elif resume_text_input.strip():
        resume_text = resume_text_input

    if st.button("Find matching roles", type="primary"):
        if not resume_text.strip():
            st.warning("Provide a resume file or text to run the recommender.")
        else:
            try:
                query_value = None
                location_value = None
                if settings.job_data_source == "adzuna":
                    query_value = None if role_choice == "Any role" else role_choice
                    location_value = None if location_choice == "Anywhere" else location_choice
                engine = load_engine(settings.job_data_source, query_value, location_value)
                recommendations = engine.recommend(
                    resume_text,
                    top_k=top_k,
                    min_similarity=threshold,
                )
            except ValueError as exc:
                st.error(str(exc))
                return

            if not recommendations:
                st.info("No matches cleared the similarity threshold. Try lowering it or enriching your resume.")
            else:
                st.success(f"Found {len(recommendations)} relevant roles.")
                render_recommendations(recommendations)


if __name__ == "__main__":
    main()
