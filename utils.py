"""Helper functions for the Streamlit fashion trend dashboard."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DATASET_PATH = BASE_DIR / "data" / "processed" / "fashion_trend_dataset.csv"
MODEL_PATH = BASE_DIR / "models" / "model.pkl"
MODEL_SUMMARY_PATH = BASE_DIR / "web" / "data" / "model_summary.json"
PROFILE_PREDICTIONS_PATH = BASE_DIR / "web" / "data" / "profile_predictions.json"
TRENDS_BY_AGE_PATH = BASE_DIR / "web" / "data" / "trends_by_age.json"
TRENDS_BY_OCCASION_PATH = BASE_DIR / "web" / "data" / "trends_by_occasion.json"

STYLE_PREFERENCE_MAP = {
    "No specific preference": [],
    "Soft neutrals": ["white", "off white", "cream", "beige", "nude", "taupe", "brown"],
    "Bold colours": ["pink", "fuchsia", "red", "orange", "yellow"],
    "Cool tones": ["blue", "green", "teal", "turquoise"],
    "Classic darks": ["black", "grey", "gray", "navy", "maroon", "purple"],
    "Festive metallics": ["gold", "silver", "rose gold"],
}


def _sample_records() -> list[dict[str, Any]]:
    """Small fallback dataset so the dashboard can still open during setup."""
    return [
        {
            "p_id": "1001",
            "name": "Sample Casual Crop Top",
            "brand": "Demo Studio",
            "colour": "Pink",
            "price": 799,
            "avg_rating": 4.4,
            "ratingcount": 38,
            "occasion": "Casual",
            "style_category": "Tops",
            "age_group": "Teen Girls (13-19)",
            "trend_score": 0.76,
            "trend_label": "Rising Trend",
            "predicted_trend_label": "Rising Trend",
            "high_trend_probability": 0.82,
            "recommendation_score": 0.84,
            "img": "",
        },
        {
            "p_id": "1002",
            "name": "Sample Office Blazer",
            "brand": "Demo Studio",
            "colour": "Black",
            "price": 1899,
            "avg_rating": 4.6,
            "ratingcount": 44,
            "occasion": "Office",
            "style_category": "Blazers",
            "age_group": "Adult Women (20-29)",
            "trend_score": 0.83,
            "trend_label": "High Trend",
            "predicted_trend_label": "High Trend",
            "high_trend_probability": 0.9,
            "recommendation_score": 0.88,
            "img": "",
        },
        {
            "p_id": "1003",
            "name": "Sample Festive Kurta Set",
            "brand": "Demo Studio",
            "colour": "Green",
            "price": 2499,
            "avg_rating": 4.5,
            "ratingcount": 41,
            "occasion": "Festive",
            "style_category": "Ethnic Sets",
            "age_group": "Married Women (30-45)",
            "trend_score": 0.87,
            "trend_label": "High Trend",
            "predicted_trend_label": "High Trend",
            "high_trend_probability": 0.93,
            "recommendation_score": 0.91,
            "img": "",
        },
        {
            "p_id": "1004",
            "name": "Sample Evening Dress",
            "brand": "Demo Studio",
            "colour": "Navy Blue",
            "price": 2199,
            "avg_rating": 4.3,
            "ratingcount": 29,
            "occasion": "Party",
            "style_category": "Dresses",
            "age_group": "Adult Women (20-29)",
            "trend_score": 0.79,
            "trend_label": "Rising Trend",
            "predicted_trend_label": "Rising Trend",
            "high_trend_probability": 0.8,
            "recommendation_score": 0.85,
            "img": "",
        },
        {
            "p_id": "1005",
            "name": "Sample Wedding Saree",
            "brand": "Demo Studio",
            "colour": "Gold",
            "price": 3399,
            "avg_rating": 4.7,
            "ratingcount": 52,
            "occasion": "Wedding",
            "style_category": "Sarees",
            "age_group": "Elegant & Mature (45+)",
            "trend_score": 0.9,
            "trend_label": "High Trend",
            "predicted_trend_label": "High Trend",
            "high_trend_probability": 0.95,
            "recommendation_score": 0.93,
            "img": "",
        },
    ]


def normalize_image_url(url: str | None) -> str:
    """Use HTTPS to avoid mixed-content issues when remote images are shown."""
    if not url:
        return ""
    return str(url).replace("http://", "https://", 1)


def strip_html_tags(value: str | None) -> str:
    """Remove basic HTML so product descriptions stay readable in Streamlit."""
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", text).strip()


def format_price(value: float | int | None) -> str:
    """Format prices in Indian Rupees."""
    try:
        return f"Rs. {float(value):,.0f}"
    except (TypeError, ValueError):
        return "Rs. --"


def _ordered_unique(series: pd.Series) -> list[str]:
    seen: dict[str, None] = {}
    for item in series.dropna().astype(str):
        clean_item = item.strip()
        if clean_item and clean_item not in seen:
            seen[clean_item] = None
    return list(seen.keys())


def _load_json_file(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _normalise_dataset(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    frame.columns = [column.strip() for column in frame.columns]

    if "image" not in frame.columns and "img" in frame.columns:
        frame["image"] = frame["img"]

    numeric_columns = [
        "price",
        "avg_rating",
        "ratingcount",
        "trend_score",
        "high_trend_probability",
        "recommendation_score",
    ]
    for column in numeric_columns:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")

    text_columns = [
        "name",
        "brand",
        "colour",
        "occasion",
        "style_category",
        "age_group",
        "trend_label",
        "predicted_trend_label",
    ]
    for column in text_columns:
        if column in frame.columns:
            frame[column] = frame[column].fillna("Not specified").astype(str)

    if "rating_count" not in frame.columns and "ratingcount" in frame.columns:
        frame["rating_count"] = frame["ratingcount"]

    if "recommendation_score" not in frame.columns and "trend_score" in frame.columns:
        frame["recommendation_score"] = frame["trend_score"]

    if "predicted_trend_label" not in frame.columns and "trend_label" in frame.columns:
        frame["predicted_trend_label"] = frame["trend_label"]

    if "image" in frame.columns:
        frame["image"] = frame["image"].fillna("").map(normalize_image_url)

    return frame


@lru_cache(maxsize=1)
def load_dataset() -> pd.DataFrame:
    """Load the processed dataset used by the website and dashboard."""
    if PROCESSED_DATASET_PATH.exists():
        df = pd.read_csv(PROCESSED_DATASET_PATH)
    else:
        df = pd.DataFrame(_sample_records())
    return _normalise_dataset(df)


def _fallback_model_summary(df: pd.DataFrame) -> dict[str, Any]:
    top_category = (
        df.groupby("style_category")["recommendation_score"]
        .mean()
        .sort_values(ascending=False)
        .index[0]
    )
    return {
        "dataset_file": PROCESSED_DATASET_PATH.name,
        "rows_after_cleaning": int(len(df)),
        "rows_removed_as_duplicates": 0,
        "model": "KNeighborsClassifier",
        "target": "trend_label",
        "best_params": {
            "classifier__metric": "minkowski",
            "classifier__n_neighbors": 5,
            "classifier__weights": "distance",
        },
        "accuracy": 0.0,
        "precision": 0.0,
        "recall": 0.0,
        "f1_score": 0.0,
        "class_labels": sorted(df["trend_label"].dropna().unique().tolist()),
        "confusion_matrix": [],
        "top_trending_category": top_category,
        "assumptions": [
            "This fallback summary is shown because model_summary.json was not found.",
            "The dashboard is still usable with exported dataset files.",
        ],
        "note": "Replace this fallback by keeping the exported JSON from the notebook pipeline.",
    }


@lru_cache(maxsize=1)
def load_model_summary() -> dict[str, Any]:
    """Load exported model metrics or build a lightweight fallback summary."""
    if MODEL_SUMMARY_PATH.exists():
        return _load_json_file(MODEL_SUMMARY_PATH)
    return _fallback_model_summary(load_dataset())


def _build_recommendation_records(df: pd.DataFrame, top_n: int = 60) -> list[dict[str, Any]]:
    """Turn top rows into simple product cards."""
    sorted_df = df.sort_values(
        by=["recommendation_score", "avg_rating", "ratingcount"],
        ascending=[False, False, False],
    ).head(top_n)

    records: list[dict[str, Any]] = []
    for _, row in sorted_df.iterrows():
        records.append(
            {
                "id": str(row.get("p_id", "")),
                "product_id": str(row.get("p_id", "")),
                "name": row.get("name", "Fashion item"),
                "category": row.get("style_category", "Not specified"),
                "age_group": row.get("age_group", "Not specified"),
                "occasion": row.get("occasion", "Not specified"),
                "price": float(row.get("price", 0) or 0),
                "rating": float(row.get("avg_rating", 0) or 0),
                "rating_count": int(float(row.get("ratingcount", 0) or 0)),
                "trend_score": float(row.get("trend_score", 0) or 0),
                "recommendation_score": float(row.get("recommendation_score", 0) or 0),
                "trend_label": row.get("predicted_trend_label", row.get("trend_label", "Trend match")),
                "brand": row.get("brand", "Brand"),
                "colour": row.get("colour", "Not specified"),
                "image": normalize_image_url(row.get("image", "")),
                "description": row.get("name", ""),
                "reason_tags": [
                    row.get("occasion", "Occasion"),
                    row.get("age_group", "Age group"),
                    row.get("style_category", "Category"),
                    f"Rating {float(row.get('avg_rating', 0) or 0):.1f}",
                ],
            }
        )
    return records


def _normalise_product_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Clean image URLs and descriptions for display."""
    cleaned: list[dict[str, Any]] = []
    for item in records:
        cleaned.append(
            {
                **item,
                "image": normalize_image_url(item.get("image", "")),
                "description": strip_html_tags(item.get("description", "")),
                "reason_tags": item.get("reason_tags", []),
            }
        )
    return cleaned


