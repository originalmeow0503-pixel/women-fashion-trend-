# Women's Fashion Trend Prediction Website

This project is a college-ready end-to-end machine learning and frontend system for predicting trending women's clothing preferences by age group and occasion.

It combines:
- Jupyter Notebook + Python for data cleaning, EDA, feature engineering, KNN modeling, evaluation, and export
- HTML, CSS, and JavaScript for a static shopping-style website
- precomputed JSON files so the project works on GitHub Pages without a Python backend

## Project Overview

Business idea:
an AI-assisted fashion website that identifies what styles are trending for different women based on age group, occasion, and product popularity.

Examples used in the project:
- Teen girls: tops, dresses, shorts, co-ord styles
- Young women: co-ord sets, dresses, office-ready looks, casual tops
- Married women: kurtis, ethnic sets, festive wear
- Older women: sarees, traditional wear, classic ethnic styles

Main occasions used in the website:
- Casual
- Party
- Wedding
- Festive
- Office
- Vacation
- Daily Wear

## Dataset Used

The notebook is built around the Kaggle CSV placed here:

`data/raw/Fashion Dataset.csv`

Actual columns found in the dataset:
- `p_id`
- `name`
- `price`
- `colour`
- `brand`
- `img`
- `ratingCount`
- `avg_rating`
- `description`
- `p_attributes`

Most useful columns for this project:
- `name`: helps identify product type
- `price`: numeric feature for KNN
- `brand`: useful for brand popularity features
- `colour`: optional categorical context
- `img`: used in the website product cards
- `ratingCount`: popularity proxy
- `avg_rating`: quality/review proxy
- `description`: keyword-based feature engineering
- `p_attributes`: the richest column because it contains `Occasion`, `Top Type`, `Bottom Type`, `Main Trend`, and more

## Assumptions

The dataset does not directly contain all business columns needed for live trend prediction, so the notebook makes these clear assumptions:

- There is no real customer age column, so `age_group` is created using rule-based fashion logic from product text and attributes.
- There is no true customer purchase history or customer ID, so `ratingCount` is used as a popularity proxy.
- There is no direct trend label, so the notebook creates `trend_score` and `trend_label` logically from ratings, popularity, value, and style fit.
- There is no reliable single `occasion` column outside the attributes, so occasion labels are created from `p_attributes` and product keywords.

## Machine Learning Workflow

The notebook file is:

- [fashion_trend_analysis.ipynb](/Users/vidhidhawan/Documents/New project/notebooks/fashion_trend_analysis.ipynb)

There is also a Python-source version of the same notebook:

- [fashion_trend_analysis.py](/Users/vidhidhawan/Documents/New project/notebooks/fashion_trend_analysis.py)

Notebook steps:
1. Load the raw Kaggle dataset from `data/raw/`.
2. Inspect columns and explain which fields are useful.
3. Clean the data:
   remove duplicates, fill missing values, and cap outliers in `price` and `ratingCount`.
4. Parse `p_attributes` into usable columns.
5. Create business features:
   `occasion`, `style_category`, `age_group`, `price_band`, `brand_popularity`, `value_score`, and more.
6. Create the prediction target:
   `trend_label` with classes `Classic Stable`, `Rising Trend`, and `High Trend`.
7. Train a `KNeighborsClassifier` only.
8. Evaluate the model using:
   accuracy, precision, recall, F1-score, classification report, and confusion matrix.
9. Export cleaned CSV and frontend JSON files for the website.

Why KNN is used:
- easy to explain in a college project
- works well when similar products should receive similar trend labels
- requires proper scaling and encoding, which the notebook demonstrates clearly

Why silhouette score is not used:
- silhouette score is for clustering
- this project uses supervised KNN classification
- so classification metrics are the correct evaluation choice

## Website

The static website lives in:

- [index.html](/Users/vidhidhawan/Documents/New project/web/index.html)
- [cart.html](/Users/vidhidhawan/Documents/New project/web/cart.html)
- [checkout.html](/Users/vidhidhawan/Documents/New project/web/checkout.html)
- [styles.css](/Users/vidhidhawan/Documents/New project/web/styles.css)
- [app.js](/Users/vidhidhawan/Documents/New project/web/app.js)

