Place your trained model file here as:

`models/model.pkl`

Recommended setup:
- Save the full preprocessing pipeline and KNN model together in one file.
- Keep the processed dataset at `data/processed/fashion_trend_dataset.csv`.
- The Streamlit app will fall back to exported JSON recommendations when `model.pkl` is not available.
