"""
Resume card display component for showing matched results.
"""

from typing import Dict, List, Optional

import streamlit as st


def display_resume_card(
    rank: int,
    filename: str,
    overall_score: float,
    tfidf_score: float,
    entity_score: float,
    matched_skills: List[str],
    matched_keywords: List[str],
    candidate_name: Optional[str] = None,
) -> None:
    """
    Display a formatted resume match card.
    
    Args:
        rank: Ranking position
        filename: Resume filename
        overall_score: Overall match score (0-1)
        tfidf_score: TF-IDF similarity score (0-1)
        entity_score: Entity matching score (0-1)
        matched_skills: List of matched skills
        matched_keywords: List of matched keywords
        candidate_name: Optional candidate name
    """
    # Determine match quality
    if overall_score >= 0.8:
        match_class = "high-match"
        match_emoji = "🟢"
    elif overall_score >= 0.6:
        match_class = "medium-match"
        match_emoji = "🟡"
    else:
        match_class = "low-match"
        match_emoji = "🔴"
    
    # Create card container
    with st.container():
        st.markdown(
            f"""
            <div class="match-card {match_class}">
            """,
            unsafe_allow_html=True,
        )
        
        # Header with rank and score
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            st.markdown(f"### #{rank}")
        
        with col2:
            if candidate_name:
                st.markdown(f"**{candidate_name}**")
            st.caption(filename)
        
        with col3:
            st.metric(f"{match_emoji} Match Score", f"{overall_score:.1%}")
        
        # Score breakdown
        st.markdown("---")
        breakdown_col1, breakdown_col2 = st.columns(2)
        
        with breakdown_col1:
            st.metric("TF-IDF Match", f"{tfidf_score:.1%}")
        
        with breakdown_col2:
            st.metric("Entity Match", f"{entity_score:.1%}")
        
        # Matched skills and keywords
        if matched_skills:
            st.markdown("**🎯 Matched Skills:**")
            skill_badges = " ".join([f"🏷️ `{skill}`" for skill in matched_skills[:5]])
            st.markdown(skill_badges)
            if len(matched_skills) > 5:
                st.caption(f"... and {len(matched_skills) - 5} more")
        
        if matched_keywords:
            st.markdown("**📍 Matched Keywords:**")
            keyword_badges = " ".join([f"`{kw}`" for kw in matched_keywords[:8]])
            st.markdown(keyword_badges)
            if len(matched_keywords) > 8:
                st.caption(f"... and {len(matched_keywords) - 8} more")
        
        st.markdown("</div>", unsafe_allow_html=True)


def display_results_table(results: List[Dict]) -> None:
    """
    Display results in a table format.
    
    Args:
        results: List of result dictionaries with scoring information
    """
    st.markdown("### 📊 Results Summary")
    
    # Prepare data for display
    display_data = []
    for idx, result in enumerate(results, 1):
        display_data.append({
            "Rank": idx,
            "Filename": result.get("filename", "Unknown"),
            "Overall Score": f"{result.get('overall_score', 0):.1%}",
            "TF-IDF": f"{result.get('tfidf_score', 0):.1%}",
            "Entity": f"{result.get('entity_score', 0):.1%}",
            "Skills Matched": len(result.get("matched_skills", [])),
        })
    
    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
    )


def display_no_results() -> None:
    """
    Display message when no results are available.
    """
    st.info(
        """
        📭 No results available yet.
        
        Please:
        1. Upload resume PDF(s)
        2. Provide job description
        3. Click "Score Resumes" to process
        """
    )
