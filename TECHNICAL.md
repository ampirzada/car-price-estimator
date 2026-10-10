# Technical Plan: Used-Car Price Estimator

Beginner-friendly Python app. No implementation yet, just the plan.
Spec sources are PRD.md for what to build and FUNCTIONAL.md for inputs, outputs, and edge cases.

## 1. Files to create

- app.py: the whole app in one file. It loads the data, trains the model once at startup, shows the six input fields in the browser, and shows the estimate plus range, factors, and confidence.
- requirements.txt: the list of Python libraries so anyone can install the same setup locally or on Railway.
- Existing file we reuse: used-cars.csv. Do not edit it. It stays the only dataset.

No other files are needed for the first version. No database, no extra config files.

## 2. Which CSV columns the model uses

- Inputs the model learns from: brand, model, year, mileage_miles, fuel_type, transmission. These are exactly the six inputs from FUNCTIONAL.md.
- Target the model predicts: price_usd.
- Ignored columns: accident_reported and clean_title. They exist in the CSV but PRD.md puts them out of scope, so the model does not use them.

Notes for beginners: year and mileage_miles are numbers and go in as-is. Brand, model, fuel_type, and transmission are words, so the app converts them to a numeric form the model can use via one-hot encoding. Transmission and model have many messy variants, so the app must use the exact labels from the CSV and not invent new ones.

## 3. How the model trains when the app starts

When the browser app starts, it does this once and keeps the result in memory:

1. Load used-cars.csv with pandas.
2. Split columns into inputs (the six above) and target (price_usd).
3. Convert the word columns to model-ready form and train a RandomForestRegressor from scikit-learn on all rows.
4. Keep the trained model in Streamlit caching so it trains only once, not on every button click.

Prediction per user request: take the six inputs, convert them the same way, ask the forest for a price, then derive the extras from FUNCTIONAL.md. The low-high range comes from the spread of the individual trees in the forest, narrow when trees agree and wide when they disagree. Top factors come from a simple explanation such as comparing the input to dataset averages and the model's feature importance. Confidence is high when the brand and model have many similar rows and the year and mileage are inside common ranges, and low for very old cars, very high mileage, or rare brands as listed in FUNCTIONAL.md.

## 4. Libraries needed

Only three libraries, listed in requirements.txt:

- pandas for loading and handling used-cars.csv.
- scikit-learn for the RandomForestRegressor model and its helpers.
- streamlit for the browser screen with input fields and result display.

Python 3.14 is already in use here. The existing .venv virtual environment is reused. No database driver or other framework is needed.

## 5. How to run it locally on Windows

Use the existing .venv in this folder. The steps are: activate the venv, install from requirements.txt once, then start the Streamlit app and open the browser address it prints.

Activation uses the PowerShell activate script inside .venv Scripts. Installing uses pip with requirements.txt. Starting uses Streamlit to run app.py. The app then trains on used-cars.csv at startup and shows the six input fields.

## 6. Later deploy to Railway

No extra deploy files are needed for the first deploy. Railway is enough with:

- requirements.txt so Railway installs pandas, scikit-learn, and streamlit automatically.
- A start command that runs Streamlit on the port Railway provides and listens on all addresses.

The same app.py runs unchanged. Railway builds from requirements.txt, runs the start command, and the app trains at startup exactly like it does locally.
