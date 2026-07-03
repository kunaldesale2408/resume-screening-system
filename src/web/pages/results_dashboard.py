"""
Results Dashboard page - View and analyze scored results.
"""

import streamlit as st
from src.web.components import (
    display_resume_card,
    create_score_comparison_chart,
    create_match_distribution_chart,
    show_export_options,
    display_no_results,
)


def render():
    """
    Render the Results Dashboard page.
    """
    st.markdown('<div class="main-header">📊 Results Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        "View detailed analysis of scored resumes with visualizations and match breakdowns."
    )

    # Check if results exist
    if not st.session_state.get("scoring_results"):
        display_no_results()
        return

    results = st.session_state.scoring_results

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Ranked Results", "📈 Charts", "📊 Statistics", "💾 Export"]
    )

    with tab1:
        render_ranked_results(results)

    with tab2:
        render_charts(results)

    with tab3:
        render_statistics(results)

    with tab4:
        render_export(results)


def render_ranked_results(results):
    """
    Display ranked resume results.

    Args:
        results: List of scored results
    """
    st.markdown("### Ranked Candidates")

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        min_score = st.slider(
            "Minimum score:",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.05,
            format="%.0%",
        )

    with col2:
        sort_by = st.selectbox(
            "Sort by:",
            ["Overall Score", "TF-IDF Score", "Entity Score"],
        )

    with col3:
        show_count = st.number_input(
            "Show top N:",
            min_value=1,
            max_value=len(results),
            value=min(10, len(results)),
        )

    # Filter results
    filtered_results = [
        r for r in results if r["overall_score"] >= min_score
    ]

    # Sort results
    sort_key = {
        "Overall Score": "overall_score",
        "TF-IDF Score": "tfidf_score",
        "Entity Score": "entity_score",
    }[sort_by]
    filtered_results.sort(key=lambda x: x[sort_key], reverse=True)

    # Display top N
    filtered_results = filtered_results[:show_count]

    if not filtered_results:
        st.info("No results match the selected filters.")
        return

    for idx, result in enumerate(filtered_results, 1):
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


def render_charts(results):
    """
    Display visualization charts.

    Args:
        results: List of scored results
    """
    st.markdown("### Visualizations")

    col1, col2 = st.columns(2)

    with col1:
        create_score_comparison_chart(results)

    with col2:
        create_match_distribution_chart(results)


def render_statistics(results):
    """
    Display statistical summary.

    Args:
        results: List of scored results
    """
    st.markdown("### Statistical Summary")

    overall_scores = [r["overall_score"] for r in results]
    tfidf_scores = [r["tfidf_score"] for r in results]
    entity_scores = [r["entity_score"] for r in results]

    import numpy as np

    stats_data = {
        "Metric": [
            "Mean",
            "Median",
            "Std Dev",
            "Min",
            "Max",
        ],
        "Overall Score": [
            f"{np.mean(overall_scores):.2%}",
            f"{np.median(overall_scores):.2%}",
            f"{np.std(overall_scores):.2%}",
            f"{np.min(overall_scores):.2%}",
            f"{np.max(overall_scores):.2%}",
        ],
        "TF-IDF Score": [
            f"{np.mean(tfidf_scores):.2%}",
            f"{np.median(tfidf_scores):.2%}",
            f"{np.std(tfidf_scores):.2%}",
            f"{np.min(tfidf_scores):.2%}",
            f"{np.max(tfidf_scores):.2%}",
        ],
        "Entity Score": [
            f"{np.mean(entity_scores):.2%}",
            f"{np.median(entity_scores):.2%}",
            f"{np.std(entity_scores):.2%}",
            f"{np.min(entity_scores):.2%}",
            f"{np.max(entity_scores):.2%}",
        ],
    }

    st.dataframe(stats_data, use_container_width=True, hide_index=True)


def render_export(results):
    """
    Display export options.

    Args:
        results: List of scored results
    """
    st.markdown("### Export Results")
    show_export_options(results, st.session_state.job_description)
