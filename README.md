# Short-Term Rental Price Predictor

> ⚠️ Work in progress — this README will be filled in as each phase is completed.
> See `PROJECT_PLAN.md` for the full roadmap and the technical decision log.

## Summary

A regression model that predicts the price per night of an Airbnb-style listing, using
open data from [Inside Airbnb](http://insideairbnb.com/). The ingestion pipeline is
**city-agnostic**: it works with any city in the Inside Airbnb catalog, not just the one
used during development.

## Repository structure

```
rental-price-predictor/
├── data/
│   ├── raw/            # Downloaded, unmodified data (contents not version-controlled)
│   └── processed/      # Cleaned data, ready for feature engineering
├── notebooks/          # Exploration and prototyping (EDA, quick tests)
├── src/
│   ├── data/            # Ingestion and cleaning (ingest.py)
│   ├── features/        # Feature engineering (build_features.py)
│   ├── models/           # Training and evaluation (train.py, evaluate.py)
│   └── api/              # FastAPI service (main.py)
├── tests/               # pytest tests
├── PROJECT_PLAN.md       # Roadmap and decision log
├── requirements.txt
├── .gitignore
└── README.md
```

## Current status

See the phase table in `PROJECT_PLAN.md`.

## How to run (will be completed in later phases)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
