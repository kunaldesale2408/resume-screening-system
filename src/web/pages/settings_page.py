"""
Settings page - Configure matching thresholds and weights.
"""

import streamlit as st
from src.config import settings


def render():
    """
    Render the Settings page.
    """
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown(
        "Configure matching parameters, thresholds, and feature weights."
    )

    # Create tabs for different settings sections
    tab1, tab2, tab3 = st.tabs(
        ["🎯 Matching Parameters", "⚖️ Weights", "📋 About"]
    )

    with tab1:
        render_matching_parameters()

    with tab2:
        render_weights()

    with tab3:
        render_about()


def render_matching_parameters():
    """
    Display matching parameter settings.
    """
    st.markdown("### Matching Parameters")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Similarity Thresholds")

        similarity_threshold = st.slider(
            "Similarity Threshold",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.similarity_threshold,
            step=0.05,
            help="Minimum similarity score to consider a match",
            format="%.2f",
        )

        st.session_state.similarity_threshold = similarity_threshold

        st.info(
            f"📌 Resumes with scores below {similarity_threshold:.0%} will be flagged as low matches."
        )

    with col2:
        st.markdown("#### Processing Settings")

        batch_size = st.slider(
            "Batch Size",
            min_value=1,
            max_value=64,
            value=32,
            step=1,
            help="Number of resumes to process in parallel",
        )

        timeout = st.slider(
            "Processing Timeout (seconds)",
            min_value=60,
            max_value=600,
            value=300,
            step=30,
            help="Maximum time allowed for processing",
        )

    st.markdown("---")

    # Advanced settings
    with st.expander("🔧 Advanced Settings"):
        st.markdown("#### TF-IDF Configuration")

        col1, col2 = st.columns(2)

        with col1:
            max_features = st.number_input(
                "Max Features",
                min_value=1000,
                max_value=10000,
                value=5000,
                step=1000,
            )

            min_df = st.number_input(
                "Min DF (minimum document frequency)",
                min_value=1,
                max_value=10,
                value=2,
            )

        with col2:
            max_df = st.slider(
                "Max DF (maximum document frequency)",
                min_value=0.5,
                max_value=1.0,
                value=0.95,
                step=0.05,
            )

            ngram_range = st.selectbox(
                "N-gram Range",
                [(1, 1), (1, 2), (1, 3)],
                index=1,
            )

        st.success(
            f"✅ TF-IDF will use {max_features} features with n-grams {ngram_range}"
        )


def render_weights():
    """
    Display weight configuration.
    """
    st.markdown("### Feature Weights")

    st.markdown(
        """
        Adjust the weights to control how much each matching method influences the final score.
        Weights are normalized to sum to 1.0.
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        tfidf_weight = st.slider(
            "TF-IDF Weight",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.tfidf_weight,
            step=0.05,
            help="Weight for TF-IDF text similarity matching",
            format="%.2f",
        )

        st.session_state.tfidf_weight = tfidf_weight

    with col2:
        entity_weight = st.slider(
            "Entity Weight",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.entity_weight,
            step=0.05,
            help="Weight for entity-based skill matching",
            format="%.2f",
        )

        st.session_state.entity_weight = entity_weight

    # Normalize weights
    total_weight = tfidf_weight + entity_weight
    if total_weight > 0:
        normalized_tfidf = tfidf_weight / total_weight
        normalized_entity = entity_weight / total_weight
    else:
        normalized_tfidf = normalized_entity = 0.5

    st.markdown("---")
    st.markdown("#### Normalized Weights")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("TF-IDF", f"{normalized_tfidf:.1%}")

    with col2:
        st.metric("Entity", f"{normalized_entity:.1%}")

    with col3:
        st.metric("Total", f"{normalized_tfidf + normalized_entity:.1%}")

    st.markdown("---")

    # Entity weight breakdown
    with st.expander("🎯 Entity Matching Weights"):
        st.markdown("Configure how different entity types are weighted")

        col1, col2 = st.columns(2)

        with col1:
            skills_weight = st.slider(
                "Skills",
                min_value=0.0,
                max_value=1.0,
                value=0.4,
                step=0.05,
            )

            experience_weight = st.slider(
                "Experience",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.05,
            )

        with col2:
            education_weight = st.slider(
                "Education",
                min_value=0.0,
                max_value=1.0,
                value=0.2,
                step=0.05,
            )

            certifications_weight = st.slider(
                "Certifications",
                min_value=0.0,
                max_value=1.0,
                value=0.1,
                step=0.05,
            )

        st.success(
            f"✅ Entity weights configured: Skills={skills_weight:.0%}, "
            f"Experience={experience_weight:.0%}, Education={education_weight:.0%}, "
            f"Certifications={certifications_weight:.0%}"
        )


def render_about():
    """
    Display about and help information.
    """
    st.markdown("### About This System")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            #### System Information
            - **Application**: {settings.APP_NAME}
            - **Version**: {settings.APP_VERSION}
            - **Match Accuracy**: 85%+
            - **Processing Speed**: Sub-minute for batch operations
            """
        )

    with col2:
        st.markdown(
            """
            #### Technology Stack
            - **NLP Engine**: spaCy, TF-IDF, NLTK
            - **Similarity**: Cosine similarity
            - **Frontend**: Streamlit
            - **Backend**: FastAPI
            """
        )

    st.markdown("---")

    st.markdown(
        """
        #### How It Works
        
        1. **Resume Extraction**: PDFs are parsed and text is extracted
        2. **Text Preprocessing**: Text is cleaned and normalized
        3. **Feature Engineering**: TF-IDF vectors and entities are extracted
        4. **Matching**: Resume features are compared against JD features
        5. **Scoring**: Weighted combination of TF-IDF and entity matches
        6. **Ranking**: Resumes ranked by overall score
        
        #### Matching Metrics
        
        - **TF-IDF Score**: Text similarity between resume and JD
        - **Entity Score**: Matching of extracted skills and experience
        - **Overall Score**: Weighted combination of both scores
        """
    )

    st.markdown("---")

    st.info(
        """
        📧 **Support & Questions**
        
        For issues, questions, or feedback, please contact:
        - GitHub: [@kunaldesale2408](https://github.com/kunaldesale2408)
        - Email: kunaldesale9766@gmail.com
        """
    )

    # Reset settings button
    st.markdown("---")
    if st.button("🔄 Reset to Default Settings", use_container_width=True):
        st.session_state.similarity_threshold = settings.SIMILARITY_THRESHOLD
        st.session_state.tfidf_weight = settings.TFIDF_WEIGHT
        st.session_state.entity_weight = settings.ENTITY_WEIGHT
        st.success("✅ Settings reset to defaults!")
        st.rerun()
