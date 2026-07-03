"""
Analytics page - Historical trends and statistics.
"""

import streamlit as st
from datetime import datetime, timedelta
import numpy as np


def render():
    """
    Render the Analytics page.
    """
    st.markdown('<div class="main-header">📈 Analytics</div>', unsafe_allow_html=True)
    st.markdown(
        "View historical statistics and trends of resume screening results."
    )

    # Analytics sections
    tab1, tab2, tab3 = st.tabs(
        ["📊 Historical Data", "🎯 Performance Trends", "📍 Common Patterns"]
    )

    with tab1:
        render_historical_data()

    with tab2:
        render_performance_trends()

    with tab3:
        render_common_patterns()


def render_historical_data():
    """
    Display historical data and statistics.
    """
    st.markdown("### Historical Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Screenings", "12", "+2 this week")

    with col2:
        st.metric("Avg Match Score", "72.4%", "-1.2%")

    with col3:
        st.metric("Total Resumes Scored", "147", "+23")

    with col4:
        st.metric("High Matches (>80%)", "34", "+5")

    # Date range selector
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30),
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
        )

    st.info(
        f"📅 Showing data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    )

    # Sample historical table
    historical_data = {
        "Date": [
            (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(10)
        ],
        "Screenings": np.random.randint(8, 15, 10),
        "Avg Score": [f"{np.random.uniform(0.65, 0.85):.1%}" for _ in range(10)],
        "High Matches": np.random.randint(2, 8, 10),
    }

    st.dataframe(historical_data, use_container_width=True, hide_index=True)


def render_performance_trends():
    """
    Display performance trend analysis.
    """
    st.markdown("### Performance Trends")

    # Placeholder chart data
    import plotly.graph_objects as go

    dates = [
        (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(30, 0, -1)
    ]
    avg_scores = np.random.uniform(0.65, 0.85, 30).cumsum() / np.arange(1, 31)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=avg_scores * 100,
            mode="lines+markers",
            name="Avg Score",
            line=dict(color="#1f77b4", width=2),
            fill="tozeroy",
        )
    )

    fig.update_layout(
        title="Average Match Score Trend (30 Days)",
        xaxis_title="Date",
        yaxis_title="Score (%)",
        hovermode="x unified",
        height=400,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_common_patterns():
    """
    Display common patterns and insights.
    """
    st.markdown("### Common Patterns & Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🏆 Top Matched Skills")
        top_skills = [
            ("Python", 0.89),
            ("Machine Learning", 0.82),
            ("Data Analysis", 0.78),
            ("SQL", 0.76),
            ("NLP", 0.73),
        ]

        for skill, match_rate in top_skills:
            st.write(f"{skill}: **{match_rate:.0%}** match rate")

    with col2:
        st.markdown("#### 📌 Common Requirements")
        common_reqs = [
            "3+ years experience",
            "Bachelor's degree",
            "Team player",
            "Problem-solving skills",
            "Communication skills",
        ]

        for req in common_reqs:
            st.write(f"✓ {req}")

    st.markdown("---")
    st.markdown("#### 💡 Recommendations")

    st.success(
        """
        - Candidates with strong **Python** skills have 89% match rate
        - **Machine Learning** experience is highly valued
        - Focus on **data analysis** competencies for higher matches
        """
    )
