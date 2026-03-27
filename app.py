"""Streamlit dashboard for the women fashion trend prediction project."""

from __future__ import annotations

import html

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from utils import (
    build_prediction_result,
    format_price,
    get_age_highlights,
    get_occasion_highlights,
    get_overview_metrics,
    get_sidebar_options,
    get_top_category_counts,
    load_dataset,
    load_model_if_available,
    load_model_summary,
)

DATASET_DISPLAY_PATH = "data/processed/fashion_trend_dataset.csv"
MODEL_DISPLAY_PATH = "models/model.pkl"

st.set_page_config(
    page_title="Women Fashion Trend Dashboard",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    """Light CSS for a clean, minimal layout."""
    st.markdown(
        """
        <style>
            .stApp {
                background: #f7f4ef;
            }
            [data-testid="stSidebar"] {
                background: #f3ede5;
                border-right: 1px solid rgba(98, 74, 61, 0.12);
            }
            .block-container {
                max-width: 1200px;
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            .hero-card, .soft-card, .metric-card {
                background: #fffdf9;
                border: 1px solid rgba(98, 74, 61, 0.10);
                border-radius: 20px;
                box-shadow: 0 10px 28px rgba(98, 74, 61, 0.06);
            }
            .hero-card {
                padding: 1.8rem 1.9rem;
                background: #fffdf9;
            }
            .soft-card {
                padding: 1.15rem 1.25rem;
            }
            .metric-card {
                min-height: 150px;
                padding: 1rem 1.1rem;
            }
            .eyebrow {
                text-transform: uppercase;
                letter-spacing: 0.14em;
                font-size: 0.75rem;
                color: #9d5d43;
                font-weight: 700;
                margin-bottom: 0.45rem;
            }
            .hero-title {
                font-size: clamp(2rem, 4vw, 3.8rem);
                line-height: 1.05;
                color: #2f221c;
                margin: 0 0 0.8rem 0;
            }
            .muted {
                color: #6b5b53;
                line-height: 1.7;
            }
            .metric-label {
                color: #7a665d;
                font-size: 0.9rem;
                margin-bottom: 0.4rem;
            }
            .metric-value {
                font-size: 1.9rem;
                font-weight: 700;
                color: #2f221c;
                margin-bottom: 0.5rem;
            }
            .result-chip {
                display: inline-block;
                padding: 0.4rem 0.8rem;
                margin-right: 0.45rem;
                margin-bottom: 0.45rem;
                border-radius: 999px;
                background: #f4e8dc;
                color: #734d39;
                font-size: 0.85rem;
                font-weight: 600;
            }
            .footer-note {
                padding: 1rem 0 0.25rem 0;
                color: #6f635d;
                font-size: 0.92rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, help_text: str) -> None:
    """Reusable metric block."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(label)}</div>
            <div class="metric-value">{html.escape(value)}</div>
            <div class="muted">{html.escape(help_text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    """Simple footer visible on every page."""
    st.markdown("---")
    st.markdown(
        """
        <div class="footer-note">
            Student project dashboard based on the processed dataset and exported notebook outputs.
        </div>
        """,
        unsafe_allow_html=True,
    )


def make_bar_chart(data: pd.DataFrame, category_col: str, value_col: str, title: str, color: str) -> plt.Figure:
    """Create a clean horizontal bar chart."""
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ordered = data.sort_values(value_col, ascending=True)
    ax.barh(ordered[category_col], ordered[value_col], color=color, edgecolor="none")
    ax.set_title(title, loc="left", fontsize=13, weight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x", alpha=0.18)
    ax.tick_params(axis="y", labelsize=10)
    ax.tick_params(axis="x", labelsize=9)
    fig.patch.set_facecolor("#fffdf9")
    ax.set_facecolor("#fffdf9")
    return fig


def render_product_cards(items: list[dict], section_title: str) -> None:
    """Display recommended items in a balanced grid."""
    st.subheader(section_title)
    columns = st.columns(min(len(items), 3) or 1, gap="large")

    for index, item in enumerate(items):
        column = columns[index % len(columns)]
        with column:
            with st.container(border=True):
                if item.get("image"):
                    st.image(item["image"], use_container_width=True)
                st.caption(item.get("brand", "Brand"))
                st.markdown(f"**{item.get('name', 'Fashion item')}**")
                st.markdown(
                    f"{format_price(item.get('price'))}  |  Rating {float(item.get('rating', 0)):.1f}"
                )
                st.caption(
                    f"Recommendation score: {float(item.get('recommendation_score', 0)) * 100:.1f}%"
                )
                tags = item.get("reason_tags", [])[:3]
                if tags:
                    st.markdown(
                        " ".join([f"<span class='result-chip'>{html.escape(str(tag))}</span>" for tag in tags]),
                        unsafe_allow_html=True,
                    )


def render_home(df: pd.DataFrame, summary: dict) -> None:
    """Overview page."""
    st.markdown(
        """
        <div class="hero-card">
            <div class="eyebrow">Women fashion trend project</div>
            <h1 class="hero-title">A simple dashboard for the project results.</h1>
            <p class="muted">
                This app brings the processed dataset, recommendation outputs, and model summary into one place.
                It is designed to be easy to explain in a student presentation.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    metric_columns = st.columns(4, gap="medium")
    for column, metric in zip(metric_columns, get_overview_metrics(df, summary)):
        with column:
            render_metric_card(metric["label"], metric["value"], metric["help"])

    left_col, right_col = st.columns([1.05, 0.95], gap="large")
    with left_col:
        st.markdown(
            """
            <div class="soft-card">
                <div class="eyebrow">Project snapshot</div>
                <h3 style="margin-top:0;">What this dashboard shows</h3>
                <p class="muted">
                    The dashboard shows the main outputs from the project in a cleaner format.
                </p>
                <ul class="muted">
                    <li>Inputs are based on age group, occasion, and clothing category.</li>
                    <li>Recommendations are taken from filtered project data.</li>
                    <li>Accuracy is shown for derived labels, not real customer labels.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right_col:
        top_categories = get_top_category_counts(df)
        fig = make_bar_chart(
            top_categories,
            "style_category",
            "count",
            "Top categories in the processed dataset",
            "#b56d4f",
        )
        st.pyplot(fig, use_container_width=True)


def render_prediction(result: dict) -> None:
    """Prediction page with cards, explanation, table, and chart."""
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="eyebrow">Trend prediction</div>
            <h2 style="margin-top:0;">Predicted trend match: {html.escape(result['predicted_category'])}</h2>
            <p class="muted">{html.escape(result['profile_summary'])}</p>
            <div>
                <span class="result-chip">Trend label: {html.escape(result['trend_label'])}</span>
                <span class="result-chip">Confidence: {result['confidence_score']:.1f}%</span>
                <span class="result-chip">Average rating: {result['average_rating']:.2f}</span>
                <span class="result-chip">Products reviewed: {result['product_count']}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(result["selection_note"])

    explanation_col, stats_col = st.columns([1.3, 0.7], gap="large")
    with explanation_col:
        st.markdown(
            f"""
            <div class="soft-card">
                <div class="eyebrow">Why this result appears</div>
                <p class="muted">{html.escape(result['explanation'])}</p>
                <p class="muted">
                    The dashboard first checks the selected filters. If there is no exact match, it uses the closest
                    available rows from the processed dataset.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with stats_col:
        st.markdown(
            f"""
            <div class="soft-card">
                <div class="eyebrow">Supporting numbers</div>
                <p><strong>Selected category:</strong> {html.escape(result['selected_category'])}</p>
                <p><strong>Profile trend score:</strong> {result['profile_trend_score']:.1f}%</p>
                <p><strong>Recommendation confidence:</strong> {result['confidence_score']:.1f}%</p>
                <p><strong>Top label in slice:</strong> {html.escape(result['trend_label'])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_product_cards(result["items"], "Recommended items")

    table_col, chart_col = st.columns([1.2, 0.8], gap="large")
    with table_col:
        st.subheader("Supporting table")
        display_df = result["support_table"].copy()
        display_df["Price"] = display_df["Price"].map(format_price)
        display_df["Recommendation Score"] = display_df["Recommendation Score"].map(lambda value: f"{float(value) * 100:.1f}%")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    with chart_col:
        st.subheader("Top item scores")
        chart_data = result["chart_table"].copy()
        fig = make_bar_chart(chart_data, "Item", "Recommendation Score", "Recommendation score by item", "#8b5a44")
        st.pyplot(fig, use_container_width=True)


def render_dataset_insights(df: pd.DataFrame) -> None:
    """Minimal charts for presentation-safe insights."""
    st.markdown(
        """
        <div class="hero-card">
            <div class="eyebrow">Dataset insights</div>
            <h2 style="margin-top:0;">Short visual summaries from the processed dataset.</h2>
            <p class="muted">
                These charts are kept simple so they are easy to explain during a presentation.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_categories = get_top_category_counts(df)
    age_highlights = get_age_highlights()
    age_highlights["score_percent"] = age_highlights["recommendation_score"] * 100
    occasion_highlights = get_occasion_highlights()
    occasion_highlights["score_percent"] = occasion_highlights["recommendation_score"] * 100

    col1, col2 = st.columns(2, gap="large")
    with col1:
        fig = make_bar_chart(
            top_categories,
            "style_category",
            "count",
            "Top categories",
            "#b56d4f",
        )
        st.pyplot(fig, use_container_width=True)
    with col2:
        fig = make_bar_chart(
            age_highlights,
            "age_group",
            "score_percent",
            "Strongest trend match by age group",
            "#9f7a5a",
        )
        st.pyplot(fig, use_container_width=True)

    fig = make_bar_chart(
        occasion_highlights,
        "occasion",
        "score_percent",
        "Strongest trend match by occasion",
        "#7d5a49",
    )
    st.pyplot(fig, use_container_width=True)

    st.subheader("Data preview")
    preview_columns = ["name", "brand", "style_category", "age_group", "occasion", "trend_label", "recommendation_score"]
    preview_df = df[preview_columns].copy().head(12)
    preview_df["recommendation_score"] = preview_df["recommendation_score"].map(lambda value: f"{float(value) * 100:.1f}%")
    st.dataframe(preview_df, use_container_width=True, hide_index=True)


def render_model_info(summary: dict, model_status: str) -> None:
    """Explain the model in honest, simple language."""
    metric_col, note_col = st.columns([0.9, 1.1], gap="large")

    with metric_col:
        st.markdown(
            """
            <div class="soft-card">
                <div class="eyebrow">Model info</div>
                <h3 style="margin-top:0;">KNN-based classification</h3>
                <p class="muted">
                    The project uses K-Nearest Neighbours. In simple terms, it compares the selected profile with
                    similar rows in the processed dataset and then returns the closest match.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        metric_df = pd.DataFrame(
            {
                "Metric": [
                    "Validation Accuracy (Derived Labels)",
                    "Precision",
                    "Recall",
                    "F1 Score",
                    "Best K",
                ],
                "Value": [
                    f"{float(summary.get('accuracy', 0)) * 100:.1f}%",
                    f"{float(summary.get('precision', 0)) * 100:.1f}%",
                    f"{float(summary.get('recall', 0)) * 100:.1f}%",
                    f"{float(summary.get('f1_score', 0)) * 100:.1f}%",
                    summary.get("best_params", {}).get("classifier__n_neighbors", "--"),
                ],
            }
        )
        st.dataframe(metric_df, use_container_width=True, hide_index=True)

    with note_col:
        assumptions = summary.get("assumptions", [])
        st.markdown(
            f"""
            <div class="soft-card">
                <div class="eyebrow">Method notes</div>
                <p class="muted">
                    These numbers come from the notebook pipeline. The model is trained on engineered labels and
                    preprocessed features, so the result should be presented as a student project, not as a live
                    production system.
                </p>
                <p><strong>Current model status:</strong> {html.escape(model_status)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("**Key assumptions**")
        for item in assumptions:
            st.write(f"- {item}")

        if summary.get("note"):
            st.caption(summary["note"])


def render_about_project() -> None:
    """Project context and future integration notes."""
    st.markdown(
        """
        <div class="hero-card">
            <div class="eyebrow">About project</div>
            <h2 style="margin-top:0;">How this dashboard fits the existing project.</h2>
            <p class="muted">
                This Streamlit app is another presentation layer for the same women fashion trend project. It reads
                the processed dataset and exported JSON files and shows them in a simple dashboard format.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown(
            """
            <div class="soft-card">
                <div class="eyebrow">What the project does</div>
                <ul class="muted">
                    <li>Cleans the fashion dataset and derives age group, occasion, and trend-related fields.</li>
                    <li>Uses a KNN model for similarity-based classification on derived trend labels.</li>
                    <li>Exports JSON outputs that can be shown in both the website and this dashboard.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="soft-card">
                <div class="eyebrow">Where to place your files</div>
                <p class="muted">
                    Processed dataset: <code>{DATASET_DISPLAY_PATH}</code><br>
                    Trained model: <code>{MODEL_DISPLAY_PATH}</code>
                </p>
                <p class="muted">
                    The easiest later setup is to save the preprocessing steps and trained KNN model together in
                    <code>models/model.pkl</code>.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("How to connect the real trained model later")
    st.write("1. Save the preprocessing pipeline and trained KNN model as `models/model.pkl`.")
    st.write("2. Keep using `data/processed/fashion_trend_dataset.csv` for charts and recommended items.")
    st.write("3. Update `build_prediction_result()` if your saved pipeline expects different input fields.")
    st.write("4. Replace the fallback filtering logic with `model.predict()` and `model.predict_proba()` when the model file is ready.")


inject_styles()

dataset = load_dataset()
model_summary = load_model_summary()
_model_object, model_status = load_model_if_available()
options = get_sidebar_options(dataset)

st.sidebar.title("Women Fashion Dashboard")
st.sidebar.caption("Student project")
page = st.sidebar.radio(
    "Sections",
    ["Home / Overview", "Trend Prediction", "Dataset Insights", "Model Info", "About Project"],
)

st.sidebar.markdown("---")
st.sidebar.subheader("Prediction inputs")
selected_age_group = st.sidebar.selectbox("Age group", options["age_groups"])
selected_occasion = st.sidebar.selectbox("Occasion", options["occasions"])

filtered_categories = dataset[
    (dataset["age_group"] == selected_age_group) & (dataset["occasion"] == selected_occasion)
]["style_category"]
category_options = filtered_categories.dropna().astype(str).unique().tolist() or options["categories"]
selected_category = st.sidebar.selectbox("Clothing category", category_options)
selected_style_preference = st.sidebar.selectbox("Style preference (optional)", options["style_preferences"])
predict_clicked = st.sidebar.button("Predict trend match", use_container_width=True, type="primary")

if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = build_prediction_result(
        age_group=selected_age_group,
        occasion=selected_occasion,
        category=selected_category,
        style_preference=selected_style_preference,
    )

if predict_clicked:
    st.session_state.prediction_result = build_prediction_result(
        age_group=selected_age_group,
        occasion=selected_occasion,
        category=selected_category,
        style_preference=selected_style_preference,
    )

prediction_result = st.session_state.prediction_result

if page == "Home / Overview":
    render_home(dataset, model_summary)
elif page == "Trend Prediction":
    render_prediction(prediction_result)
elif page == "Dataset Insights":
    render_dataset_insights(dataset)
elif page == "Model Info":
    render_model_info(model_summary, model_status)
else:
    render_about_project()

render_footer()
