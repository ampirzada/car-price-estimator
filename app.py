"""Used-car price estimator: Streamlit UI + RandomForest model trained on used-cars.csv."""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

CSV_PATH = Path(__file__).with_name("used-cars.csv")
FEATURE_COLS = ["brand", "model", "year", "mileage_miles", "fuel_type", "transmission"]
TARGET_COL = "price_usd"
CATEGORICAL_COLS = ["brand", "model", "fuel_type", "transmission"]
NUMERIC_COLS = ["year", "mileage_miles"]


@st.cache_resource
def load_data():
    df = pd.read_csv(CSV_PATH)
    return df


@st.cache_resource
def train_model():
    df = load_data()
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]
    preprocess = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLS),
            ("num", "passthrough", NUMERIC_COLS),
        ]
    )
    model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    pipeline = Pipeline([("preprocess", preprocess), ("model", model)])
    pipeline.fit(X, y)
    stats = {
        "median_year": float(df["year"].median()),
        "median_mileage": float(df["mileage_miles"].median()),
        "median_price": float(df["price_usd"].median()),
        "brand_counts": df["brand"].value_counts().to_dict(),
        "min_year": int(df["year"].min()),
        "max_year": int(df["year"].max()),
    }
    return pipeline, stats


def predict_with_range(pipeline, row):
    X = pd.DataFrame([row])
    estimate = float(pipeline.predict(X)[0])
    trees = pipeline.named_steps["model"].estimators_
    transformed = pipeline.named_steps["preprocess"].transform(X)
    tree_preds = np.array([t.predict(transformed)[0] for t in trees])
    low = float(np.percentile(tree_preds, 10))
    high = float(np.percentile(tree_preds, 90))
    return estimate, low, high


def build_factors(row, estimate, stats, df):
    overall_median = stats["median_price"]
    candidates = []
    median_mileage = stats["median_mileage"]
    if row["mileage_miles"] <= median_mileage * 0.5:
        candidates.append((3, "Low mileage added a lot of value."))
    elif row["mileage_miles"] < median_mileage * 0.85:
        candidates.append((2, "Below-average mileage added some value."))
    elif row["mileage_miles"] > median_mileage * 2.0:
        candidates.append((3, "Very high mileage pulled the price down a lot."))
    elif row["mileage_miles"] > median_mileage * 1.3:
        candidates.append((2, "High mileage pulled the price down."))
    else:
        candidates.append((1, "Mileage is close to average, so it moved the price only a little."))

    median_year = stats["median_year"]
    if row["year"] >= median_year + 6:
        candidates.append((3, "Very recent year added a lot of value."))
    elif row["year"] >= median_year + 2:
        candidates.append((2, "Newer year added some value."))
    elif row["year"] <= median_year - 10:
        candidates.append((3, "Old year pulled the price down a lot."))
    elif row["year"] <= median_year - 4:
        candidates.append((2, "Older year pulled the price down."))
    else:
        candidates.append((1, "Year is close to average, so it moved the price only a little."))

    brand_median = df.loc[df["brand"] == row["brand"], "price_usd"].median()
    if pd.notna(brand_median):
        if brand_median >= overall_median * 1.5:
            candidates.append((2, f"{row['brand']} listings usually cost more, which pushed the price up."))
        elif brand_median <= overall_median * 0.6:
            candidates.append((2, f"{row['brand']} listings usually cost less, which pulled the price down."))
        else:
            candidates.append((1, f"{row['brand']} is priced near average, so brand moved the price only a little."))
    brand_count = stats["brand_counts"].get(row["brand"], 0)
    if brand_count < 10:
        candidates.append((3, f"Only {brand_count} listings for {row['brand']}, so this part is uncertain."))

    same_model = df[(df["brand"] == row["brand"]) & (df["model"] == row["model"])]
    if len(same_model) == 0:
        candidates.append((2, "This model was not seen for that brand, which makes the estimate less certain."))
    else:
        model_median = same_model["price_usd"].median()
        if pd.notna(model_median) and pd.notna(brand_median):
            if model_median >= brand_median * 1.3:
                candidates.append((2, "This trim usually costs more than others from the same brand, which pushed the price up."))
            elif model_median <= brand_median * 0.7:
                candidates.append((2, "This trim usually costs less than others from the same brand, which pulled the price down."))

    fuel_median = df.loc[df["fuel_type"] == row["fuel_type"], "price_usd"].median()
    if pd.notna(fuel_median) and abs(fuel_median - overall_median) >= overall_median * 0.3:
        direction = "up" if fuel_median > overall_median else "down"
        candidates.append((1, f"Fuel type ({row['fuel_type']}) usually prices {direction}, a small effect."))

    candidates.sort(key=lambda item: -item[0])
    factors = [text for _, text in candidates[:3]]
    while len(factors) < 3:
        factors.append("Other details matched typical listings, so they moved the price only a little.")
    return factors