def _build_profile_predictions(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Create simple profile summaries when exported JSON is unavailable."""
    profiles: list[dict[str, Any]] = []
    grouped = df.groupby(["age_group", "occasion"], dropna=False)
    for (age_group, occasion), group in grouped:
        category_scores = (
            group.groupby("style_category")["recommendation_score"]
            .mean()
            .sort_values(ascending=False)
        )
        predicted_style = category_scores.index[0]
        top_products_df = (
            group[group["style_category"] == predicted_style]
            .sort_values(
                by=["recommendation_score", "avg_rating", "ratingcount"],
                ascending=[False, False, False],
            )
            .head(5)
        )
        profiles.append(
            {
                "age_group": age_group,
                "occasion": occasion,
                "predicted_style": predicted_style,
                "trend_score": round(float(group["trend_score"].mean()), 3),
                "avg_rating": round(float(group["avg_rating"].mean()), 2),
                "product_count": int(len(group)),
                "summary": (
                    f"For {age_group.lower()} and {occasion.lower()} use, "
                    f"{predicted_style.lower()} has the strongest average score in this dataset slice."
                ),
                "products": _build_recommendation_records(top_products_df, top_n=5),
            }
        )
    return profiles


@lru_cache(maxsize=1)
def load_profile_predictions() -> list[dict[str, Any]]:
    """Load exported profile predictions or derive them from the dataset."""
    if PROFILE_PREDICTIONS_PATH.exists():
        profiles = _load_json_file(PROFILE_PREDICTIONS_PATH)
    else:
        profiles = _build_profile_predictions(load_dataset())

    for profile in profiles:
        profile["products"] = _normalise_product_records(profile.get("products", []))
    return profiles


def _aggregate_by_column(column_name: str) -> pd.DataFrame:
    df = load_dataset()
    grouped = (
        df.groupby([column_name, "style_category"])["recommendation_score"]
        .mean()
        .reset_index()
        .sort_values("recommendation_score", ascending=False)
    )
    return grouped


@lru_cache(maxsize=1)
def load_trends_by_age() -> pd.DataFrame:
    """Load age-group trend summary for charts."""
    if TRENDS_BY_AGE_PATH.exists():
        return pd.DataFrame(_load_json_file(TRENDS_BY_AGE_PATH))
    return _aggregate_by_column("age_group")


@lru_cache(maxsize=1)
def load_trends_by_occasion() -> pd.DataFrame:
    """Load occasion trend summary for charts."""
    if TRENDS_BY_OCCASION_PATH.exists():
        return pd.DataFrame(_load_json_file(TRENDS_BY_OCCASION_PATH))
    return _aggregate_by_column("occasion")


def load_model_if_available() -> tuple[Any | None, str]:
    """
    Try to load a saved model pipeline.

    The easiest future integration is to save the full preprocessing pipeline
    plus KNN classifier as `models/model.pkl`.
    """
    if not MODEL_PATH.exists():
        return None, "No local model.pkl found. The dashboard is using exported recommendation outputs."

    try:
        import joblib

        model = joblib.load(MODEL_PATH)
        return model, "Loaded model.pkl successfully."
    except Exception as exc:  # pragma: no cover - defensive path for local setup
        return None, f"model.pkl was found but could not be loaded: {exc}"


def get_sidebar_options(df: pd.DataFrame) -> dict[str, list[str]]:
    """Create clean dropdown options from the processed dataset."""
    return {
        "age_groups": _ordered_unique(df["age_group"]),
        "occasions": _ordered_unique(df["occasion"]),
        "categories": _ordered_unique(df["style_category"]),
        "style_preferences": list(STYLE_PREFERENCE_MAP.keys()),
    }


def _apply_style_preference(df: pd.DataFrame, style_preference: str) -> pd.DataFrame:
    keywords = STYLE_PREFERENCE_MAP.get(style_preference, [])
    if not keywords or "colour" not in df.columns:
        return df

    colour_series = df["colour"].fillna("").astype(str).str.lower()
    mask = colour_series.apply(lambda value: any(keyword in value for keyword in keywords))
    filtered = df[mask]
    return filtered if not filtered.empty else df


def _find_profile_entry(age_group: str, occasion: str) -> dict[str, Any] | None:
    for entry in load_profile_predictions():
        if entry.get("age_group") == age_group and entry.get("occasion") == occasion:
            return entry
    return None


def _reason_summary(items: list[dict[str, Any]]) -> str:
    tag_counter: dict[str, int] = {}
    for item in items:
        for tag in item.get("reason_tags", []):
            tag_counter[tag] = tag_counter.get(tag, 0) + 1
    if not tag_counter:
        return "These items were selected from the highest-scoring rows in the filtered dataset."
    top_tags = [tag for tag, _count in sorted(tag_counter.items(), key=lambda pair: pair[1], reverse=True)[:3]]
    return "Most recommended items align with " + ", ".join(top_tags) + "."


def _to_product_records(df: pd.DataFrame, limit: int = 5) -> list[dict[str, Any]]:
    top_df = df.sort_values(
        by=["recommendation_score", "avg_rating", "ratingcount"],
        ascending=[False, False, False],
    ).head(limit)
    return _build_recommendation_records(top_df, top_n=limit)


def _choose_result_pool(
    df: pd.DataFrame,
    age_group: str,
    occasion: str,
    category: str,
    style_preference: str,
) -> tuple[pd.DataFrame, str]:
    """Pick the simplest useful dataset slice for the current filters."""
    profile_pool = df[(df["age_group"] == age_group) & (df["occasion"] == occasion)].copy()
    category_pool = profile_pool[profile_pool["style_category"] == category].copy()
    styled_pool = _apply_style_preference(category_pool, style_preference)

    if not styled_pool.empty:
        return styled_pool, "Showing items that match the selected profile, category, and style preference."
    if not category_pool.empty:
        return category_pool, "Showing items that match the selected profile and category."
    if not profile_pool.empty:
        return profile_pool, "Showing the strongest items for the selected age group and occasion."

    fallback_pool = df[df["style_category"] == category].copy()
    if not fallback_pool.empty:
        return fallback_pool, "No exact profile match was found, so the results are based on the selected category."

    return df.copy(), "No exact match was found, so the results are based on the strongest rows in the dataset."


def build_prediction_result(
    age_group: str,
    occasion: str,
    category: str,
    style_preference: str,
    top_n: int = 5,
) -> dict[str, Any]:
    """Build the prediction view from profile summaries and filtered rows."""
    df = load_dataset()
    profile_entry = _find_profile_entry(age_group, occasion)
    selected_pool, selection_note = _choose_result_pool(
        df,
        age_group=age_group,
        occasion=occasion,
        category=category,
        style_preference=style_preference,
    )

    predicted_category = (
        selected_pool.groupby("style_category")["recommendation_score"]
        .mean()
        .sort_values(ascending=False)
        .index[0]
    )
    dominant_label = (
        selected_pool["predicted_trend_label"]
        .mode()
        .iloc[0]
        if not selected_pool["predicted_trend_label"].mode().empty
        else "Trend match"
    )
    top_items = _to_product_records(selected_pool, limit=top_n)
    explanation = _reason_summary(top_items)

    profile_summary = profile_entry.get("summary") if profile_entry else ""
    if profile_summary and profile_entry.get("predicted_style") != category:
        profile_summary += f" The selected category is {category}, so the list below stays within that category where possible."

    support_table = (
        pd.DataFrame(top_items)[
            ["name", "brand", "category", "price", "rating", "recommendation_score", "trend_label"]
        ]
        .rename(
            columns={
                "name": "Item",
                "brand": "Brand",
                "category": "Category",
                "price": "Price",
                "rating": "Rating",
                "recommendation_score": "Recommendation Score",
                "trend_label": "Trend Label",
            }
        )
    )

    chart_table = support_table[["Item", "Recommendation Score"]].copy()
    chart_table["Recommendation Score"] = chart_table["Recommendation Score"].astype(float) * 100

    return {
        "predicted_category": predicted_category,
        "selected_category": category,
        "trend_label": dominant_label,
        "confidence_score": round(float(selected_pool["recommendation_score"].head(min(10, len(selected_pool))).mean() * 100), 1),
        "profile_trend_score": round(float(selected_pool["trend_score"].mean() * 100), 1),
        "average_rating": round(float(selected_pool["avg_rating"].mean()), 2),
        "product_count": int(len(selected_pool)),
        "selection_note": selection_note,
        "profile_summary": profile_summary or "This result is based on the strongest rows available for the selected filters.",
        "explanation": explanation,
        "items": top_items,
        "support_table": support_table,
        "chart_table": chart_table,
    }


def get_overview_metrics(df: pd.DataFrame, summary: dict[str, Any]) -> list[dict[str, str]]:
    """Small summary blocks for the Home section."""
    return [
        {
            "label": "Rows in processed dataset",
            "value": f"{int(summary.get('rows_after_cleaning', len(df))):,}",
            "help": "Rows available after cleaning and duplicate handling.",
        },
        {
            "label": "Style categories",
            "value": str(df["style_category"].nunique()),
            "help": "Unique clothing categories used across recommendations.",
        },
        {
            "label": "Occasions covered",
            "value": str(df["occasion"].nunique()),
            "help": "Occasion groups represented in the filtered dataset.",
        },
        {
            "label": "Validation accuracy (derived labels)",
            "value": f"{float(summary.get('accuracy', 0)) * 100:.1f}%",
            "help": "Accuracy measured against engineered trend labels, not customer ground truth.",
        },
    ]


def get_top_category_counts(df: pd.DataFrame, limit: int = 8) -> pd.DataFrame:
    """Count the most common categories for a clean dashboard chart."""
    return (
        df["style_category"]
        .value_counts()
        .head(limit)
        .rename_axis("style_category")
        .reset_index(name="count")
    )


def get_age_highlights() -> pd.DataFrame:
    """Take the top trend match for each age group."""
    age_df = load_trends_by_age().copy()
    age_df = age_df.sort_values("recommendation_score", ascending=False)
    return age_df.groupby("age_group", as_index=False).first()


def get_occasion_highlights() -> pd.DataFrame:
    """Take the top trend match for each occasion."""
    occasion_df = load_trends_by_occasion().copy()
    occasion_df = occasion_df.sort_values("recommendation_score", ascending=False)
    return occasion_df.groupby("occasion", as_index=False).first()
