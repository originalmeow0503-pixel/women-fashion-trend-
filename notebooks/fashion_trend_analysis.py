# %% [markdown]
# # Women's Fashion Trend Prediction With KNN
#
# This notebook is designed for a college project that combines:
# - data cleaning
# - exploratory data analysis
# - feature engineering
# - KNN-based trend prediction
# - static website integration through JSON export
#
# Business goal:
# predict what women's clothing styles are trending for different age groups and occasions.
#
# Important note:
# this dataset is a product catalog, not a transaction dataset. That means some business fields
# such as customer age, customer ID, and real purchase history are not available directly.
# We will create sensible proxy features and clearly document every assumption.

# %%
import ast
import json
import re
import warnings
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
from IPython.display import display
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")
matplotlib.use("Agg")
import matplotlib.pyplot as plt

pd.set_option("display.max_columns", 100)
sns.set_theme(style="whitegrid", palette="rocket")


# %% [markdown]
# ## 1. Paths And Dataset Loading
#
# The Kaggle CSV is stored in `data/raw/`.
# The notebook also exports cleaned data and website-ready JSON into project folders.

# %%
PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
WEB_DATA_DIR = PROJECT_ROOT / "web" / "data"
MODELS_DIR = PROJECT_ROOT / "models"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

DATA_PATH = RAW_DIR / "Fashion Dataset.csv"
if not DATA_PATH.exists():
    csv_files = sorted(RAW_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("No CSV file found in data/raw/.")
    DATA_PATH = csv_files[0]

print(f"Using dataset: {DATA_PATH.name}")

df_raw = pd.read_csv(DATA_PATH)
print("Raw shape:", df_raw.shape)
display(df_raw.head())


# %% [markdown]
# ## 2. Inspect Columns And Identify Useful Fields
#
# These are the main useful columns in this Kaggle dataset:
# - `name`: product title
# - `price`: product price
# - `brand`: fashion brand
# - `colour`: product color
# - `img`: image URL
# - `ratingCount`: popularity proxy
# - `avg_rating`: product quality/review proxy
# - `description`: detailed product text
# - `p_attributes`: rich dictionary-like metadata that contains fields such as `Occasion`,
#   `Top Type`, `Bottom Type`, and `Main Trend`
#
# Columns like `Unnamed: 0` are indexing artifacts and are not useful for modeling.

# %%
def normalize_name(name):
    return re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")


df = df_raw.copy()
df.columns = [normalize_name(col) for col in df.columns]

print("Normalized columns:")
print(df.columns.tolist())
print()
print("Dataset info:")
display(df.info())

useful_columns = pd.DataFrame(
    [
        ["name", "Yes", "Main product name used for style and keyword extraction."],
        ["price", "Yes", "Numeric product price used in EDA and KNN features."],
        ["brand", "Yes", "Useful for brand popularity and product grouping."],
        ["colour", "Yes", "Helpful categorical feature for product context."],
        ["img", "Yes", "Used by the shopping website product cards."],
        ["ratingcount", "Yes", "Proxy for popularity and customer engagement."],
        ["avg_rating", "Yes", "Proxy for satisfaction and product quality."],
        ["description", "Yes", "Helpful for rule-based occasion/style detection."],
        ["p_attributes", "Yes", "Most important metadata source for occasion and product type."],
        ["p_id", "Yes", "Useful as a product identifier."],
        ["unnamed_0", "No", "Looks like an exported row index, so we drop it."],
    ],
    columns=["column", "useful_for_project", "why_it_matters"],
)
display(useful_columns)


# %% [markdown]
# ## 3. Helper Functions
#
# The dataset stores many fashion details inside `p_attributes` as a string representation of a
# Python dictionary. We parse that column and then use rule-based business logic to build:
# - standardized occasion labels
# - style categories
# - age groups
# - business-friendly trend scores

# %%
AGE_GROUPS = [
    "Teen Girls (13-19)",
    "Young Women (20-29)",
    "Married Women (30-45)",
    "Older Women (46+)",
]

AGE_STYLE_PREFERENCES = {
    "Teen Girls (13-19)": ["Tops", "Shorts", "Dresses", "Co-ord Sets", "Jumpsuits"],
    "Young Women (20-29)": ["Co-ord Sets", "Tops", "Dresses", "Office Wear", "Jumpsuits", "Bottom Wear"],
    "Married Women (30-45)": ["Ethnic Sets", "Kurtis & Kurtas", "Traditional Wear", "Dresses", "Bottom Wear"],
    "Older Women (46+)": ["Sarees", "Traditional Wear", "Ethnic Sets", "Kurtis & Kurtas"],
}

OCCASION_STYLE_PREFERENCES = {
    "Casual": ["Tops", "Shorts", "Bottom Wear", "Dresses", "Co-ord Sets"],
    "Party": ["Tops", "Dresses", "Jumpsuits", "Co-ord Sets"],
    "Wedding": ["Sarees", "Ethnic Sets", "Traditional Wear", "Dresses"],
    "Festive": ["Ethnic Sets", "Kurtis & Kurtas", "Traditional Wear", "Sarees"],
    "Office": ["Office Wear", "Tops", "Bottom Wear", "Co-ord Sets"],
    "Vacation": ["Dresses", "Shorts", "Tops", "Co-ord Sets", "Bottom Wear"],
    "Daily Wear": ["Kurtis & Kurtas", "Traditional Wear", "Tops", "Bottom Wear", "Sarees"],
}

AGE_OCCASION_AFFINITY = {
    "Teen Girls (13-19)": {"Casual": 0.18, "Party": 0.18, "Vacation": 0.16},
    "Young Women (20-29)": {"Casual": 0.16, "Party": 0.16, "Office": 0.18, "Vacation": 0.12},
    "Married Women (30-45)": {"Daily Wear": 0.15, "Festive": 0.2, "Wedding": 0.2},
    "Older Women (46+)": {"Daily Wear": 0.14, "Festive": 0.18, "Wedding": 0.18},
}


def parse_attribute_dict(value):
    if pd.isna(value):
        return {}
    text = str(value).strip()
    if not text:
        return {}
    try:
        parsed = ast.literal_eval(text)
        return parsed if isinstance(parsed, dict) else {}
    except (ValueError, SyntaxError):
        return {}


def clean_text(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def strip_html(text):
    return re.sub(r"<[^>]+>", " ", clean_text(text)).strip()


def normalize_title(text):
    return clean_text(text).title() if clean_text(text) else "Unknown"


def preference_score(style_category, preferred_styles):
    if style_category not in preferred_styles:
        return 0.18
    rank = preferred_styles.index(style_category)
    score_map = {0: 1.0, 1: 0.9, 2: 0.8, 3: 0.7, 4: 0.6, 5: 0.5}
    return score_map.get(rank, 0.45)


def minmax_scale(series):
    minimum = series.min()
    maximum = series.max()
    if maximum == minimum:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - minimum) / (maximum - minimum)


def clip_outliers_iqr(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = max(series.min(), q1 - 1.5 * iqr)
    upper = q3 + 1.5 * iqr
    return series.clip(lower=lower, upper=upper), round(lower, 2), round(upper, 2)


def standardize_occasion(raw_occasion, text_blob):
    text = f"{clean_text(raw_occasion)} {clean_text(text_blob)}".lower()

    mapping = [
        ("Wedding", ["wedding", "bridal", "bride", "engagement", "sangeet", "mehendi"]),
        ("Office", ["office", "work", "formal", "corporate"]),
        ("Party", ["party", "evening", "club", "cocktail"]),
        ("Vacation", ["vacation", "travel", "beach", "resort", "holiday", "outdoor"]),
        ("Festive", ["festive", "ethnic", "traditional", "fusion", "festival", "pooja", "puja"]),
        ("Daily Wear", ["daily", "everyday", "maternity", "routine"]),
        ("Casual", ["casual", "western", "sports", "sport", "street"]),
    ]

    for label, keywords in mapping:
        if any(keyword in text for keyword in keywords):
            return label
    return "Casual"


def infer_style_category(row):
    text_blob = " ".join(
        [
            clean_text(row.get("name")),
            clean_text(row.get("description")),
            clean_text(row.get("attr_top_type")),
            clean_text(row.get("attr_bottom_type")),
            clean_text(row.get("attr_main_trend")),
            clean_text(row.get("occasion")),
        ]
    ).lower()

    if any(word in text_blob for word in ["saree", "sari"]):
        return "Sarees"
    if any(word in text_blob for word in ["co-ord", "co ord", "coord", "co-ords"]):
        return "Co-ord Sets"
    if any(word in text_blob for word in ["jumpsuit", "playsuit", "romper"]):
        return "Jumpsuits"
    if any(word in text_blob for word in ["kurta set", "kurta with", "palazzos", "dupatta", "sharara", "gharara", "lehenga"]):
        return "Ethnic Sets"
    if any(word in text_blob for word in ["kurta", "kurti", "tunic"]):
        return "Kurtis & Kurtas"
    if any(word in text_blob for word in ["traditional", "ethnic wear", "indian wear"]):
        return "Traditional Wear"
    if any(word in text_blob for word in ["dress", "maxi", "midi", "gown", "anarkali dress"]):
        return "Dresses"
    if any(word in text_blob for word in ["crop top", "top", "t-shirt", "tee", "shirt", "blouse", "cami", "tank"]):
        return "Tops"
    if any(word in text_blob for word in ["shorts", "short"]):
        return "Shorts"
    if any(word in text_blob for word in ["blazer", "jacket", "shrug", "coat", "layer"]):
        return "Jackets & Layers"
    if any(word in text_blob for word in ["trouser", "pants", "jeans", "palazzo", "leggings", "skirt", "bottom"]):
        return "Bottom Wear"
    if row.get("occasion") == "Office":
        return "Office Wear"
    return "Traditional Wear" if row.get("occasion") in {"Festive", "Wedding"} else "Tops"


def infer_age_group(style_category, occasion, text_blob):
    scores = {age_group: preference_score(style_category, preferences) for age_group, preferences in AGE_STYLE_PREFERENCES.items()}

    for age_group, affinity in AGE_OCCASION_AFFINITY.items():
        scores[age_group] += affinity.get(occasion, 0)

    text = clean_text(text_blob).lower()
    if any(keyword in text for keyword in ["girls", "crop", "mini", "short", "teen"]):
        scores["Teen Girls (13-19)"] += 0.18
    if any(keyword in text for keyword in ["office", "formal", "workwear"]):
        scores["Young Women (20-29)"] += 0.18
    if any(keyword in text for keyword in ["dupatta", "ethnic", "kurta", "kurti", "palazzo"]):
        scores["Married Women (30-45)"] += 0.16
    if any(keyword in text for keyword in ["saree", "traditional", "classic"]):
        scores["Older Women (46+)"] += 0.18

    return max(scores, key=scores.get)


def create_reason_tags(row):
    tags = [
        row["occasion"],
        row["age_group"],
        row["style_category"],
        f"Rating {row['avg_rating']:.1f}",
    ]
    if row["ratingcount"] > 0:
        tags.append(f"{int(row['ratingcount'])} ratings")
    return tags[:4]


def pick_best_image(row):
    image = clean_text(row.get("img"))
    if image:
        return image
    return "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=900&q=80"


# %% [markdown]
# ## 4. Data Cleaning
#
# Cleaning tasks completed here:
# - remove unnecessary columns
# - parse `p_attributes`
# - handle missing values
# - remove duplicate products
# - cap numeric outliers for KNN-friendly modeling
# - standardize text labels

# %%
starting_rows = len(df)

if "unnamed_0" in df.columns:
    df = df.drop(columns=["unnamed_0"])

attribute_df = pd.json_normalize(df["p_attributes"].apply(parse_attribute_dict))
attribute_df.columns = [f"attr_{normalize_name(col)}" for col in attribute_df.columns]

df = pd.concat([df.drop(columns=["p_attributes"]), attribute_df], axis=1)

duplicate_subset = [column for column in ["p_id", "name", "brand", "price"] if column in df.columns]
before_duplicates = len(df)
df = df.drop_duplicates(subset=duplicate_subset).copy()
duplicates_removed = before_duplicates - len(df)

for column in ["name", "brand", "colour", "description", "img", "p_id"]:
    if column in df.columns:
        df[column] = df[column].fillna("Unknown").map(clean_text)

df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["avg_rating"] = pd.to_numeric(df["avg_rating"], errors="coerce")
df["ratingcount"] = pd.to_numeric(df["ratingcount"], errors="coerce")

df["price"] = df["price"].fillna(df["price"].median())
df["ratingcount"] = df["ratingcount"].fillna(0)
brand_rating_fill = df.groupby("brand")["avg_rating"].transform("median")
df["avg_rating"] = df["avg_rating"].fillna(brand_rating_fill).fillna(df["avg_rating"].median())
df["avg_rating"] = df["avg_rating"].clip(lower=1, upper=5)

df["brand"] = df["brand"].replace({"Roadster the lifestyle co": "Roadster The Lifestyle Co"}).map(normalize_title)
df["colour"] = df["colour"].replace({"na": "Unknown", "": "Unknown"}).map(normalize_title)
df["name"] = df["name"].replace({"Unknown": "Unknown Fashion Product"})
df["description"] = df["description"].replace({"Unknown": "No description available"})

df["price"], price_lower, price_upper = clip_outliers_iqr(df["price"])
df["ratingcount"], rating_lower, rating_upper = clip_outliers_iqr(df["ratingcount"])

print("Rows before cleaning:", starting_rows)
print("Rows after cleaning:", len(df))
print("Duplicate rows removed:", duplicates_removed)
print(f"Price clipped to range: {price_lower} to {price_upper}")
print(f"Rating count clipped to range: {rating_lower} to {rating_upper}")

missing_after_cleaning = df[["name", "price", "brand", "avg_rating", "ratingcount"]].isna().sum()
display(missing_after_cleaning.to_frame("missing_values_after_cleaning"))


# %% [markdown]
# ## 5. Feature Engineering
#
# Because the dataset does not contain real customer age or real purchase transactions,
# we engineer practical proxy features:
# - `occasion` from product attributes and keyword rules
# - `style_category` from product title, description, and product attributes
# - `age_group` from business logic rules
# - popularity and value signals for KNN
# - `trend_score` and `trend_label` as a supervised target for prediction

# %%
df["description_clean"] = df["description"].map(strip_html)
df["text_blob"] = (
    df["name"].fillna("")
    + " "
    + df["description_clean"].fillna("")
    + " "
    + df.get("attr_main_trend", pd.Series("", index=df.index)).fillna("").astype(str)
    + " "
    + df.get("attr_top_type", pd.Series("", index=df.index)).fillna("").astype(str)
    + " "
    + df.get("attr_bottom_type", pd.Series("", index=df.index)).fillna("").astype(str)
)

df["occasion_raw"] = df.get("attr_occasion", pd.Series("", index=df.index)).fillna("")
df["occasion"] = df.apply(lambda row: standardize_occasion(row["occasion_raw"], row["text_blob"]), axis=1)
df["style_category"] = df.apply(infer_style_category, axis=1)
df["age_group"] = df.apply(lambda row: infer_age_group(row["style_category"], row["occasion"], row["text_blob"]), axis=1)

df["description_length"] = df["description_clean"].str.split().str.len().fillna(0)
df["rating_count_log"] = np.log1p(df["ratingcount"])
df["brand_popularity"] = df.groupby("brand")["ratingcount"].transform("mean")
df["brand_avg_rating"] = df.groupby("brand")["avg_rating"].transform("mean")
df["value_score"] = df["avg_rating"] / np.log1p(df["price"].clip(lower=1))
df["rating_available"] = (df["ratingcount"] > 0).astype(int)
df["price_band"] = pd.cut(
    df["price"],
    bins=[0, 799, 1499, 2499, 3999, np.inf],
    labels=["Budget", "Affordable", "Mid Premium", "Premium", "Luxury"],
    include_lowest=True,
)

df["age_style_fit"] = df.apply(
    lambda row: preference_score(row["style_category"], AGE_STYLE_PREFERENCES[row["age_group"]]),
    axis=1,
)
df["occasion_style_fit"] = df.apply(
    lambda row: preference_score(row["style_category"], OCCASION_STYLE_PREFERENCES[row["occasion"]]),
    axis=1,
)

rating_norm = minmax_scale(df["avg_rating"])
popularity_norm = minmax_scale(df["rating_count_log"])
brand_popularity_norm = minmax_scale(df["brand_popularity"])
value_norm = minmax_scale(df["value_score"])

df["trend_score"] = (
    0.32 * rating_norm
    + 0.26 * popularity_norm
    + 0.10 * brand_popularity_norm
    + 0.10 * value_norm
    + 0.12 * df["age_style_fit"]
    + 0.10 * df["occasion_style_fit"]
).round(4)

q1 = df["trend_score"].quantile(0.33)
q2 = df["trend_score"].quantile(0.66)

df["trend_label"] = pd.cut(
    df["trend_score"],
    bins=[-np.inf, q1, q2, np.inf],
    labels=["Classic Stable", "Rising Trend", "High Trend"],
)

display(
    df[
        [
            "name",
            "brand",
            "price",
            "occasion",
            "style_category",
            "age_group",
            "trend_score",
            "trend_label",
        ]
    ].head(10)
)


# %% [markdown]
# ## 6. Exploratory Data Analysis
#
# These charts help explain:
# - how products are distributed across age groups
# - which styles are most common
# - which occasions dominate the catalog
# - how age groups and style categories connect
# - how ratings and popularity relate to trend labels

# %%
fig, axes = plt.subplots(2, 2, figsize=(18, 12))

sns.countplot(data=df, y="age_group", order=df["age_group"].value_counts().index, ax=axes[0, 0])
axes[0, 0].set_title("Distribution Of Age Groups")
axes[0, 0].set_xlabel("Product Count")
axes[0, 0].set_ylabel("")

top_styles = df["style_category"].value_counts().head(10).reset_index()
top_styles.columns = ["style_category", "count"]
sns.barplot(data=top_styles, x="count", y="style_category", ax=axes[0, 1])
axes[0, 1].set_title("Top Clothing Categories")
axes[0, 1].set_xlabel("Product Count")
axes[0, 1].set_ylabel("")

occasion_counts = df["occasion"].value_counts().reset_index()
occasion_counts.columns = ["occasion", "count"]
sns.barplot(data=occasion_counts, x="count", y="occasion", ax=axes[1, 0])
axes[1, 0].set_title("Occasion-Wise Product Distribution")
axes[1, 0].set_xlabel("Product Count")
axes[1, 0].set_ylabel("")

heatmap_data = pd.crosstab(df["age_group"], df["style_category"])
sns.heatmap(heatmap_data, cmap="YlOrBr", ax=axes[1, 1])
axes[1, 1].set_title("Trend Analysis By Age Group")

plt.tight_layout()
plt.show()


# %%
plt.figure(figsize=(12, 7))
sns.scatterplot(
    data=df.sample(min(len(df), 3000), random_state=42),
    x="ratingcount",
    y="avg_rating",
    hue="trend_label",
    alpha=0.7,
)
plt.title("Relationship Between Popularity, Ratings, And Trend Labels")
plt.xlabel("Rating Count")
plt.ylabel("Average Rating")
plt.show()

display(
    df.groupby(["age_group", "style_category"])
    .agg(products=("name", "count"), mean_trend_score=("trend_score", "mean"))
    .sort_values(["age_group", "mean_trend_score"], ascending=[True, False])
    .groupby(level=0)
    .head(3)
    .reset_index()
)


# %% [markdown]
# ### EDA Observations
#
# Beginner-friendly interpretation:
# - `ratingCount` acts like a popularity signal, so products with many ratings often receive higher trend scores.
# - `p_attributes` is the most useful column because it tells us the occasion and product type.
# - The catalog is heavily fashion-category driven, so creating `style_category` and `occasion` improves business readability.
# - Because the dataset is more product-focused than customer-focused, we use proxy features instead of real RFM.


# %% [markdown]
# ## 7. KNN Modeling
#
# Why KNN?
# - KNN is easy to explain in a college viva.
# - It works well when similar products should have similar labels.
# - After encoding categorical features and scaling numeric features, KNN can compare fashion products by distance.
#
# Why we do not use silhouette score:
# - silhouette score is for clustering quality
# - KNN here is a supervised classification model
# - so we use accuracy, precision, recall, F1-score, and a confusion matrix instead

# %%
feature_columns = [
    "price",
    "avg_rating",
    "ratingcount",
    "rating_count_log",
    "description_length",
    "brand_popularity",
    "brand_avg_rating",
    "value_score",
    "rating_available",
    "age_style_fit",
    "occasion_style_fit",
    "style_category",
    "occasion",
    "age_group",
    "brand",
    "colour",
    "price_band",
]

target_column = "trend_label"

model_df = df[feature_columns + [target_column]].copy()

X = model_df[feature_columns]
y = model_df[target_column].astype(str)

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

numeric_features = [
    "price",
    "avg_rating",
    "ratingcount",
    "rating_count_log",
    "description_length",
    "brand_popularity",
    "brand_avg_rating",
    "value_score",
    "rating_available",
    "age_style_fit",
    "occasion_style_fit",
]
categorical_features = ["style_category", "occasion", "age_group", "brand", "colour", "price_band"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded,
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]
            ),
            numeric_features,
        ),
        (
            "cat",
            Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("encoder", OneHotEncoder(handle_unknown="ignore")),
                ]
            ),
            categorical_features,
        ),
    ]
)

