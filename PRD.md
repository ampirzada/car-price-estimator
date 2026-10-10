# PRD: Used-Car Price Estimator

## Problem
Buyers and sellers guess at used-car prices. Listings vary a lot by age, mileage, and specs, so it is hard to know what a fair price is.

## Who it's for
Anyone buying or selling a used car who wants a quick price check before negotiating.

## Goals
- Give a fair price estimate from real listings.
- Be simple: enter basic car details, get a price.
- Be honest about limits when we have little similar data.

## In scope
- Input: brand, model, year, mileage, fuel type, transmission.
- Output: one estimated price in USD, plus a price range.
- Estimates learned from `used-cars.csv` only.
- A simple way to enter the car and see the result.

## Out of scope
- Accident history, title status, condition photos, or location pricing.
- Live listings, dealer feeds, or guaranteed selling prices.
- Accounts, saved searches, or payment features.

## How we'll know it works
- A user can enter the six inputs and gets a price plus a range.
- Estimates are close to real listing prices for common cars when tested on held-out rows.
- The app says when confidence is low, for example rare brands or very old or high-mileage cars.