def find_similar_listings(df, row, estimate, n=3):
    same_model = df[(df["brand"] == row["brand"]) & (df["model"] == row["model"])].copy()
    same_brand = df[df["brand"] == row["brand"]].copy()
    picked = pd.DataFrame()
    if not same_model.empty:
        same_model["price_diff"] = (same_model["price_usd"] - estimate).abs()
        picked = same_model.nsmallest(n, "price_diff")
    if len(picked) < n and not same_brand.empty:
        same_brand["price_diff"] = (same_brand["price_usd"] - estimate).abs()
        extra = same_brand[~same_brand.index.isin(picked.index)].nsmallest(n - len(picked), "price_diff")
        picked = pd.concat([picked, extra])
    if len(picked) < n:
        rest = df.copy()
        rest["price_diff"] = (rest["price_usd"] - estimate).abs()
        extra = rest[~rest.index.isin(picked.index)].nsmallest(n - len(picked), "price_diff")
        picked = pd.concat([picked, extra])
    cols = ["brand", "model", "year", "mileage_miles", "fuel_type", "transmission", "price_usd"]
    return picked[cols].reset_index(drop=True)


def confidence_level(row, stats, df):
    reasons = []
    if row["year"] <= 2004:
        reasons.append("very old car with few comparable listings")
    if row["mileage_miles"] >= 200000:
        reasons.append("very high mileage")
    brand_count = stats["brand_counts"].get(row["brand"], 0)
    if brand_count < 10:
        reasons.append(f"rare brand ({brand_count} listings)")
    same_model = df[(df["brand"] == row["brand"]) & (df["model"] == row["model"])]
    if len(same_model) == 0:
        reasons.append("unseen brand-plus-model combination")
    if len(reasons) >= 2:
        level = "Low"
    elif len(reasons) == 1:
        level = "Medium"
    else:
        level = "High"
    return level, reasons


st.title("Used-Car Price Estimator")
st.write("Enter the car details. The estimate is learned from real listings in used-cars.csv.")

df = load_data()
pipeline, stats = train_model()

brands = sorted(df["brand"].dropna().unique().tolist())
fuel_types = sorted(df["fuel_type"].dropna().unique().tolist())
transmissions = sorted(df["transmission"].dropna().unique().tolist())

brand = st.selectbox("Brand", brands, index=brands.index("Honda") if "Honda" in brands else 0)
brand_models = sorted(df.loc[df["brand"] == brand, "model"].dropna().unique().tolist())
model = st.selectbox("Model", brand_models)
fuel_type = st.selectbox("Fuel type", fuel_types)
transmission = st.selectbox("Transmission", transmissions)
year = st.number_input("Year", min_value=1998, max_value=2024, value=2019, step=1)
mileage = st.number_input("Mileage (miles)", min_value=0, value=62000, step=1000)

if st.button("Estimate price"):
    errors = []
    if not brand:
        errors.append("Pick a brand from the list.")
    if not model:
        errors.append("Pick a model from the list.")
    if year < 1998 or year > 2024:
        errors.append("Year must be between 1998 and 2024.")
    if mileage < 0:
        errors.append("Mileage cannot be negative.")
    if errors:
        for message in errors:
            st.error(message)
    else:
        row = {
            "brand": brand,
            "model": model,
            "year": int(year),
            "mileage_miles": int(mileage),
            "fuel_type": fuel_type,
            "transmission": transmission,
        }
        estimate, low, high = predict_with_range(pipeline, row)
        st.metric("Estimated price (USD)", f"${estimate:,.0f}")
        st.write(f"Expected range: ${low:,.0f} – ${high:,.0f}")
        level, reasons = confidence_level(row, stats, df)
        if level == "High":
            st.success("Confidence: High — plenty of similar listings.")
        elif level == "Medium":
            st.warning(f"Confidence: Medium — {'; '.join(reasons)}.")
        else:
            st.warning(f"Confidence: Low — {'; '.join(reasons)}.")
        st.subheader("3 biggest factors")
        for factor in build_factors(row, estimate, stats, df):
            st.write(f"- {factor}")
        st.subheader("3 most similar real listings")
        st.write("Same model first, closest in price to the estimate.")
        st.dataframe(find_similar_listings(df, row, estimate))
