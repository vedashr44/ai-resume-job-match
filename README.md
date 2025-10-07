# AI Resume - Job Match Recommender

An end-to-end NLP project that ranks relevant job opportunities for a candidate based on resume content. The system ingests resume text (direct input or PDF upload), vectors both resumes and job descriptions with TF-IDF, and surfaces the closest matches with skill alignment feedback.

## Features
- Resume ingestion from raw text or PDF uploads.
- TF-IDF baseline similarity engine with configurable thresholds.
- Automatic skill overlap detection to highlight strengths and potential gaps.
- Streamlit web UI plus a lightweight CLI for experimentation.
- Swappable job dataset (ships with a small sample to get you started).

## Project Structure
```
.
|-- app/
|   |-- config.py          # Runtime configuration and environment overrides
|   |-- data_loader.py     # Dataset validation and dataclass conversion
|   |-- data_models.py     # Dataclasses for job postings
|   |-- embedding.py       # TF-IDF wrapper and similarity utilities
|   |-- preprocessing.py   # Text normalization helpers
|   |-- recommender.py     # Core recommendation engine
|   |-- resume_parser.py   # Resume text extraction (PDF + plain text)
|-- data/
|   |-- jobs_sample.csv    # Example dataset (replace with your own)
|-- streamlit_app.py       # Streamlit UI
|-- main.py                # CLI entrypoint
|-- requirements.txt
|-- README.md
```

## Getting Started
1. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # macOS/Linux
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify the sample pipeline**
   ```bash
   python main.py --resume-text "Applied AI engineer with Python, NLP, and cloud deployment experience."
   ```

## Using Your Own Job Dataset
- Replace `data/jobs_sample.csv` with a richer dataset that contains at least the columns:
  `job_id, job_title, company, location, description, skills`.
- Point the app to that file with an environment variable or `.env` file:
  ```
  JOB_DATASET_PATH=/path/to/your/jobs.csv
  TOP_K_RESULTS=5
  MIN_SIMILARITY_THRESHOLD=0.05
  ```
- Restart the CLI or Streamlit app to pick up the new dataset.

## Using Live Data from Adzuna
- Sign up for a free Adzuna developer account and grab your `app_id` and `app_key`.
- Create a `.env` file (or set environment variables) with:
  ```
  JOB_DATA_SOURCE=adzuna
  ADZUNA_APP_ID=your_app_id
  ADZUNA_APP_KEY=your_app_key
  ADZUNA_QUERY=machine learning engineer       # optional keyword search
  ADZUNA_LOCATION=San Francisco                 # optional location filter
  ADZUNA_MAX_PAGES=2                            # number of pages to fetch
  ADZUNA_RESULTS_PER_PAGE=50                    # Adzuna allows up to 50
  ```
- Restart the app. The recommender will fetch live postings each run and vectorize them on the fly.
- Remember that network calls require internet access and count against Adzuna rate limits; cache results or reduce `ADZUNA_MAX_PAGES` if needed.
- Inside the Streamlit sidebar, pick your target role and location from the dropdowns—each change triggers a fresh Adzuna fetch, so you can explore different job families without editing configuration files.

## Launch the Web App
```bash
streamlit run streamlit_app.py
```
Open the provided local URL, upload a resume (PDF or text), or paste the text and click **Find matching roles**.

## Next Steps & Enhancements
- Swap the TF-IDF baseline for Sentence-BERT or other transformer embeddings (plug into `app/embedding.py`).
- Add feedback generation via GPT APIs using the matched and missing skills list.
- Persist or expose recommendations via a FastAPI or Flask backend for multi-user scenarios.
- Containerize the app and deploy to Streamlit Cloud, Render, or Hugging Face Spaces.

## Troubleshooting
- If PDF extraction returns empty text, ensure the PDF is not scanned. For scanned resumes, integrate OCR (for example, Tesseract).
- For large datasets, consider persisting the fitted vectorizer to disk or upgrading to FAISS or another approximate nearest neighbor index.
