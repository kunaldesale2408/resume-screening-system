#!/bin/bash
# Run Streamlit application

echo "🚀 Starting Resume Screening System - Streamlit Frontend"
echo ""
echo "📍 App running at: http://localhost:8501"
echo "📖 Press Ctrl+C to stop"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run Streamlit
streamlit run src/web/streamlit_app.py
