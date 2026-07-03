"""
README for Streamlit Web Application
"""

# Streamlit Web Interface - Resume Screening System

## Overview

This directory contains the interactive Streamlit web application for the Resume Screening System. The application provides a user-friendly interface for uploading resumes, configuring matching parameters, and viewing detailed scoring results with visualizations.

## Features

### 📤 Upload & Score Page
- **Batch PDF Upload**: Upload multiple resumes simultaneously
- **Job Description Input**: Paste or upload job descriptions
- **Real-time Processing**: Progress tracking during scoring
- **Instant Results**: View ranked candidates with match scores

### 📊 Results Dashboard
- **Ranked Results**: View candidates sorted by match score
- **Score Breakdown**: TF-IDF and entity matching scores
- **Visual Charts**: Score comparison and distribution charts
- **Statistics**: Mean, median, standard deviation analysis
- **Export Options**: Download results as CSV or PDF

### 📈 Analytics Page
- **Historical Data**: Track screening statistics over time
- **Performance Trends**: Visualize score trends and patterns
- **Common Patterns**: Identify high-match skills and requirements
- **Insights**: Recommendations based on historical data

### ⚙️ Settings Page
- **Matching Parameters**: Adjust similarity thresholds
- **Feature Weights**: Configure TF-IDF vs Entity matching balance
- **Entity Weighting**: Fine-tune skill, experience, education weights
- **Advanced Settings**: TF-IDF parameters (n-grams, feature count)

## Project Structure

```
src/web/
├── streamlit_app.py          # Main application entry point
├── utils.py                  # Utility functions and helpers
├── components/
│   ├── __init__.py
│   ├── uploader.py          # PDF/text file upload handlers
│   ├── card_display.py      # Resume result cards
│   ├── charts.py            # Data visualizations (Plotly/Matplotlib)
│   └── exporter.py          # CSV/PDF export functionality
└── pages/
    ├── __init__.py
    ├── upload_and_score.py  # Upload & scoring interface
    ├── results_dashboard.py # Results viewing and analysis
    ├── analytics.py        # Historical analytics
    └── settings_page.py    # Configuration and settings
```

## Running the Application

### Local Development

```bash
# Navigate to repository root
cd resume-screening-system

# Install dependencies
pip install -r requirements.txt
Python -m spacy download en_core_web_sm

# Run Streamlit app
streamlit run src/web/streamlit_app.py
```

The application will start at `http://localhost:8501`

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:8501
```

### Using Makefile

```bash
# Run frontend
make run-frontend

# Or run backend and frontend together (in separate terminals)
make run-backend  # Terminal 1
make run-frontend # Terminal 2
```

## Configuration

### Streamlit Config (`.streamlit/config.toml`)

```toml
[theme]
primaryColor = "#1f77b4"              # Primary UI color
backgroundColor = "#ffffff"           # Page background
secondaryBackgroundColor = "#f0f2f6" # Secondary background
textColor = "#262730"                # Text color

[client]
maxUploadSize = 50                   # Max upload size in MB

[server]
port = 8501                          # Streamlit server port
maxUploadSize = 50                   # Server-side max upload
```

### Environment Variables (`.env`)

```bash
# Application
APP_NAME="Resume Screening System"
APP_VERSION="1.0.0"
DEBUG=True

# Paths
DATA_PATH="./data"
MODELS_PATH="./models"

# NLP Configuration
SPACY_MODEL="en_core_web_sm"
TFIDF_MAX_FEATURES=5000
TFIDF_MIN_DF=2
TFIDF_MAX_DF=0.95
TFIDF_NGRAM_RANGE="(1, 2)"

# Matching
TFIDF_WEIGHT=0.6
ENTITY_WEIGHT=0.4
SIMILARITY_THRESHOLD=0.5
CONFIDENCE_THRESHOLD=0.6

# Server
STREAMLIT_PORT=8501
STREAMLIT_LOGGER_LEVEL="info"
```

## Components Documentation

### Uploader Component (`uploader.py`)

**Functions:**
- `upload_pdf_files()`: Handle batch PDF resume uploads
- `upload_text_jd()`: Handle job description input (text or file)
- `show_sample_inputs()`: Display sample data for testing

**Usage:**
```python
from src.web.components import upload_pdf_files, upload_text_jd

resumes = upload_pdf_files()
jd_text = upload_text_jd()
```

### Card Display Component (`card_display.py`)

**Functions:**
- `display_resume_card()`: Show formatted resume result card
- `display_results_table()`: Display results in table format
- `display_no_results()`: Show "no results" message

**Usage:**
```python
from src.web.components import display_resume_card

