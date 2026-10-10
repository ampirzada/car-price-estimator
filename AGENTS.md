# AGENTS.md

Repo contains only `used-cars.csv` (~3,915 rows + header, ~273 KB). No code, README, manifests, build/test/lint config, or CI.

## Data

- File: `used-cars.csv`, header: `brand,model,year,mileage_miles,fuel_type,transmission,accident_reported,clean_title,price_usd`
- Categorical values are messy / non-normalized (e.g. `transmission` has many free-text variants like `A/T`, `5-Speed A/T`, `F`; `clean_title` uses `Yes/No/Unknown`). Do not assume a fixed enum — inspect actual values before encoding.
- No train/test split or schema docs exist. Treat the CSV as the single source of truth.

## Working here

- No package manager, test runner, or formatter is configured. Do not add tooling unless asked.
- For quick inspection use stdlib only, e.g. `python3 -c` with `csv`/`collections`; do not assume `pandas`/`numpy`/`sklearn` are installed.
- `used-cars.csv` is the only dataset file — do not create `*.csv` derivatives without being asked.
