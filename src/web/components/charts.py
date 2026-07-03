"""
Data visualization components using Plotly and Matplotlib.
"""

from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def create_score_comparison_chart(results: List[Dict]) -> None:
    """
    Create a bar chart comparing match scores.
    
    Args:
        results: List of result dictionaries
    """
    if not results:
        st.info("No data available for visualization")
        return
    
    filenames = [r.get("filename", f"Resume {i}").replace(".pdf", "") for i, r in enumerate(results)]
    overall_scores = [r.get("overall_score", 0) * 100 for r in results]
    tfidf_scores = [r.get("tfidf_score", 0) * 100 for r in results]
    entity_scores = [r.get("entity_score", 0) * 100 for r in results]
    
    # Create figure
    fig = go.Figure(
        data=[
            go.Bar(name="Overall Score", x=filenames, y=overall_scores),
            go.Bar(name="TF-IDF Score", x=filenames, y=tfidf_scores),
            go.Bar(name="Entity Score", x=filenames, y=entity_scores),
        ]
    )
    
    fig.update_layout(
        title="📊 Match Score Comparison",
        xaxis_title="Resume",
        yaxis_title="Score (%)",
        barmode="group",
        hovermode="x unified",
        height=400,
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_match_distribution_chart(results: List[Dict]) -> None:
    """
    Create a distribution chart of match scores.
    
    Args:
        results: List of result dictionaries
    """
    if not results:
        st.info("No data available for visualization")
        return
    
    overall_scores = [r.get("overall_score", 0) * 100 for r in results]
    
    # Create histogram
    fig = px.histogram(
        x=overall_scores,
        nbins=10,
        title="📈 Match Score Distribution",
        labels={"x": "Match Score (%)", "count": "Frequency"},
        color_discrete_sequence=["#1f77b4"],
    )
    
    # Add mean line
    mean_score = np.mean(overall_scores)
    fig.add_vline(
        x=mean_score,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: {mean_score:.1f}%",
        annotation_position="top right",
    )
    
    fig.update_layout(height=400, showlegend=False)
    
    st.plotly_chart(fig, use_container_width=True)


def create_skills_heatmap(skills_matrix: Dict[str, Dict[str, float]]) -> None:
    """
    Create a heatmap of skill matches across resumes.
    
    Args:
        skills_matrix: Dictionary with structure {resume_name: {skill: match_score}}
    """
    if not skills_matrix:
        st.info("No skill data available for visualization")
        return
    
    # Prepare data
    resumes = list(skills_matrix.keys())
    all_skills = set()
    for skills in skills_matrix.values():
        all_skills.update(skills.keys())
    
    all_skills = sorted(list(all_skills))[:15]  # Limit to top 15 skills
    
    # Create matrix
    data = []
    for skill in all_skills:
        row = [skills_matrix.get(resume, {}).get(skill, 0) * 100 for resume in resumes]
        data.append(row)
    
    # Create heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=data,
            x=resumes,
            y=all_skills,
            colorscale="Blues",
            text=np.array(data).round(1),
            texttemplate="%{text:.0f}%",
            textfont={"size": 10},
        )
    )
    
    fig.update_layout(
        title="🔥 Skill Match Heatmap",
        xaxis_title="Resume",
        yaxis_title="Skill",
        height=500,
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_timeline_chart(historical_data: List[Dict]) -> None:
    """
    Create a line chart showing score trends over time.
    
    Args:
        historical_data: List of historical results with timestamps
    """
    if not historical_data:
        st.info("No historical data available")
        return
    
    # Extract data
    timestamps = [d.get("timestamp", "") for d in historical_data]
    avg_scores = [d.get("avg_score", 0) * 100 for d in historical_data]
    max_scores = [d.get("max_score", 0) * 100 for d in historical_data]
    
    # Create figure
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=avg_scores,
            mode="lines+markers",
            name="Average Score",
            line=dict(color="#1f77b4", width=2),
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=max_scores,
            mode="lines+markers",
            name="Max Score",
            line=dict(color="#ff7f0e", width=2),
        )
    )
    
    fig.update_layout(
        title="📈 Score Trends Over Time",
        xaxis_title="Date",
        yaxis_title="Score (%)",
        hovermode="x unified",
        height=400,
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_metric_cards(stats: Dict[str, float]) -> None:
    """
    Display key metrics in card format.
    
    Args:
        stats: Dictionary of statistics to display
    """
    cols = st.columns(len(stats))
    
    for col, (label, value) in zip(cols, stats.items()):
        with col:
            st.metric(label, f"{value:.1%}" if value < 2 else f"{value:.1f}")