knn_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", KNeighborsClassifier()),
    ]
)

param_grid = {
    "classifier__n_neighbors": [5, 7, 9, 11],
    "classifier__weights": ["uniform", "distance"],
    "classifier__metric": ["minkowski"],
}

grid_search = GridSearchCV(
    estimator=knn_pipeline,
    param_grid=param_grid,
    scoring="f1_weighted",
    cv=5,
    n_jobs=1,
    verbose=0,
)

grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_

y_pred = best_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
precision, recall, f1_score, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted")
conf_matrix = confusion_matrix(y_test, y_pred)

print("Best parameters:", grid_search.best_params_)
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-score:  {f1_score:.4f}")
print()
print("Classification report:")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

ConfusionMatrixDisplay(confusion_matrix=conf_matrix, display_labels=label_encoder.classes_).plot(cmap="Oranges")
plt.title("KNN Confusion Matrix")
plt.show()


# %% [markdown]
# ## 8. Add Model Predictions Back To The Dataset
#
# We use the trained KNN model to predict trend labels for all products.
# We also compute the probability of the `High Trend` class, which helps us rank products for the website.

# %%
all_encoded_predictions = best_model.predict(X)
all_prediction_probabilities = best_model.predict_proba(X)
high_trend_index = int(label_encoder.transform(["High Trend"])[0])

