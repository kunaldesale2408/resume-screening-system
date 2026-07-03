"""
Pytest configuration and fixtures.
"""

import pytest


@pytest.fixture
def sample_resume():
    """Sample resume text for testing."""
    return """
    JOHN DOE
    Email: john@example.com | Phone: (555) 123-4567
    
    PROFESSIONAL SUMMARY
    Experienced Software Engineer with 5+ years in Python development and machine learning.
    
    EXPERIENCE
    Senior Python Developer - Tech Company (2021-Present)
    - Developed Python applications using FastAPI and Django
    - Implemented machine learning models using scikit-learn and TensorFlow
    - Led team of 3 developers
    
    Python Developer - StartUp Inc (2018-2021)
    - Built REST APIs using Flask and FastAPI
    - Implemented NLP solutions using spaCy and NLTK
    
    EDUCATION
    BS Computer Science - State University (2018)
    
    SKILLS
    Programming: Python, Java, JavaScript, SQL
    ML/AI: Machine Learning, NLP, TensorFlow, scikit-learn, spaCy
    Tools: Git, Docker, FastAPI, Streamlit
    """


@pytest.fixture
def sample_jd():
    """Sample job description for testing."""
    return """
    Senior Python Developer
    
    We are looking for a Senior Python Developer with strong experience in:
    - 5+ years of Python development
    - FastAPI and REST API development
    - Machine Learning and NLP experience
    - Docker and containerization
    - Team leadership experience
    
    Requirements:
    - Strong Python skills
    - Experience with scikit-learn, TensorFlow, or similar ML frameworks
    - Familiarity with spaCy for NLP
    - Git version control
    - Communication skills
    """


@pytest.fixture
def sample_jd_simple():
    """Simple job description for testing."""
    return """
    Junior Python Developer
    
    Requirements:
    - Python programming
    - SQL database knowledge
    """
