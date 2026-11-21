# AI-Powered Resume Screening System

Ranks resumes against a job description and explains each score: which required skills a candidate has, which are missing, and how their experience and education compare with what the job asks for.

It combines two signals:

- **TF-IDF similarity**: how closely the resume's vocabulary matches the job description
- **Requirement matching**: skills, years of experience, education level and certifications, extracted with spaCy and rules

A **FastAPI** backend exposes the engine as a REST API, and a **Streamlit** app lets a recruiter upload resumes and review the ranking. Both run in **Docker**.

---

## How it works

```
 PDF / DOCX / TXT
        │
        ▼
 1. Extract text      pdfplumber → PyMuPDF → PyPDF2, OCR (Tesseract) for scanned PDFs
        │
        ▼
 2. Clean             Unicode normalisation; remove e-mails, phone numbers, URLs
        │
        ├──────────────────────────────┐
        ▼                              ▼
 3a. Lemmatise (spaCy)          3b. Extract structured facts
     drop stop words                 - skills: PhraseMatcher over a 100+ skill taxonomy with aliases
     + one token per skill           - experience: "5+ years" or summed job date ranges
        │                            - education: degree level (Diploma → PhD)
        ▼                            - certifications, name and organisations (spaCy NER)
 4a. TF-IDF + cosine                    │
     similarity to the JD               ▼
        │                       4b. Requirement match against the JD
        │                            - skill groups: "FastAPI, Flask, or Django" is met by any one
        │                            - "a plus" / "nice to have" skills count half
        └──────────────┬──────────────┘
                       ▼
 5. overall = 0.4 × TF-IDF + 0.6 × requirement match  →  rank  →  Strong / Possible / Weak
```

### Details worth knowing

| Decision | Why |
|---|---|
| Skill aliases map to one canonical name (`sklearn` → `scikit-learn`, `ML` → `Machine Learning`) | Plain TF-IDF treats them as unrelated words |
| Each skill is also added to the TF-IDF text as one token (`skill_scikit_learn`) | So aliases count as the same term in the similarity score too |
| Words like "Go", "Excel", "Spark" and "REST" are matched case-sensitively | "go the extra mile" and "excel at teamwork" aren't skills |
| Job sentences with "or", "such as" or "/" become *any-of* groups | A job asking for "FastAPI, Flask, or Django" shouldn't penalise someone who knows only Flask |
| Soft skills (communication, teamwork) aren't scored | A resume can claim them but can't show them |
| Only requirements the job states are scored, and weights are re-normalised | A job with no degree requirement doesn't penalise anyone for education |
| Date ranges in the experience section are merged before summing | Overlapping jobs aren't double-counted; education dates are ignored |
| TF-IDF is fitted on the batch (the job plus all uploaded resumes) | No external corpus is needed. A resume's TF-IDF score can shift slightly when other resumes are added, so use it for ranking within a batch. |

Weights and thresholds live in [`config/features_config.json`](config/features_config.json); the skill taxonomy is in [`config/skills.json`](config/skills.json) and can be extended without code changes.

---

## Accuracy

There is no published accuracy figure yet. The shortlist thresholds are starting values, not tuned ones.

To measure accuracy, label real resumes as fit (1) or not fit (0) for a job and run:

```bash
python scripts/evaluate.py path/to/labels.csv --out report.json
```

It reports accuracy, precision, recall and F1 at the configured threshold, ROC-AUC, precision@k per job, the best-F1 threshold, and seconds per resume. The CSV format is shown in [`tests/fixtures/eval_demo/labels.csv`](tests/fixtures/eval_demo/labels.csv). That folder is a small **synthetic** set used to test the script, not a benchmark.

---

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/kunaldesale2408/resume-screening-system.git
cd resume-screening-system
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt   # includes the spaCy en_core_web_sm model
```

**Streamlit app** (scores in-process, no backend needed):

```bash
streamlit run src/web/streamlit_app.py     # http://localhost:8501
```

**API**:

```bash
uvicorn src.api.main:app --reload --port 8000   # docs at http://localhost:8000/docs
```

**Both in Docker** (the Streamlit container calls the API container):

```bash
cp .env.example .env
docker compose up --build
```

### API

| Method | Path | Body | Returns |
|---|---|---|---|
| `GET` | `/health` | | status, version, whether the spaCy model loaded |
| `GET` | `/config` | | current weights and thresholds |
| `POST` | `/score` | multipart: `resumes` (files), `job_description` (text) or `jd_file` | ranked results |
| `POST` | `/score/text` | JSON: `job_description`, `resumes: [{name, text}]` | ranked results |

```bash
curl -X POST http://localhost:8000/score \
  -F "job_description=<assets/sample_jd.txt" \
  -F "resumes=@candidate1.pdf" -F "resumes=@candidate2.docx"
```

Each result includes `overall_score`, `tfidf_score`, `entity_score`, `component_scores` (skills, experience, education, certifications), `matched_skills`, `missing_skills`, `missing_preferred`, `matched_keywords`, `years_experience`, `education` and a `recommendation`.

---

## Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

38 tests cover extraction (TXT, DOCX, PDF, corrupt files), cleaning, skill matching, requirement parsing, experience and education extraction, scoring, every API endpoint and error case, and the evaluation script.

---

## Project structure

```
src/
├── nlp.py                      # loads the spaCy pipeline once
├── preprocessing/
│   ├── extractor.py            # PDF / DOCX / TXT → text (with OCR fallback)
│   └── cleaner.py              # normalisation and lemmatisation
├── feature_engineering/
│   ├── skills.py               # skill taxonomy matching, job requirement groups
│   ├── entities.py             # sections, experience, education, certifications, NER
│   └── __init__.py             # ResumeProfile / JobProfile builders
├── matching/
│   └── scorer.py               # TF-IDF similarity + requirement match → ranking
├── api/
│   ├── main.py                 # FastAPI app
│   ├── routes/scoring.py       # /score, /score/text, /config
│   ├── services/scoring_service.py
│   └── schemas.py              # request/response models
└── web/                        # Streamlit app (upload, results, analytics)
    └── scoring_client.py       # calls the API if API_URL is set, else scores in-process
config/
├── features_config.json        # weights and thresholds
└── skills.json                 # skill taxonomy
scripts/evaluate.py             # accuracy against human labels
tests/                          # pytest suite + synthetic evaluation fixtures
docker/                         # Dockerfiles for backend and frontend
```

---

## Limitations and next steps

- **Lexical matching.** TF-IDF and the taxonomy only catch skills written in recognisable words. Sentence embeddings (e.g. `all-MiniLM-L6-v2`) would catch paraphrases such as "built neural nets" for Deep Learning.
- **Experience isn't weighted by relevance.** Eight years as a chef counts the same as eight years in ML. Experience could be counted only in roles that mention the job's skills.
- **Thresholds aren't tuned.** They need a labelled set and `scripts/evaluate.py`.
- **Settings page.** The sliders on the Settings page aren't wired to the engine yet; it reads `config/features_config.json`.
- **Bias.** Names, e-mails and phone numbers are stripped before matching, but scores should support a recruiter's decision, not replace it.

---

## Author

**Kunal Desale** · GitHub: [@kunaldesale2408](https://github.com/kunaldesale2408)