df["predicted_trend_label"] = label_encoder.inverse_transform(all_encoded_predictions)
df["high_trend_probability"] = all_prediction_probabilities[:, high_trend_index].round(4)
df["recommendation_score"] = (0.65 * df["trend_score"] + 0.35 * df["high_trend_probability"]).round(4)

display(
    df[
        [
            "name",
            "style_category",
            "occasion",
            "age_group",
            "trend_score",
            "predicted_trend_label",
            "high_trend_probability",
            "recommendation_score",
        ]
    ]
    .sort_values("recommendation_score", ascending=False)
    .head(10)
)


# %% [markdown]
# ## 9. Business Insights
#
# Here we summarize what is trending by age group and by occasion.
# These tables directly support the recommendation sections used on the website.

# %%
trends_by_age = (
    df.groupby(["age_group", "style_category"], as_index=False)["recommendation_score"]
    .mean()
    .sort_values(["age_group", "recommendation_score"], ascending=[True, False])
)
top_age_insights = trends_by_age.groupby("age_group").head(3).reset_index(drop=True)

trends_by_occasion = (
    df.groupby(["occasion", "style_category"], as_index=False)["recommendation_score"]
    .mean()
    .sort_values(["occasion", "recommendation_score"], ascending=[True, False])
)
top_occasion_insights = trends_by_occasion.groupby("occasion").head(3).reset_index(drop=True)

