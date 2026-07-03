#!/bin/bash
# Setup script for Resume Screening System

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════════"
echo "   Resume Screening System - Setup Script"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check Python version
echo "📋 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' || echo "")
echo "✓ Python $PYTHON_VERSION"

if [[ ! $PYTHON_VERSION =~ ^3\.(10|11|12) ]]; then
    echo "⚠️  Warning: Python 3.10+ recommended, found $PYTHON_VERSION"
fi

echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "🚀 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel -q
echo "✓ pip upgraded"

echo ""

# Install dependencies
echo "📚 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
    echo "✓ Dependencies installed"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

echo ""

# Download spaCy model
echo "🧠 Downloading spaCy language model..."
python -m spacy download en_core_web_sm -q 2>/dev/null || true
echo "✓ spaCy model ready"

echo ""

# Setup environment file
echo "🔐 Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ .env file created from template"
    else
        echo "⚠️  .env.example not found, skipping .env setup"
    fi
else
    echo "✓ .env file already exists"
fi

echo ""

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/raw data/processed models logs assets
echo "✓ Directories created"

echo ""

# Setup streamlit config
echo "⚙️  Setting up Streamlit configuration..."
mkdir -p .streamlit
echo "✓ .streamlit directory ready"

echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "   ✅ Setup Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📖 Next Steps:"
echo ""
echo "   1. Activate virtual environment (if not already):"
echo "      source venv/bin/activate"
echo ""
echo "   2. Run the Streamlit application:"
echo "      streamlit run src/web/streamlit_app.py"
echo ""
echo "   3. Or run with Makefile:"
echo "      make run-frontend"
echo ""
echo "   4. Application opens at: http://localhost:8501"
echo ""
echo "   For more info, see: QUICKSTART.md"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
