# Quick Start Guide - Streamlit Web Application

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.10+
- pip or conda
- ~500MB disk space

### Step 1: Clone & Setup

```bash
# Clone repository
git clone https://github.com/kunaldesale2408/resume-screening-system.git
cd resume-screening-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Optional: Edit .env for custom settings
# nano .env  or  code .env
```

### Step 3: Run the Application

```bash
# Start Streamlit app
streamlit run src/web/streamlit_app.py
```

✅ App opens at **http://localhost:8501**

---

## 📖 Using the Application

### 1️⃣ Upload Resumes

1. Navigate to **📤 Upload & Score** page
2. Click **Upload PDFs** and select resume files
3. Can upload multiple files at once
4. Files show in preview with size

### 2️⃣ Add Job Description

**Option A: Paste Text**
- Select "📝 Paste Text"
- Paste job description content
- Preview shows first 500 characters

**Option B: Upload File**
- Select "📄 Upload File"
- Upload TXT or PDF containing JD
- Auto-extracts text from PDF

### 3️⃣ Score Resumes

1. Click **🚀 Score Resumes** button
2. Progress bar shows processing status
3. Results display immediately

### 4️⃣ View Results

**Results Dashboard** shows:
- ✅ Ranked list by match score
- 📊 Score breakdown (TF-IDF + Entity)
- 🎯 Matched skills highlighted
- 📝 Matched keywords

### 5️⃣ Export & Analyze

**Export Options:**
- 📥 Download as CSV
- 📋 Download as PDF

**Analytics:**
- 📈 Historical trends
- 🔥 Most matched skills
- 💡 Recommendations

---

## ⚙️ Configuration

### Adjust Matching Parameters

1. Go to **⚙️ Settings** page
2. **Similarity Threshold**: Min score to consider (0.0-1.0)
3. **Feature Weights**:
   - TF-IDF: Text similarity
   - Entity: Skill/experience matching
4. **Entity Weights**: Breakdown by type

### Sample Data

Test with sample files:

```bash
# Load from UI
- Click "⚙️ Settings"
- Find "📚 Load Sample Data"
- Click "Load Sample Job Description"
- Click "Load Sample Resume"
```

---

## 🐳 Using Docker

### Build & Run

```bash
# Build images
docker-compose build

# Run containers
docker-compose up
```

**Access:**
- Frontend: http://localhost:8501
- API: http://localhost:8000/docs

### Stop

```bash
# Stop containers
docker-compose down

# Clean up volumes
docker-compose down -v
```

---

## 📋 Command Reference

### Using Makefile

```bash
# Install deps
make install

# Setup environment
make setup

# Run frontend only
make run-frontend

# Run backend only
make run-backend

# Format code
make format

# Run tests
make test

# Docker operations
make docker-build
make docker-up
make docker-down
```

### Direct Commands

```bash
# Run Streamlit
streamlit run src/web/streamlit_app.py

# Run FastAPI backend
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v --cov=src

# Format code
black src tests
isort src tests
```

---

## 🔧 Troubleshooting

### Issue: Port 8501 already in use

```bash
# Run on different port
streamlit run src/web/streamlit_app.py --server.port=8502
```

### Issue: Module import errors

```bash
# Ensure in repo root and run:
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
streamlit run src/web/streamlit_app.py
```

### Issue: PDF upload fails

```bash
# Reinstall dependencies
pip install --upgrade pdfplumber pdf2image
```

### Issue: Memory issues with large files

```bash
# Edit .streamlit/config.toml
[client]
maxUploadSize = 100  # Increase to 100MB

[server]
maxUploadSize = 100
```

---

## 📚 Additional Resources

### Documentation Files
- **[README.md](../README.md)** - Project overview
- **[ARCHITECTURE.md](../docs/ARCHITECTURE.md)** - System design
- **[Web README](./README.md)** - Web interface details

### Key Files
- **Main App**: `src/web/streamlit_app.py`
- **Components**: `src/web/components/`
- **Pages**: `src/web/pages/`
- **Config**: `.streamlit/config.toml`

### API Documentation

When running backend:

```bash
uvicorn src.api.main:app --reload
# Visit http://localhost:8000/docs
```

---

## 💡 Tips & Best Practices

✅ **Do:**
- Upload 5-10 resumes at a time for best performance
- Use clear, complete job descriptions
- Regularly export results for backup
- Adjust thresholds based on your needs
- Try sample data first to understand UI

❌ **Don't:**
- Upload extremely large PDF files (>10MB)
- Modify core config files without understanding
- Use special characters in filenames
- Leave app running idle for extended periods

---

## 🤝 Support & Feedback

**Issues or Questions?**
- GitHub Issues: [Create Issue](https://github.com/kunaldesale2408/resume-screening-system/issues)
- Email: kunaldesale9766@gmail.com
- GitHub: [@kunaldesale2408](https://github.com/kunaldesale2408)

**Contributing:**
- Fork repository
- Create feature branch
- Submit pull request

---

## 📊 Performance Metrics

- **Accuracy**: 85%+ on validated dataset
- **Processing Speed**: ~1 resume/second
- **Memory Usage**: ~500MB for typical use
- **Concurrent Users**: 5-10 (single instance)

---

**Happy Resume Screening! 🎉**