print("Top trends by age group:")
display(top_age_insights)

print("Top trends by occasion:")
display(top_occasion_insights)


# %% [markdown]
# Beginner-friendly business meaning:
#
# - Teen girls usually lean toward short, trendy, and western-inspired categories such as tops and dresses.
# - Young women show stronger performance in versatile styles such as co-ord sets, dresses, and office-friendly looks.
# - Married women often score higher for kurtis, ethnic sets, and festive wear.
# - Older women are more strongly aligned with sarees and traditional wear.
#
# Because the dataset is catalog-heavy, these insights are "trend intelligence from product popularity and ratings"
# rather than true live customer purchase forecasting.


# %% [markdown]
# ## 10. Export Clean Data And Website JSON
#
# GitHub Pages cannot run Python code.
# So the best deployment strategy is:
# 1. train KNN locally in Jupyter
# 2. export JSON files
# 3. let the website read those files with JavaScript

# %%
export_columns = [
    "p_id",
    "name",
    "brand",
    "colour",
    "price",
    "avg_rating",
    "ratingcount",
    "occasion",
    "style_category",
    "age_group",
    "trend_score",
    "trend_label",
    "predicted_trend_label",
    "high_trend_probability",
    "recommendation_score",
    "img",
]

processed_output = df[export_columns].copy()
processed_output.to_csv(PROCESSED_DIR / "fashion_trend_dataset.csv", index=False)


