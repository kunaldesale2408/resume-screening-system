"""
Upload & Score page - Main scoring interface.
"""

import io
from typing import List, Tuple

import streamlit as st
from src.config import settings
from src.web.components import (
    display_resume_card,
    upload_pdf_files,
    upload_text_jd,
    show_export_options,
)


def render():
    """
    Render the Upload & Score page.
    """
    st.markdown('<div class="main-header">📤 Upload & Score Resumes</div>', unsafe_allow_html=True)
    st.markdown(
        "Upload resume PDFs and provide a job description to get match scores and ranking."
    )

    # Create two-column layout
    col_upload, col_jd = st.columns(2)

    with col_upload:
        uploaded_resumes = upload_pdf_files()
        if uploaded_resumes:
            st.session_state.uploaded_files = uploaded_resumes

    with col_jd:
        jd_text = upload_text_jd()
        if jd_text:
            st.session_state.job_description = jd_text

    # Scoring section
    st.markdown("<div class='section-header'>🎯 Score Resumes</div>", unsafe_allow_html=True)

    # Check prerequisites
    if not st.session_state.uploaded_files or not st.session_state.job_description:
        st.warning(
            "⚠️ Please upload resume(s) and provide job description to proceed."
        )
        return

    # Scoring controls
    col1, col2, col3 = st.columns(3)

    with col1:
        process_button = st.button(
            "🚀 Score Resumes",
            key="score_button",
            use_container_width=True,
            type="primary",
        )

    with col2:
        st.info(f"📋 Resumes: {len(st.session_state.uploaded_files)}")

    with col3:
        st.info(f"📝 JD Length: {len(st.session_state.job_description)} chars")

    # Process resumes when button clicked
    if process_button:
        score_resumes()

    # Display results if available
    if st.session_state.get("scoring_results"):
        display_scoring_results(st.session_state.scoring_results)


def score_resumes():
    """
    Process uploaded resumes and calculate match scores.
    """
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Placeholder for actual scoring logic
        # In production, this would call the matching engine

        results = []
        total_files = len(st.session_state.uploaded_files)

        for idx, (filename, file_bytes) in enumerate(st.session_state.uploaded_files):
            progress = (idx + 1) / total_files
            progress_bar.progress(progress)
            status_text.text(f"Processing {idx + 1}/{total_files}: {filename}...")

            # Placeholder scores (replace with actual scoring)
            overall_score = 0.75 + (idx * 0.05)
            tfidf_score = 0.70 + (idx * 0.04)
            entity_score = 0.80 + (idx * 0.03)

            result = {
                "filename": filename,
                "overall_score": min(overall_score, 1.0),
                "tfidf_score": min(tfidf_score, 1.0),
                "entity_score": min(entity_score, 1.0),
                "matched_skills": ["Python", "Machine Learning", "NLP"],
                "matched_keywords": ["AI", "resume screening", "ranking"],
                "candidate_name": filename.replace(".pdf", ""),
            }
            results.append(result)

        # Sort by overall score
        results.sort(key=lambda x: x["overall_score"], reverse=True)

        st.session_state.scoring_results = results
        status_text.empty()
        progress_bar.empty()

        st.success(f"✅ Scored {total_files} resume(s)!")

    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Error during scoring: {str(e)}")
        st.session_state.scoring_results = None


def display_scoring_results(results: List[dict]):
    """
    Display scored results.

    Args:
        results: List of scored resume results
    """
    st.markdown("<div class='section-header'>📊 Scoring Results</div>", unsafe_allow_html=True)

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Resumes", len(results))
    with col2:
        avg_score = sum(r["overall_score"] for r in results) / len(results)
        st.metric("Avg Score", f"{avg_score:.1%}")
    with col3:
        max_score = max(r["overall_score"] for r in results)
        st.metric("Best Match", f"{max_score:.1%}")
    with col4:
        min_score = min(r["overall_score"] for r in results)
        st.metric("Lowest Match", f"{min_score:.1%}")

    st.markdown("---")

    # Display each result as a card
    for idx, result in enumerate(results, 1):
        display_resume_card(
            rank=idx,
            filename=result["filename"],
            overall_score=result["overall_score"],
            tfidf_score=result["tfidf_score"],
            entity_score=result["entity_score"],
            matched_skills=result["matched_skills"],
            matched_keywords=result["matched_keywords"],
            candidate_name=result.get("candidate_name"),
        )

    # Export options
    show_export_options(results, st.session_state.job_description)