display_resume_card(
    rank=1,
    filename="resume.pdf",
    overall_score=0.85,
    tfidf_score=0.82,
    entity_score=0.88,
    matched_skills=["Python", "ML"],
    matched_keywords=["AI", "data"]
)
```

### Charts Component (`charts.py`)

**Functions:**
- `create_score_comparison_chart()`: Bar chart of scores
- `create_match_distribution_chart()`: Histogram of match scores
- `create_skills_heatmap()`: Heatmap of skill matches
- `create_timeline_chart()`: Line chart of score trends
- `create_metric_cards()`: Display key metrics

**Usage:**
```python
from src.web.components import create_score_comparison_chart

create_score_comparison_chart(results)
```

### Exporter Component (`exporter.py`)

**Functions:**
- `export_results_csv()`: Export to CSV format
- `export_results_pdf()`: Export to PDF format
- `show_export_options()`: Display export buttons

**Usage:**
```python
from src.web.components import show_export_options

show_export_options(results, job_description)
```

## Page Descriptions

### Upload & Score Page

**Purpose**: Main interface for uploading resumes and job descriptions

**Features:**
- Batch PDF upload with file preview
- Job description input (paste or upload)
- Progress bar during processing
- Real-time result display
- Score summary metrics

**File**: `pages/upload_and_score.py`

### Results Dashboard

**Purpose**: Detailed analysis and visualization of scored results

**Features:**
- Ranked candidate list with filtering
- Match score breakdown
- Interactive charts and visualizations
- Statistical summaries
- Export functionality

**File**: `pages/results_dashboard.py`

### Analytics Page

**Purpose**: Historical trends and pattern analysis

**Features:**
- Historical screening statistics
- Performance trend charts
- Common matched skills
- Recommendations based on patterns

**File**: `pages/analytics.py`

### Settings Page

**Purpose**: Configuration and parameter tuning

**Features:**
- Similarity threshold adjustment
- Feature weight configuration
- Entity weight breakdown
- TF-IDF parameters
- Reset to defaults

**File**: `pages/settings_page.py`

## Integration with Backend

The Streamlit frontend can integrate with the FastAPI backend:

```python
import requests

API_BASE_URL = "http://localhost:8000"

def score_resumes_via_api(resume_bytes, jd_text):
    """Call backend API for scoring."""
    response = requests.post(
        f"{API_BASE_URL}/score",
        files={"resume": resume_bytes},
        data={"job_description": jd_text}
    )
    return response.json()
```

## Styling and Customization

### Custom CSS Classes

The app includes custom CSS classes for styling:

```css
.main-header          /* Main page header */
.section-header       /* Section headers */
.match-card          /* Result cards */
.high-match          /* High match styling */
.medium-match        /* Medium match styling */
.low-match           /* Low match styling */
.metric-card         /* Metric cards */
```

### Color Scheme

- **Primary**: #1f77b4 (Blue)
- **Background**: #ffffff (White)
- **Secondary Background**: #f0f2f6 (Light Gray)
- **Text**: #262730 (Dark Gray)
- **High Match**: #00cc00 (Green)
- **Medium Match**: #ffaa00 (Orange)
- **Low Match**: #ff0000 (Red)

## Performance Optimization

### Caching

Streamlit's caching is used for expensive operations:

```python
@st.cache_data
def load_model():
    return load_vectorizer_and_model()
```

### Session State

Session state preserves data across reruns:

```python
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
```

## Troubleshooting

### Issue: "ModuleNotFoundError" when importing

**Solution**: Ensure you're running from the repository root and PYTHONPATH includes the repo directory.

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
streamlit run src/web/streamlit_app.py
```

### Issue: PDF upload not working

**Solution**: Ensure `pdfplumber` is installed and accessible.

```bash
pip install pdfplumber
```

### Issue: Slow performance with large files

**Solution**: Increase the `maxUploadSize` in `.streamlit/config.toml` and adjust batch processing parameters.

## Future Enhancements

- [ ] Real-time scoring with WebSocket updates
- [ ] Candidate profile management and tracking
- [ ] Advanced filtering and search
- [ ] Email notifications for high matches
- [ ] API key management for backend authentication
- [ ] Drag-and-drop file upload interface
- [ ] Resume preview with highlighting
- [ ] Batch job scheduling
- [ ] Performance metrics dashboard
- [ ] Multi-language support

## Contributing

To contribute to the web interface:

1. Create a new branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Submit a pull request with description

## Support

For issues or questions:
- Open a GitHub issue
- Contact: kunaldesale9766@gmail.com
- GitHub: [@kunaldesale2408](https://github.com/kunaldesale2408)