def product_payload(row):
    return {
        "id": str(row["p_id"]) if clean_text(row["p_id"]) else clean_text(row["name"]),
        "product_id": clean_text(row["p_id"]),
        "name": clean_text(row["name"]),
        "category": clean_text(row["style_category"]),
        "age_group": clean_text(row["age_group"]),
        "occasion": clean_text(row["occasion"]),
        "price": round(float(row["price"]), 2),
        "rating": round(float(row["avg_rating"]), 2),
        "rating_count": int(round(float(row["ratingcount"]))),
        "trend_score": round(float(row["trend_score"]), 4),
        "recommendation_score": round(float(row["recommendation_score"]), 4),
        "trend_label": clean_text(row["predicted_trend_label"]),
        "brand": clean_text(row["brand"]),
        "colour": clean_text(row["colour"]),
        "image": pick_best_image(row),
        "description": clean_text(row["description"]),
        "reason_tags": create_reason_tags(row),
    }


recommendations = (
    df.sort_values(["recommendation_score", "avg_rating", "ratingcount"], ascending=False)
    .head(60)
    .apply(product_payload, axis=1)
    .tolist()
)

sample_products = (
    df.sort_values(["recommendation_score", "avg_rating", "ratingcount"], ascending=False)
    .head(8)
    .apply(product_payload, axis=1)
    .tolist()
)

