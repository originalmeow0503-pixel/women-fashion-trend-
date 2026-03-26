# Women's Fashion Trend Prediction Website

This repository contains my final-year project on women’s fashion trend classification and frontend visualization.

The project has two parts:
- a Jupyter/Python workflow for cleaning data, engineering features, training a KNN model, and exporting results
- a static HTML/CSS/JavaScript website that reads those exported JSON files and presents them in a website interface

## What The Project Does

This is not a live commercial forecasting system. It is a student project that explores whether product metadata can be used to create useful proxy trend labels and show the results in a clear frontend.

In simple terms, the workflow is:
1. Load a women’s fashion product dataset from Kaggle.
2. Clean the data and parse useful information from `p_attributes`.
3. Derive features such as `occasion`, `style_category`, `age_group`, `price_band`, and popularity-related measures.
4. Create proxy targets such as `trend_score` and `trend_label` using rules and scoring logic.
5. Train and evaluate a `KNeighborsClassifier`.
6. Export the processed outputs to JSON.
7. Display those exports in a static website hosted on GitHub Pages.

## Important Honesty Note

For panel presentation, these are the most important points to say clearly:

- `trend_label` is an engineered target, not a real customer ground-truth label.
- `age_group` is inferred from product text and attributes because the dataset does not contain real customer age values.
- `occasion` is partly derived from `p_attributes` and keyword rules.
- `ratingCount` and `avg_rating` are used as popularity and quality proxies because transaction-level behavior is not available.
- the website is a static demo that reads exported JSON files; it is not running a live backend model.

## Dataset

Raw dataset location:

- `data/raw/Fashion Dataset.csv`

Useful columns in the dataset:
- `name`
- `price`
- `colour`
- `brand`
- `img`
- `ratingCount`
- `avg_rating`
- `description`
- `p_attributes`

Why these columns matter:
- `name` and `description` help identify style/category keywords
- `price` supports value and price-band features
- `brand` helps with brand-level patterns
- `img` is used in the website cards
- `ratingCount` is used as a popularity proxy
- `avg_rating` is used as a quality proxy
- `p_attributes` contains important fields such as occasion and garment details

## Notebook And ML Workflow

Notebook files:

- [`notebooks/fashion_trend_analysis.ipynb`](notebooks/fashion_trend_analysis.ipynb)
- [`notebooks/fashion_trend_analysis.py`](notebooks/fashion_trend_analysis.py)

Main steps in the notebook:
1. Load the raw CSV from `data/raw/`.
2. Clean duplicates and missing values.
3. Parse `p_attributes` into usable columns.
4. Engineer features such as `occasion`, `style_category`, `age_group`, `price_band`, and popularity/value features.
5. Create `trend_score` and `trend_label`.
6. Train a `KNeighborsClassifier`.
7. Evaluate the classifier with accuracy, precision, recall, and F1-score.
8. Export website-ready JSON files to `web/data/`.

Why KNN was used:
- it is easy to explain in an academic setting
- it fits a similarity-based classification idea
- it shows the effect of encoding, scaling, and feature engineering clearly

Important evaluation note:
- the reported validation accuracy is against derived trend labels, not against real customer behavior labels
- on the homepage, this is shown as `Validation Accuracy (Derived Labels)` to avoid overstating what the metric means

## My Contribution

The parts I implemented in this project include:
- understanding the raw dataset and identifying usable columns
- cleaning the data and handling missing values
- extracting information from `p_attributes`
- designing rule-based features for `occasion`, `age_group`, and `trend_score`
- training and evaluating the KNN classifier
- exporting notebook outputs into JSON for static hosting
- building the frontend in HTML, CSS, and JavaScript
- connecting the exported data to the website without using a backend framework

## Website

Frontend files:

- [`web/index.html`](web/index.html)
- [`web/cart.html`](web/cart.html)
- [`web/checkout.html`](web/checkout.html)
- [`web/styles.css`](web/styles.css)
- [`web/app.js`](web/app.js)

What the website shows:
- homepage with project summary and key exported metrics
- featured recommendations from exported model outputs
- profile-based trend matching by age group and occasion
- age-group recommendation blocks
- occasion-based recommendation blocks
- searchable and filterable product listing
- cart and checkout demo flow using browser storage

## Exported Files Used By The Website

The notebook generates:
- `data/processed/fashion_trend_dataset.csv`
- `web/data/model_summary.json`
- `web/data/recommendations.json`
- `web/data/sample_products.json`
- `web/data/profile_predictions.json`
- `web/data/trends_by_age.json`
- `web/data/trends_by_occasion.json`

The frontend reads these exported files with JavaScript and renders the UI from them.

## How To Run Locally

Install Python dependencies if you want to rerun the notebook:

```bash
pip install -r requirements.txt
```

To preview the website locally, serve the `web/` folder through a local HTTP server:

```bash
python3 -m http.server 8000 --directory web
```

Then open:

- [http://localhost:8000](http://localhost:8000)

Important:
- do not open `web/index.html` directly with `file://`
- browsers often block `fetch()` calls to local JSON files in `file://` mode
- if you use `file://`, the page may show fallback values instead of the exported data

## GitHub Pages Deployment

GitHub Pages is configured through:

- [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml)

That workflow publishes the `web/` folder directly. So the deployed website and the correct local preview should both be served from the same folder structure.

## Folder Structure

```text
New project/
├── .github/
│   └── workflows/
│       └── deploy-pages.yml
├── data/
│   ├── raw/
│   │   └── Fashion Dataset.csv
│   └── processed/
│       └── fashion_trend_dataset.csv
├── notebooks/
│   ├── fashion_trend_analysis.ipynb
│   └── fashion_trend_analysis.py
├── requirements.txt
└── web/
    ├── index.html
    ├── cart.html
    ├── checkout.html
    ├── styles.css
    ├── app.js
    ├── assets/
    └── data/
```

## Limitations

- the dataset is product-centric, not customer-centric
- the target labels are engineered proxies
- age group and some occasion values are inferred rather than observed
- popularity is approximated from ratings and rating count
- the website is static and does not run the model live
- without a backend, GitHub Pages can only display exported results, not fresh predictions

## Future Improvements

- test additional classifiers and compare them fairly against KNN
- use a dataset with real customer purchase history
- add stronger validation around the engineered labels
- store curated product images locally to reduce external image dependency
- add a backend if live prediction is needed in a future version
