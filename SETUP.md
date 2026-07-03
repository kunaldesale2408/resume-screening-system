# 🚀 Setup Instructions

## Option 1: Automated Setup (Recommended)

### Linux/macOS

```bash
# Clone repository
git clone https://github.com/kunaldesale2408/resume-screening-system.git
cd resume-screening-system

# Run setup script
bash scripts/setup.sh

# Run the application
streamlit run src/web/streamlit_app.py
```

### Windows

```bash
# Clone repository
git clone https://github.com/kunaldesale2408/resume-screening-system.git
cd resume-screening-system

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Copy environment file
copy .env.example .env

# Run the application
streamlit run src/web/streamlit_app.py
```

---

## Option 2: Using Make Commands

```bash
# Install dependencies
make install

# Setup environment
make setup

# Run frontend
make run-frontend
```

---

## Option 3: Docker

```bash
# Build and run
docker-compose up --build

# Access at http://localhost:8501
```

---

## Option 4: Manual Setup

### Step 1: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 3: Configure Environment

```bash
cp .env.example .env
# Optional: Edit .env for custom settings
```

### Step 4: Run Application

```bash
streamlit run src/web/streamlit_app.py
```

---

## ✅ Verify Installation

### Check Python
```bash
python --version  # Should be 3.10+
```

### Check Dependencies
```bash
pip list | grep streamlit
pip list | grep spacy
```

### Check spaCy Model
```bash
python -m spacy validate
```

### Test Import
```bash
python -c "import src.config; print('✓ Config loads')"
```

---

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:8501 | Streamlit web app |
| API Docs | http://localhost:8000/docs | FastAPI Swagger UI |
| API | http://localhost:8000 | FastAPI backend |

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8501  # Linux/macOS
netstat -ano | findstr :8501  # Windows

# Kill process
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows

# Or use different port
streamlit run src/web/streamlit_app.py --server.port=8502
```

### Module Import Error

```bash
# Add repo to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
streamlit run src/web/streamlit_app.py
```

### PDF Upload Issues

```bash
# Reinstall PDF dependencies
pip install --upgrade pdfplumber pdf2image
```

### Memory Issues

```bash
# Edit .streamlit/config.toml
[client]
maxUploadSize = 100  # Increase to 100MB
```

---

## 📖 Documentation

- **[QUICKSTART.md](./QUICKSTART.md)** - Quick start guide
- **[README.md](./README.md)** - Project overview
- **[src/web/README.md](./src/web/README.md)** - Web interface guide
- **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - System architecture

---

## 🎯 Next Steps

1. ✅ Run the application
2. 📤 Upload sample resumes and job descriptions
3. 🎨 Explore the interface
4. ⚙️ Adjust settings as needed
5. 📊 View analytics and results
6. 💾 Export results

---

## 💡 Tips

- Use sample data first to understand UI
- Adjust similarity thresholds based on your needs
- Export results regularly for backup
- Check logs for debugging: `tail -f logs/app.log`
- Use Docker for consistent environment

---

**Happy Resume Screening! 🎉**