age_showcase = (
    df.assign(
        showcase_score=df.apply(
            lambda row: 0.75 * row["recommendation_score"] + 0.25 * row["age_style_fit"],
            axis=1,
        )
    )
    .groupby(["age_group", "style_category"], as_index=False)["showcase_score"]
    .mean()
    .sort_values(["age_group", "showcase_score"], ascending=[True, False])
)
trends_by_age_export = (
    age_showcase.groupby("age_group")
    .head(4)
    .rename(columns={"showcase_score": "recommendation_score"})
    .to_dict(orient="records")
)

occasion_showcase = (
    df.assign(
        showcase_score=df.apply(
            lambda row: 0.75 * row["recommendation_score"] + 0.25 * row["occasion_style_fit"],
            axis=1,
        )
    )
    .groupby(["occasion", "style_category"], as_index=False)["showcase_score"]
    .mean()
    .sort_values(["occasion", "showcase_score"], ascending=[True, False])
)
trends_by_occasion_export = (
    occasion_showcase.groupby("occasion")
    .head(4)
    .rename(columns={"showcase_score": "recommendation_score"})
    .to_dict(orient="records")
)

profile_predictions = []
for age_group in AGE_GROUPS:
    for occasion in OCCASION_STYLE_PREFERENCES:
        subset = df[(df["age_group"] == age_group) & (df["occasion"] == occasion)].copy()
        if subset.empty:
            subset = df[df["occasion"] == occasion].copy()
        if subset.empty:
            subset = df[df["age_group"] == age_group].copy()
        if subset.empty:
            subset = df.copy()

        style_scores = (
            subset.groupby("style_category", as_index=False)
            .agg(
                trend_score=("trend_score", "mean"),
                recommendation_score=("recommendation_score", "mean"),
                avg_rating=("avg_rating", "mean"),
                product_count=("name", "count"),
            )
        )
        style_scores["profile_score"] = style_scores["style_category"].map(
            lambda style: 0.7 * float(
                style_scores.loc[style_scores["style_category"] == style, "recommendation_score"].iloc[0]
            )
            + 0.15 * preference_score(style, AGE_STYLE_PREFERENCES[age_group])
            + 0.15 * preference_score(style, OCCASION_STYLE_PREFERENCES[occasion])
        )

        best_style_row = style_scores.sort_values(["profile_score", "product_count"], ascending=False).iloc[0]
        predicted_style = best_style_row["style_category"]
        profile_products = (
            subset[subset["style_category"] == predicted_style]
            .sort_values(["recommendation_score", "avg_rating", "ratingcount"], ascending=False)
            .head(4)
            .apply(product_payload, axis=1)
            .tolist()
        )

        profile_predictions.append(
            {
                "age_group": age_group,
                "occasion": occasion,
                "predicted_style": predicted_style,
                "trend_score": round(float(best_style_row["trend_score"]), 3),
                "avg_rating": round(float(best_style_row["avg_rating"]), 2),
                "product_count": int(best_style_row["product_count"]),
                "summary": f"For {age_group.lower()} shoppers looking for {occasion.lower()} outfits, {predicted_style.lower()} are the strongest trending match in this dataset.",
                "products": profile_products,
            }
        )

