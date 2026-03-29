from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "web" / "data"

STYLE_PREFERENCE_CONFIG = {
    "no_preference": {
        "label": "No specific preference",
        "title_prefix": "Balanced",
        "keywords": [],
        "fallback_sort": "recommendation_score",
    },
    "soft_neutrals": {
        "label": "Soft neutrals",
        "title_prefix": "Soft Neutral",
        "keywords": ["white", "off white", "cream", "beige", "nude", "taupe", "brown", "camel", "peach"],
        "fallback_sort": "price_asc",
    },
    "bold_colours": {
        "label": "Bold colours",
        "title_prefix": "Bold Colour",
        "keywords": ["pink", "fuchsia", "red", "orange", "coral", "magenta", "yellow"],
        "fallback_sort": "recommendation_score",
    },
    "cool_tones": {
        "label": "Cool tones",
        "title_prefix": "Cool Tone",
        "keywords": ["blue", "green", "teal", "turquoise", "lavender", "navy", "olive"],
        "fallback_sort": "name_asc",
    },
    "classic_darks": {
        "label": "Classic darks",
        "title_prefix": "Classic Dark",
        "keywords": ["black", "grey", "gray", "navy", "maroon", "purple", "charcoal"],
        "fallback_sort": "rating_desc",
    },
    "festive_metallics": {
        "label": "Festive metallics",
        "title_prefix": "Festive Metallic",
        "keywords": ["gold", "silver", "bronze", "champagne", "copper", "rose gold"],
        "fallback_sort": "price_desc",
    },
}


app = Flask(__name__)
CORS(app)


def load_json(filename: str, fallback):
    path = DATA_DIR / filename
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback


PROFILE_PREDICTIONS = load_json("profile_predictions.json", [])
RECOMMENDATIONS = load_json("recommendations.json", [])