Website features:
- landing page with branding and hero banner
- trending recommendations section
- age-group-based recommendation section
- occasion-wise recommendation section
- searchable and filterable product listing
- add to cart
- cart summary page
- checkout form with address and payment UI
- responsive design
- static JSON integration for GitHub Pages

Brand tone used:
- polished
- fashion-focused
- modern
- submission-ready for a final-year project demo

## Folder Structure

```text
New project/
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   ├── README.md
│   ├── raw/
│   │   ├── Fashion Dataset.csv
│   │   └── README.md
│   └── processed/
│       └── fashion_trend_dataset.csv
├── models/
├── notebooks/
│   ├── fashion_trend_analysis.ipynb
│   └── fashion_trend_analysis.py
└── web/
    ├── index.html
    ├── cart.html
    ├── checkout.html
    ├── styles.css
    ├── app.js
    ├── assets/
    └── data/
        ├── model_summary.json
        ├── recommendations.json
        ├── sample_products.json
        ├── trends_by_age.json
        ├── trends_by_occasion.json
        └── profile_predictions.json
```

## How Notebook Output Connects To The Website

GitHub Pages cannot run Python or a Jupyter model live.

So this project uses the best static-hosting alternative:

1. Train and evaluate the KNN model locally in Jupyter.
2. Export results into JSON files inside `web/data/`.
3. Load those JSON files using JavaScript in the website.
4. Display recommendations, top trends, and precomputed profile predictions in the UI.

This means:
- no backend is required
- the website stays GitHub Pages compatible
- the frontend still shows model-driven outputs

## Output Files Generated By The Notebook

The notebook exports:
- `data/processed/fashion_trend_dataset.csv`
- `web/data/model_summary.json`
- `web/data/recommendations.json`
- `web/data/sample_products.json`
- `web/data/trends_by_age.json`
- `web/data/trends_by_occasion.json`
- `web/data/profile_predictions.json`

## How To Run The Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the notebook:
1. Open the project in VS Code or Jupyter.
2. Open [fashion_trend_analysis.ipynb](/Users/vidhidhawan/Documents/New project/notebooks/fashion_trend_analysis.ipynb).
3. Run all cells from top to bottom.

Preview the website locally:
1. Open the `web/` folder using VS Code Live Server, or serve the project with a static file server.
2. Open `index.html` through that local server.

Important:
opening the HTML file directly with `file://` may block `fetch()` calls for JSON. Use Live Server or any simple local web server while testing.

## GitHub Pages Deployment Steps

This project now includes a ready-made workflow:

- [.github/workflows/deploy-pages.yml](/Users/vidhidhawan/Documents/New project/.github/workflows/deploy-pages.yml)

It deploys the `web/` folder directly to GitHub Pages whenever you push to the `main` branch.

Follow these steps:
1. Create a new GitHub repository.
2. Push this project to that repository.
3. In GitHub, open `Settings > Pages`.
4. For the source, choose `GitHub Actions`.
5. Push again if needed, or open the `Actions` tab and let the workflow run.
6. After the workflow succeeds, GitHub will publish your site URL.

Example commands:

```bash
cd "/Users/vidhidhawan/Documents/New project"
git add .
git commit -m "Add women fashion trend prediction project"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

After pushing:
1. Open the GitHub repository.
2. Go to `Settings > Pages`.
3. Set the source to `GitHub Actions`.
4. Wait for the `Deploy GitHub Pages` workflow to finish.
5. Open the Pages URL shown by GitHub.

## Limitations

- The dataset is product-centric, not customer-centric.
- Age groups are inferred using business rules, not real customer age data.
- Purchase behavior is approximated using ratings and rating count.
- Real-time prediction is not available on GitHub Pages because there is no Python backend.
- Occasion labels are partly rule-based because the dataset stores many details inside `p_attributes`.

## Future Improvements

- Add a true customer dataset with age, purchases, and order history
- add seasonal trend analysis if month or date fields become available
- build a Flask or FastAPI backend for real-time prediction
- add collaborative filtering or hybrid recommendation logic in a future version
- improve image asset handling by downloading curated local product images
- add user login, wishlist, and order history for a fuller ecommerce experience