top_trending_category = (
    df.groupby("style_category", as_index=False)["recommendation_score"]
    .mean()
    .sort_values("recommendation_score", ascending=False)
    .iloc[0]["style_category"]
)

model_summary = {
    "dataset_file": DATA_PATH.name,
    "rows_after_cleaning": int(len(df)),
    "rows_removed_as_duplicates": int(duplicates_removed),
    "model": "KNeighborsClassifier",
    "target": "trend_label",
    "best_params": grid_search.best_params_,
    "accuracy": round(float(accuracy), 4),
    "precision": round(float(precision), 4),
    "recall": round(float(recall), 4),
    "f1_score": round(float(f1_score), 4),
    "class_labels": label_encoder.classes_.tolist(),
    "confusion_matrix": conf_matrix.tolist(),
    "top_trending_category": top_trending_category,
    "assumptions": [
        "The dataset does not include real customer age values, so age groups are created using fashion-business rules from product text and product attributes.",
        "The dataset does not include transaction-level customer history, so ratingCount is used as a popularity proxy and monetary behavior is approximated from price.",
        "GitHub Pages cannot run Python in real time, so the notebook exports static JSON files used by the website.",
    ],
    "note": "Silhouette score is not appropriate here because KNN is used for supervised classification, not clustering.",
}

