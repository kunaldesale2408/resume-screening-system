# System Architecture

## Overview

The AI-Powered Resume Screening System follows a modular, layered architecture designed for scalability, maintainability, and extensibility.

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌──────────────────────┐           ┌──────────────────┐   │
│  │  Streamlit Web App   │           │  API Documentation│   │
│  │  - Upload UI         │           │  - Swagger/OpenAPI │   │
│  │  - Results Dashboard │           │                   │   │
│  │  - Analytics         │           │                   │   │
│  └──────────────────────┘           └──────────────────┘   │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
│  ┌─────────────────┐         ┌────────────────────────┐    │
│  │ /score          │         │ /batch_score           │    │
│  │ /health         │         │ /resume/{id}           │    │
│  │ /config         │         │ /jd/{id}               │    │
│  └─────────────────┘         └────────────────────────┘    │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                 Business Logic Layer                         │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ Preprocessing   │  │  Feature     │  │  Matching &    │ │
│  │ Service         │  │  Engineering │  │  Scoring       │ │
│  │                 │  │  Service     │  │  Service       │ │
│  └─────────────────┘  └──────────────┘  └────────────────┘ │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              Core Processing Layer                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐ │
│  │PDF Text  │ │Text      │ │TF-IDF    │ │Entity         │ │
│  │Extraction│ │Cleaning  │ │Vectorizer│ │Extraction     │ │
│  └──────────┘ └──────────┘ └──────────┘ │(spaCy)        │ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ └───────────────┘ │
│  │Tokenizer │ │Lemmatizer│ │Similarity│ ┌───────────────┐ │
│  │          │ │          │ │Calculator│ │Entity Matcher │ │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘ │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                Data Layer                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │Raw Data        │  │Processed Data  │  │Models        │ │
│  │- Kaggle        │  │- Cleaned Text  │  │- TF-IDF      │ │
│  │  Resumes       │  │- Vectors       │  │- spaCy Model │ │
│  │- Job Descs     │  │- Features      │  │- Metrics     │ │
│  └────────────────┘  └────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Layer
- **Raw Data**: Kaggle datasets (resumes, job descriptions)
- **Processed Data**: Cleaned text, vectorized features
- **Models**: Trained TF-IDF vectorizer, spaCy model, validation metrics

### 2. Core Processing Layer
- **PDF Extraction**: `pdf_extractor.py` - Extracts text from PDFs
- **Text Cleaning**: `text_cleaner.py` - Tokenization, lowercasing, stopword removal
- **TF-IDF Vectorization**: Creates numerical representations of text
- **Entity Extraction**: spaCy-based entity recognition (skills, experience, etc.)
- **Similarity Calculation**: Cosine similarity between resume and JD vectors
- **Entity Matching**: Matches extracted entities between documents

### 3. Business Logic Layer
- **Preprocessing Service**: Orchestrates text extraction and cleaning
- **Feature Engineering Service**: Combines TF-IDF and entity features
- **Matching & Scoring Service**: Calculates final match scores

### 4. API Layer (FastAPI)
- RESTful endpoints for scoring, batch processing, health checks
- Input validation using Pydantic models
- Async processing for scalability
- OpenAPI documentation

### 5. User Interface Layer
- **Streamlit Web App**: Interactive dashboard for resume upload and scoring visualization
- **API Documentation**: Auto-generated Swagger/OpenAPI docs

## Data Flow

```
User Input (Resume + JD)
        ↓
   PDF Extraction
        ↓
   Text Cleaning
        ↓
   Tokenization & Lemmatization
        ↓
   TF-IDF Vectorization
        ↓
   Entity Extraction (spaCy)
        ↓
   Similarity Calculation (Cosine)
        ↓
   Entity Matching
        ↓
   Score Combination & Ranking
        ↓
   Output (Match Score + Details)
```

## Deployment Architecture

```
┌─────────────────────────────────────────────┐
│          Docker Compose Environment          │
│  ┌──────────────────────────────────────┐   │
│  │         Frontend Container            │   │
│  │  Streamlit (Port 8501)                │   │
│  │  - Web Application                    │   │
│  │  - User Interface                     │   │
│  └──────────────────────────────────────┘   │
│                    │                         │
│                    ↓                         │
│  ┌──────────────────────────────────────┐   │
│  │         Backend Container             │   │
│  │  FastAPI (Port 8000)                  │   │
│  │  - REST API Endpoints                 │   │
│  │  - Business Logic                     │   │
│  └──────────────────────────────────────┘   │
│                    │                         │
│                    ↓                         │
│  ┌──────────────────────────────────────┐   │
│  │         Data & Models Volume          │   │
│  │  - Kaggle Datasets                    │   │
│  │  - Trained Models                     │   │
│  │  - Processed Data                     │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

## Key Design Patterns

1. **Singleton Pattern**: TF-IDF vectorizer and spaCy model are loaded once and reused
2. **Service Layer Pattern**: Business logic separated into dedicated services
3. **Factory Pattern**: Document processors (PDF, TXT, DOCX) created based on file type
4. **Observer Pattern**: Logging and monitoring of processing pipeline
5. **Pipeline Pattern**: Sequential processing of resumes and JDs

## Scalability Considerations

- **Async Processing**: FastAPI supports concurrent requests
- **Batch Processing**: Multiple resumes scored simultaneously
- **Caching**: Vectorizers and models cached to avoid recomputation
- **Containerization**: Docker enables horizontal scaling
- **Resource Management**: Configurable batch size and worker count

## Security Features

- **CORS Configuration**: Controlled cross-origin requests
- **Input Validation**: Pydantic schemas validate all inputs
- **Environment Variables**: Sensitive config stored in .env
- **Error Handling**: Comprehensive error messages without exposing internals
- **Rate Limiting**: Planned for production deployment