def to_number(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_image_url(url: str | None) -> str:
    if not url:
        return "assets/images/hero-banner.svg"
    return str(url).replace("http://", "https://")


def normalize_product(product: dict, fallback_score: float = 0.0) -> dict:
    normalized = dict(product)
    normalized["image"] = normalize_image_url(product.get("image"))
    normalized["price"] = to_number(product.get("price"))
    normalized["rating"] = to_number(product.get("rating"))
    normalized["trend_score"] = to_number(product.get("trend_score"), fallback_score)
    normalized["recommendation_score"] = to_number(
        product.get("recommendation_score"),
        normalized["trend_score"] or fallback_score,
    )
    return normalized


def build_product_key(product: dict) -> str:
    product_id = product.get("product_id")
    if product_id:
        return f"pid-{product_id}"
    return f"{product.get('name', '')}__{product.get('brand', 'brand')}__{product.get('price', '')}"


def get_profile(age_group: str, occasion: str) -> dict | None:
    return next(
        (
            item
            for item in PROFILE_PREDICTIONS
            if item.get("age_group") == age_group and item.get("occasion") == occasion
        ),
        None,
    )


def get_style_config(style_preference: str | None) -> dict:
    return STYLE_PREFERENCE_CONFIG.get(style_preference or "", STYLE_PREFERENCE_CONFIG["no_preference"])


def get_matching_products(age_group: str, occasion: str, category: str | None) -> list[dict]:
    profile = get_profile(age_group, occasion)
    merged: dict[str, dict] = {}

    for product in (profile or {}).get("products", []):
        if category and product.get("category") != category:
            continue
        normalized = normalize_product(product, fallback_score=to_number((profile or {}).get("trend_score")))
        normalized["age_group"] = age_group
        normalized["occasion"] = occasion
        merged[build_product_key(normalized)] = normalized

    for product in RECOMMENDATIONS:
        matches_age = product.get("age_group") == age_group
        matches_occasion = product.get("occasion") == occasion
        matches_category = not category or product.get("category") == category
        if not (matches_age and matches_occasion and matches_category):
            continue
        normalized = normalize_product(product)
        merged.setdefault(build_product_key(normalized), normalized)

    return list(merged.values())


def sort_products(products: list[dict], sort_name: str) -> list[dict]:
    if sort_name == "price_asc":
        return sorted(products, key=lambda item: to_number(item.get("price")))
    if sort_name == "price_desc":
        return sorted(products, key=lambda item: to_number(item.get("price")), reverse=True)
    if sort_name == "rating_desc":
        return sorted(products, key=lambda item: to_number(item.get("rating")), reverse=True)
    if sort_name == "name_asc":
        return sorted(products, key=lambda item: str(item.get("name", "")).lower())
    return sorted(products, key=lambda item: to_number(item.get("recommendation_score")), reverse=True)


def rank_products_by_style(products: list[dict], style_config: dict) -> list[dict]:
    ranked = []

    for product in products:
        haystack = " ".join(
            [
                str(product.get("colour", "")),
                str(product.get("name", "")),
                str(product.get("description", "")),
                str(product.get("brand", "")),
            ]
        ).lower()
        style_match_count = sum(1 for keyword in style_config["keywords"] if keyword in haystack)
        base_score = to_number(product.get("recommendation_score") or product.get("trend_score"))
        style_boost = style_match_count * 0.03 if style_config["keywords"] else 0
        ranked.append(
            {
                **product,
                "_style_match_count": style_match_count,
                "_match_score": base_score + style_boost,
            }
        )

    fallback_sorted = sort_products(ranked, style_config["fallback_sort"])
    fallback_order = {build_product_key(item): index for index, item in enumerate(fallback_sorted)}

    ranked.sort(
        key=lambda item: (
            -int(item["_style_match_count"]),
            fallback_order.get(build_product_key(item), 0),
            -to_number(item["_match_score"]),
        )
    )
    return ranked


def build_summary(profile: dict | None, category: str, style_config: dict, ranked_products: list[dict]) -> str:
    matched_items = sum(1 for product in ranked_products if product.get("_style_match_count", 0) > 0)
    base_summary = (profile or {}).get(
        "summary",
        f"{category} is the closest match for the selected age group and occasion in the exported project data.",
    )
    category_sentence = f" This view is focused on {category.lower()}." if category else ""

    if not style_config["keywords"]:
        style_sentence = "The list is ordered by the main recommendation score for this profile."
    elif matched_items:
        style_sentence = f"{matched_items} of the top items also align with the {style_config['label'].lower()} preference."
    else:
        style_sentence = (
            f"The selected preference does not appear directly in the top items, so the list is softly re-ranked "
            f"for a {style_config['label'].lower()} direction."
        )

    return f"{base_summary}{category_sentence} {style_sentence}".strip()


def get_style_impact(ranked_products: list[dict], style_config: dict) -> dict:
    total_items = len(ranked_products)
    matched_items = sum(1 for product in ranked_products if product.get("_style_match_count", 0) > 0)

    if not style_config["keywords"]:
        return {
            "label": "Assisted Ranking",
            "note": "No specific style preference was selected, so the result is ordered using the main recommendation score for this profile.",
        }

    if matched_items >= max(2, (total_items + 1) // 2):
        return {
            "label": "Strong Style Match",
            "note": f"{matched_items} of the top {total_items} items align clearly with the selected style preference.",
        }

    if matched_items > 0:
        return {
            "label": "Partial Style Match",
            "note": f"{matched_items} of the top {total_items} items align with the selected style preference, while the final order still reflects the general recommendation score.",
        }

    return {
        "label": "Assisted Ranking",
        "note": f"The selected {style_config['label'].lower()} preference was not strongly present in the top items, so a style-aware re-ranking was used for this profile.",
    }


def clean_product_response(product: dict) -> dict:
    cleaned = {key: value for key, value in product.items() if not key.startswith("_")}
    cleaned["price"] = to_number(cleaned.get("price"))
    cleaned["rating"] = to_number(cleaned.get("rating"))
    cleaned["trend_score"] = to_number(cleaned.get("trend_score"))
    cleaned["recommendation_score"] = to_number(cleaned.get("recommendation_score"))
    return cleaned


def build_prediction_response(payload: dict) -> dict:
    age_group = (payload.get("ageGroup") or "").strip()
    occasion = (payload.get("occasion") or "").strip()
    category = (payload.get("category") or "").strip()
    style_preference = (payload.get("stylePreference") or "no_preference").strip()

    profile = get_profile(age_group, occasion)
    style_config = get_style_config(style_preference)
    matching_products = get_matching_products(age_group, occasion, category)
    ranked_products = rank_products_by_style(matching_products, style_config)[:4]

    title_category = category or (profile or {}).get("predicted_style") or "Style Match"
    recommended_style = (
        f"{style_config['title_prefix']} {title_category}"
        if style_config["keywords"]
        else title_category
    )

    average_score = (
        sum(to_number(product.get("_match_score")) for product in ranked_products) / len(ranked_products)
        if ranked_products
        else to_number((profile or {}).get("trend_score"))
    )
    style_impact = get_style_impact(ranked_products, style_config)

    return {
        "recommended_style": recommended_style,
        "summary": build_summary(profile, title_category, style_config, ranked_products),
        "score": round(average_score, 3),
        "style_impact": style_impact["label"],
        "style_impact_note": style_impact["note"],
        "style_preference": style_config["label"],
        "products": [clean_product_response(product) for product in ranked_products],
    }


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True) or {}
    if not payload.get("ageGroup") or not payload.get("occasion"):
        return jsonify({"error": "ageGroup and occasion are required"}), 400

    # Version 1 backend: this uses the exported JSON outputs.
    # A later version can replace this function with real model inference.
    response = build_prediction_response(payload)
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
