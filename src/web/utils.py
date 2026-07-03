"""
Streamlit utilities and helpers.
"""

import logging
from pathlib import Path

import streamlit as st


def setup_logging():
    """
    Configure logging for the Streamlit application.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def initialize_app():
    """
    Initialize the Streamlit application.
    """
    setup_logging()
    
    # Initialize session state
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.uploaded_files = []
        st.session_state.job_description = ""
        st.session_state.scoring_results = None
