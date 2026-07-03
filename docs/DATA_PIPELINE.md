# Data Acquisition & Preprocessing Pipeline

## Overview

The Data Acquisition & Preprocessing Pipeline is Section 2 of the Resume Screening System. It handles:

1. **Data Loading**: Kaggle dataset integration and file management
2. **PDF Extraction**: Text extraction from resume PDFs with OCR fallback
3. **Text Cleaning**: Comprehensive text preprocessing and normalization
4. **Pipeline Orchestration**: Full workflow coordination and statistics tracking

---

## Components

### 1. Data Loader (`src/data_loader.py`)

Manages dataset acquisition from Kaggle and local file loading.

**Key Features:**
- Automated Kaggle dataset download
- CSV and JSON file loading
- Train/test set creation (80/20 split)
- Sample data generation for development
- Dataset information reporting

**Usage:**
```python
from src.data_loader import KaggleDataLoader

loader = KaggleDataLoader()

# Download dataset
loader.download_dataset('elnahas/resume-dataset')

# Load CSV files
resumes_df = loader.load_resumes_csv('resumes.csv')
jds_df = loader.load_job_descriptions_csv('job_descriptions.csv')

# Create train/test split
train_df, test_df = loader.create_train_test_split(resumes_df, test_size=0.2)

# Get dataset info
info = loader.get_dataset_info()
print(info)  # Shows available files and sizes
```

### 2. PDF Extractor (`src/preprocessing/pdf_extractor.py`)

Extracts text from PDF files with multiple fallback methods.

**Extraction Methods (in order):**
1. **pdfplumber** - Fast digital PDF extraction
2. **PyPDF2** - Fallback for complex PDFs
3. **Tesseract OCR** - For scanned documents

**Features:**
- Automatic method selection
- OCR support for scanned PDFs
- Batch processing capability
- Comprehensive error handling

**Installation Requirements:**
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

**Usage:**
```python
from src.preprocessing.pdf_extractor import PDFExtractor

extractor = PDFExtractor(use_ocr=True)

# Extract from single PDF
text = extractor.extract_text('resume.pdf')

# Extract from multiple PDFs
pdf_files = ['resume1.pdf', 'resume2.pdf', 'resume3.pdf']
results = extractor.extract_from_multiple(pdf_files)
```

### 3. Text Cleaner (`src/preprocessing/text_cleaner.py`)

Comprehensive text preprocessing and normalization.

**Cleaning Steps:**
1. URL removal
2. Email address removal
3. Phone number removal
4. Special character removal
5. Lowercasing
6. Whitespace normalization
7. Tokenization
8. Stopword removal

**Features:**
- Configurable cleaning options
- Custom stopword support
- Domain-specific stopwords for resumes/JDs
- Multiple preprocessing pipelines

**Usage:**
```python
from src.preprocessing.text_cleaner import TextCleaner, clean_text

cleaner = TextCleaner(remove_stopwords=True)

# Clean text
text = "John Doe | Email: john@example.com | Phone: (555) 123-4567"
cleaned = cleaner.clean(text)
# Output: "john doe email john example com phone"

# Tokenize
tokens = cleaner.tokenize(cleaned)
# Output: ['john', 'doe', 'email', ...]

# Full pipeline
tokens = cleaner.process_full_pipeline(text)

# Convenience function
cleaned = clean_text(text, remove_stopwords=True)
```

### 4. Data Pipeline (`src/preprocessing/data_pipeline.py`)

Orchestrates the complete preprocessing workflow.

**Features:**
- End-to-end pipeline execution
- Dataframe processing (resumes and JDs)
- PDF batch processing
- Statistics tracking
- Intermediate results saving

**Usage:**
```python
from src.preprocessing.data_pipeline import DataPipeline
from src.data_loader import load_sample_datasets

pipeline = DataPipeline(
    use_ocr=True,
    remove_stopwords=True,
    save_intermediate=True
)

# Run full pipeline with sample data
processed_resumes, processed_jds = pipeline.run_full_pipeline(
    use_sample_data=True
)

# Get statistics
stats = pipeline.get_statistics()
print(stats)
# Output:
# {
#     'resumes_processed': 50,
#     'avg_resume_words': 187.5,
#     'jds_processed': 10,
#     'avg_jd_words': 234.2
# }
```

---

## Sample Data

Two sample datasets are included in `data/raw/`:

### `sample_resumes.csv`
Columns: `id`, `name`, `email`, `text`
- 3 sample resumes (easily extensible)
- Real-world resume content
- Multiple roles (Python Developer, Full Stack, ML Engineer)

### `sample_jds.csv`
Columns: `id`, `title`, `company`, `text`
- 3 sample job descriptions
- Multiple positions aligned with sample resumes
- Realistic requirements and qualifications

**Example Row:**
```csv
resume_001,John Doe,john@example.com,"John Doe
Senior Python Developer
Email: john@example.com...
EXPERIENCE
Senior Python Developer - Tech Company (2021-Present)
..."
```

---

## Workflow

```
┌──────────────────────────────────────────────┐
│  1. DATA ACQUISITION                         │
│  - Kaggle Dataset Download (optional)        │
│  - Load CSV/JSON files                       │
│  - Create train/test split (80/20)           │
└──────────┬───────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│  2. PDF EXTRACTION (if applicable)           │
│  - Try pdfplumber (digital PDFs)             │
│  - Fallback to PyPDF2                        │
│  - Fallback to OCR (scanned PDFs)            │
└──────────┬───────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│  3. TEXT CLEANING                            │
│  - Remove URLs, emails, phone numbers        │
│  - Remove special characters                 │
│  - Convert to lowercase                      │
│  - Normalize whitespace                      │
└──────────┬───────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│  4. TOKENIZATION & STOPWORD REMOVAL          │
│  - Word tokenization using NLTK              │
│  - Remove English stopwords                  │
│  - Remove domain-specific stopwords          │
│  - Filter by minimum token length            │
└──────────┬───────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│  5. STATISTICS & STORAGE                     │
│  - Calculate word/character counts           │
│  - Save processed data to CSV                │
│  - Log pipeline statistics                   │
└──────────────────────────────────────────────┘
```

---

## Configuration

Pipeline behavior is controlled via environment variables or `src/config.py`:

```python
# Text preprocessing
TFIDF_MAX_FEATURES = 5000
TFIDF_MIN_DF = 2
TFIDF_MAX_DF = 0.95
TFIDF_NGRAM_RANGE = (1, 2)

# Stopword removal
REMOVE_STOPWORDS = True

# OCR settings
USE_OCR = True
OCR_DPI = 200
```

---

## Testing

Run tests for the preprocessing module:

```bash
# Test text cleaning
pytest tests/test_preprocessing.py -v

# Test data loading
pytest tests/test_data_loader.py -v

# All preprocessing tests
pytest tests/test_preprocessing.py tests/test_data_loader.py -v --cov=src
```

---

## Output Files

Processed data is saved to `data/processed/`:

```
data/processed/
├── resumes_processed.csv       # Cleaned resumes with tokens
├── jds_processed.csv           # Cleaned job descriptions with tokens
├── resumes_train.csv           # 80% training set
├── resumes_test.csv            # 20% test set
└── pipeline_stats.json         # Processing statistics
```

**Output CSV Format:**
```csv
id,name,email,text,text_cleaned,tokens,word_count,char_count
resume_001,John Doe,john@example.com,"Original text...","cleaned text","['token1', 'token2'...]",187,1234
```

---

## Best Practices

1. **Always use OCR for scanned PDFs**: Set `use_ocr=True` if processing old resume scans
2. **Adjust stopword removal based on domain**: For technical roles, remove fewer technical terms
3. **Batch process PDFs**: Use `extract_from_multiple()` for efficiency
4. **Save intermediate results**: Enable `save_intermediate=True` for debugging
5. **Test on sample data first**: Use provided sample datasets before processing real data
6. **Monitor statistics**: Check output statistics to identify preprocessing issues

---

## Troubleshooting

### PDF Extraction Failing
```bash
# Install pdfplumber
pip install pdfplumber

# Install tesseract (Ubuntu)
sudo apt-get install tesseract-ocr
```

### NLTK Data Not Found
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

### Kaggle Authentication
```bash
# Create .kaggle/kaggle.json with your credentials
mkdir -p ~/.kaggle
echo '{"username": "your_username", "key": "your_key"}' > ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

---

## Next Steps (Section 3)

Once preprocessing is complete, proceed to **Section 3: NLP Feature Engineering** which will:
- Create TF-IDF vectors
- Extract entities using spaCy
- Combine features into final representation
