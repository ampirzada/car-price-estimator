# Functional Requirements: Used-Car Price Estimator

Based on `PRD.md` and the columns in `used-cars.csv` (3,915 rows).

## 1. Inputs

The user must enter these six values. Names match the CSV columns.

- **brand**: must be a brand found in the dataset. There are 56, including Ford, BMW, Mercedes-Benz, Chevrolet, Audi, Toyota, Honda, Jeep, and rare ones like Lucid, Karma, and smart. Reject empty or unknown brands.
- **model**: free text, for example `Accord EX-L` or `4Runner Limited`. Best results when it matches a model already listed under that brand. If the model was never seen for that brand, continue but mark confidence low.
- **year**: whole year from 1998 to 2024, the range seen in the data.
- **mileage_miles**: whole miles, 0 or more. Data covers 100 to 300,000 miles.
- **fuel_type**: one of the 6 values in the data: `Gasoline`, `Hybrid`, `Diesel`, `E85 Flex Fuel`, `Plug-In Hybrid`, `Unknown`. Use `Unknown` for electric cars, which are labeled `Unknown` in the data (for example Tesla, Lucid).
- **transmission**: one of the labels in the data. There are 60 messy variants. Common ones are `A/T`, `8-Speed A/T`, `6-Speed A/T`, `6-Speed M/T`, `Automatic`, `7-Speed A/T`, `CVT Transmission`. The user picks the closest label from a list.

Not inputs: `accident_reported`, `clean_title`, and `price_usd` exist in the CSV but the user does not enter them, per `PRD.md` out of scope.

## 2. Output

Every valid request returns:

- **Estimated price**: a single USD value, rounded to the nearest dollar.
- **Low–high range**: a narrower range for common cars, a wider range when data is thin.
- **Top factors**: 2–3 short plain-language reasons, for example low mileage pushed the price up, old year pushed the price down, or rare brand so the range is wide.
- **Confidence note**: high, medium, or low, with one sentence when low.

## 3. Unusual inputs

- **Very old car** (around 1998–2004): allow it, expect a low estimate, a wide range, and low confidence. If year is before 1998, reject it and ask for 1998–2024.
- **Very high mileage** (around 200,000–300,000 miles, or above 300,000): allow it, expect a low estimate pulled toward the bottom of the data (lowest price seen is $2,000), a wide range, and low confidence.
- **Rare brand or unseen brand-plus-model** (for example Lucid, Karma, smart, or a model never seen for that brand): allow it if the brand exists, but return a wide range and low confidence saying there are few similar listings.
- **Missing or invalid input** (empty brand/model, year outside 1998–2024, negative mileage, fuel or transmission not in the lists above): do not estimate. Show which field is wrong and what values are allowed.

## 4. Examples

1. **Common car — expect a tight range, high confidence**
   Input: Honda, Accord EX-L, 2019, 62,000 miles, Gasoline, A/T.
   Expect: price near the high-teens to low-20s thousands, narrow low–high range, factors like recent year and average mileage, high confidence.

2. **Very old and high mileage — expect a low price, wide range, low confidence**
   Input: Toyota, 4Runner 4WD, 1999, 267,000 miles, Gasoline, 5-Speed M/T.
   Expect: low estimate under $10,000, wide range, factors like very old year and very high mileage pulling the price down, low confidence.

3. **Rare brand with little data — expect a wide range and low confidence**
   Input: Lucid, Air Pure, 2023, 1,300 miles, Unknown, A/T.
   Expect: high estimate (only 3 Lucid rows exist, near $87,000–$120,000), very wide range, factors like new year and very low mileage pushing up but rare brand noted, low confidence with a message that few similar listings exist.
