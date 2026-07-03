# Usage Guide

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Web Interface](#web-interface)
4. [API Usage](#api-usage)
5. [Command Line](#command-line)

## Local Development

### Prerequisites
- Python 3.10+
- pip or conda
- Kaggle API credentials (optional, for dataset download)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/kunaldesale2408/resume-screening-system.git
   cd resume-screening-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   make install
   ```

4. **Setup environment**
   ```bash
   make setup
   ```

5. **Download Kaggle dataset** (optional)
   ```bash
   make download-dataset
   ```

### Running Locally

**Option 1: Run both services with Make**
```bash
make run-all
# Opens two terminals:
# Terminal 1: make run-backend
# Terminal 2: make run-frontend
```

**Option 2: Run services separately**
```bash
# Terminal 1: Start FastAPI backend
make run-backend
# API available at http://localhost:8000
# API docs at http://localhost:8000/docs

# Terminal 2: Start Streamlit frontend
make run-frontend
# App available at http://localhost:8501
```

**Option 3: Manual setup**
```bash
# Backend
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (in new terminal)
streamlit run src/web/streamlit_app.py
```

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Build and Run

```bash
# Build images
make docker-build

# Start containers
make docker-up

# View logs
make docker-logs

# Stop containers
make docker-down
```

### Access Services
- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Docker Compose Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Remove volumes
docker-compose down -v

# Rebuild images
docker-compose build --no-cache
```

## Web Interface

### Main Features

#### 1. Upload & Score
- Upload single or multiple resumes (PDF, TXT, DOCX)
- Paste or upload job description
- Click "Score Resumes" to process
- View ranked results with match percentages

#### 2. Results Dashboard
- View top matched resumes
- See detailed match breakdown
- Highlight matching keywords
- Export results to CSV

#### 3. Analytics
- View match score distribution
- Historical statistics
- Performance metrics

#### 4. Settings
- Adjust similarity threshold
- Configure entity weights
- Set confidence levels

### Workflow Example

1. Open http://localhost:8501
2. Go to "📤 Upload & Score" page
3. Upload resumes:
   - Click "Upload Resume Files"
   - Select multiple PDF/TXT files
4. Paste job description:
   - Copy-paste JD or upload file
5. Click "🚀 Score Resumes"
6. Review results in "📊 Results Dashboard"
7. Export results or adjust settings

## API Usage

### Base URL
```
http://localhost:8000
```

### Health Check
```bash
curl -X GET http://localhost:8000/health
```

### Score Single Resume

**Endpoint**: `POST /score`

```bash
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "John Doe, Python Developer, 5+ years experience...",
    "job_description": "Senior Python Developer, Required: 5+ years, FastAPI..."
  }'
```

**Response**:
```json
{
  "score": 87.5,
  "confidence": 0.92,
  "tfidf_similarity": 0.85,
  "entity_matches": {
    "skills": 0.9,
    "experience": 0.88,
    "education": 0.75
  },
  "matched_keywords": ["Python", "5+ years", "FastAPI", "REST API"],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Batch Score Multiple Resumes

**Endpoint**: `POST /batch_score`

```bash
curl -X POST http://localhost:8000/batch_score \
  -H "Content-Type: application/json" \
  -d '{
    "resumes": [
      {"id": "resume1", "text": "John Doe, Python Developer..."},
      {"id": "resume2", "text": "Jane Smith, Senior Engineer..."}
    ],
    "job_description": "Senior Python Developer...",
    "limit": 10,
    "offset": 0
  }'
```

**Response**:
```json
{
  "total": 2,
  "count": 2,
  "offset": 0,
  "candidates": [
    {
      "id": "resume1",
      "name": "John Doe",
      "score": 87.5,
      "confidence": 0.92,
      "matched_keywords": ["Python", "5+ years", "FastAPI"]
    },
    {
      "id": "resume2",
      "name": "Jane Smith",
      "score": 72.3,
      "confidence": 0.85,
      "matched_keywords": ["Python", "Leadership"]
    }
  ]
}
```

### Python Client Example

```python
import requests

API_URL = "http://localhost:8000"

def score_resume(resume_text, job_description):
    response = requests.post(
        f"{API_URL}/score",
        json={
            "resume_text": resume_text,
            "job_description": job_description
        }
    )
    return response.json()

# Usage
resume = "John Doe, Python Developer, 5+ years..."
jd = "Senior Python Developer, Required: 5+ years..."
result = score_resume(resume, jd)
print(f"Match Score: {result['score']}%")
```

## Command Line

### Available Make Commands

```bash
# Development
make install           # Install dependencies
make setup            # Setup environment
make clean            # Clean cache files

# Running
make run-backend      # Run FastAPI backend
make run-frontend     # Run Streamlit frontend
make run-all          # Instructions for running both

# Testing
make test             # Run tests with coverage
make lint             # Run linting checks
make format           # Format code
make type-check       # Run type checks

# Docker
make docker-build     # Build images
make docker-up        # Start containers
make docker-down      # Stop containers
make docker-logs      # View logs
make docker-clean     # Clean resources

# Data
make download-dataset # Download Kaggle dataset
```

### Manual CLI Commands

```bash
# Run tests
pytest tests/ -v
pytest tests/test_matching.py -v

# Code quality
flake8 src tests
mypy src
black src tests
isort src tests

# Run with Python directly
python -m pytest tests/
```

## Troubleshooting

### Common Issues

**Issue: spaCy model not found**
```bash
python -m spacy download en_core_web_sm
```

**Issue: PDF extraction failing**
```bash
# Install tesseract (Ubuntu/Debian)
sudo apt-get install tesseract-ocr

# Install tesseract (macOS)
brew install tesseract

# Install tesseract (Windows)
# Download from https://github.com/UB-Mannheim/tesseract/wiki
```

**Issue: Port already in use**
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

**Issue: Docker permission denied**
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

## Next Steps

- Review [API Documentation](API.md)
- Check [Deployment Guide](DEPLOYMENT.md)
- Explore [Validation Results](RESULTS.md)
