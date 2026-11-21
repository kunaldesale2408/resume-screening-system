"""
Analytics page - statistics across the screenings run in this session.

Everything here is computed from real scoring results stored in
st.session_state; nothing is simulated.
"""

from collections import Counter

import pandas as pd
import streamlit as st


def render():
    """
    Render the Analytics page.
    """
    st.markdown('<div class="main-header">📈 Analytics</div>', unsafe_allow_html=True)
    st.markdown("Statistics across the screenings you've run in this session.")

    history = st.session_state.get("screening_history", [])
    if not history:
        st.info(
            "📭 No screenings yet. Score some resumes on the **Upload & Score** page "
            "and the statistics will appear here."
        )
        return

    all_results = [r for run in history for r in run["results"]]

    tab1, tab2 = st.tabs(["📊 Overview", "📍 Skills"])
    with tab1:
        render_overview(history, all_results)
    with tab2:
        render_skills(all_results)


def render_overview(history, all_results):
    col1, col2, col3, col4 = st.columns(4)
    scores = [r["overall_score"] for r in all_results]
    with col1:
        st.metric("Screenings", len(history))
    with col2:
        st.metric("Resumes Scored", len(all_results))
    with col3:
        st.metric("Avg Match Score", f"{sum(scores) / len(scores):.1%}")
    with col4:
        strong = sum(1 for r in all_results if r.get("recommendation") == "Strong match")
        st.metric("Strong Matches", strong)

    rows = []
    for i, run in enumerate(history, 1):
        run_scores = [r["overall_score"] for r in run["results"]]
        rows.append(
            {
                "Screening": i,
                "Resumes": len(run_scores),
                "Avg Score": f"{sum(run_scores) / len(run_scores):.1%}",
                "Best Score": f"{max(run_scores):.1%}",
                "Strong Matches": sum(1 for r in run["results"] if r.get("recommendation") == "Strong match"),
                "Time (s)": round(run["processing_ms"] / 1000, 2),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_skills(all_results):
    col1, col2 = st.columns(2)
    matched = Counter(s for r in all_results for s in r.get("matched_skills", []))
    missing = Counter(s for r in all_results for s in r.get("missing_skills", []))

    with col1:
        st.markdown("#### 🏆 Most common matched skills")
        if matched:
            st.bar_chart(pd.Series(dict(matched.most_common(10))))
        else:
            st.caption("No matched skills yet.")

    with col2:
        st.markdown("#### ⚠️ Most common missing requirements")
        if missing:
            st.bar_chart(pd.Series(dict(missing.most_common(10))))
        else:
            st.caption("No missing requirements.")