(WEB_DATA_DIR / "model_summary.json").write_text(json.dumps(model_summary, indent=2))
(WEB_DATA_DIR / "recommendations.json").write_text(json.dumps(recommendations, indent=2))
(WEB_DATA_DIR / "sample_products.json").write_text(json.dumps(sample_products, indent=2))
(WEB_DATA_DIR / "trends_by_age.json").write_text(json.dumps(trends_by_age_export, indent=2))
(WEB_DATA_DIR / "trends_by_occasion.json").write_text(json.dumps(trends_by_occasion_export, indent=2))
(WEB_DATA_DIR / "profile_predictions.json").write_text(json.dumps(profile_predictions, indent=2))

print("Export complete.")
print("Processed CSV:", PROCESSED_DIR / "fashion_trend_dataset.csv")
print("Website JSON folder:", WEB_DATA_DIR)


# %% [markdown]
# ## 11. Final Conclusion
#
# This project is ready for a college submission because it shows a full end-to-end workflow:
# - real dataset loading
# - cleaning and EDA
# - feature engineering with clear assumptions
# - KNN-only model training and evaluation
# - business interpretation of trends
# - frontend integration without a Python backend
#
# Real-time prediction is not used on GitHub Pages because static hosting cannot run Python.
# The best alternative is exactly what this project does:
# export notebook results as JSON and display them in a shopping-style website.
