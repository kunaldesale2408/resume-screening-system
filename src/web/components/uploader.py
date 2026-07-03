"""
File upload handlers for PDF and text inputs.
"""

import io
from typing import List, Optional, Tuple

import streamlit as st

from src.config import settings


def upload_pdf_files() -> Optional[List[Tuple[str, bytes]]]:
    """
    Handle batch upload of PDF resume files.
    
    Returns:
        List of tuples (filename, file_bytes) or None if no files uploaded
    """
    st.subheader("📤 Upload Resumes")
    
    uploaded_files = st.file_uploader(
        "Upload PDF resume(s)",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or more PDF resume files for batch processing",
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
        
        # Display file preview
        with st.expander("📋 View uploaded files"):
            for file in uploaded_files:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(file.name)
                with col2:
                    st.caption(f"{file.size / 1024:.1f} KB")
        
        # Return files as list of tuples
        return [(file.name, file.getvalue()) for file in uploaded_files]
    
    return None


def upload_text_jd() -> Optional[str]:
    """
    Handle job description input (text or file).
    
    Returns:
        Job description text or None
    """
    st.subheader("📋 Job Description")
    
    input_method = st.radio(
        "How would you like to provide the job description?",
        ["📝 Paste Text", "📄 Upload File"],
        horizontal=True,
    )
    
    jd_text = None
    
    if input_method == "📝 Paste Text":
        jd_text = st.text_area(
            "Paste job description here:",
            height=150,
            placeholder="Enter job description text...",
            help="Paste the full job description including responsibilities, requirements, etc.",
        )
    
    else:  # Upload File
        jd_file = st.file_uploader(
            "Upload job description file",
            type=["txt", "pdf"],
            help="Upload a TXT or PDF file containing the job description",
        )
        
        if jd_file:
            if jd_file.type == "text/plain":
                jd_text = jd_file.getvalue().decode("utf-8")
            elif jd_file.type == "application/pdf":
                try:
                    import pdfplumber
                    
                    with pdfplumber.open(io.BytesIO(jd_file.getvalue())) as pdf:
                        jd_text = "".join([page.extract_text() for page in pdf.pages])
                except Exception as e:
                    st.error(f"❌ Error reading PDF: {str(e)}")
                    return None
    
    # Show preview
    if jd_text:
        with st.expander("👁️ Preview job description"):
            st.text(jd_text[:500] + "..." if len(jd_text) > 500 else jd_text)
    
    return jd_text if jd_text and jd_text.strip() else None


def show_sample_inputs():
    """
    Display sample job description and resume for testing.
    """
    with st.expander("📚 Load Sample Data", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Load Sample Job Description", use_container_width=True):
                try:
                    sample_jd_path = "assets/sample_jd.txt"
                    with open(sample_jd_path, "r") as f:
                        st.session_state.job_description = f.read()
                    st.success("✅ Sample JD loaded!")
                except FileNotFoundError:
                    st.info("📝 Sample JD file not found. You can create one at assets/sample_jd.txt")
        
        with col2:
            if st.button("📄 Load Sample Resume", use_container_width=True):
                st.info("💡 Upload sample resume from assets/sample_resume.pdf")
