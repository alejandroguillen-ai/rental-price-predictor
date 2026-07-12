# Short-Term Rental Price Predictor

> Living document. Updated in every work session with decisions, scope changes, and learnings.

**Last updated:** July 12, 2026
**Project status:** 🟢 Phase 2 in progress (ingestion pipeline)

---

## 1. Context and motivation

Portfolio project aimed at demonstrating end-to-end Data/ML skills: from data ingestion to
deploying a model in production.

## 2. Problem definition

- **Approach:** technical/academic — the goal is to maximize predictive accuracy, not to
  optimize a specific business decision (this is not a "pricing advisor" tool).
- **ML problem:** Supervised regression — predict the price per night from listing
  characteristics.
- **Target variable:** `price` (price per night, in the listing's currency)
- **City/dataset:** **Multi-city / city-agnostic.** The ingestion pipeline accepts any city
  available in the Inside Airbnb catalog as a parameter, instead of being hardcoded to a
  single one. **Development/test city: Las Palmas de Gran Canaria** — *pending
  confirmation of data availability, see Decision Log and Next Steps.*
- **Success metric:** **MAE (Mean Absolute Error)** as the primary metric, computed on the
  original price scale (euros). **RMSE** and **MAPE** are reported as secondary metrics.
  The `price` target is log-transformed (`log(price)`) before training, to reduce the
  impact of outliers (luxury listings).
- **Baseline:** predict the median price of the listing's `neighbourhood` — any model must
  clearly beat this simple baseline to justify its added complexity.

## 3. Scope and known limitations

- The data covers **short-term, Airbnb-style rentals**, not long-term residential leases.
  This distinction will be documented explicitly in the final README.
- Inside Airbnb data is a periodic snapshot (updated every 1–3 months per city), not
  real-time data.

## 4. Roadmap by phase

| Phase | Goal | Status |
|---|---|---|
| 1. Problem and data definition | Nail down city, target, metrics, baseline | ✅ Done |
| 2. Ingestion and cleaning pipeline | Reproducible download and cleaning scripts | 🟡 In progress |
| 3. EDA and feature engineering | Documented exploration + new features | ⬜ Pending |
| 4. Training with experiment tracking (MLflow) | Multiple models, logged experiments | ⬜ Pending |
| 5. Evaluation and model selection | Comparison and justification of final model | ⬜ Pending |
| 6. FastAPI service | `/predict` + `/health` endpoints | ⬜ Pending |
| 7. Tests and Docker | pytest + containerization | ⬜ Pending |
| 8. Documentation and deployment | Final README + live demo | ⬜ Pending |

## 5. Required knowledge and tools

| Area | Tool/Concept | Required level |
|---|---|---|
| Data | Python, pandas, requests | Already have a base |
| Version control | Git/GitHub (commits, .gitignore, branches) | Review best practices |
| Environment | venv or poetry, `requirements.txt` | Basic |
| Modeling | scikit-learn, XGBoost | Reinforce as we go |
| Experiment tracking | MLflow | New — learned in Phase 4 |
| API | FastAPI, Pydantic | New |
| Testing | pytest | Review |
| Containers | Docker (basic Dockerfile) | New |
| Deployment | Render or Railway (free tier) | New — covered in Phase 8 |

## 6. Decision Log

> Every significant decision is logged here with date, context, and discarded alternatives.

### 2026-07-12 — Data source
- **Decision:** Use Inside Airbnb instead of scraping listing portals or using official
  government data (SERPAVI/INE).
- **Alternatives considered:** SERPAVI/INE (official data, but no per-listing detail);
  scraping Idealista/Fotocasa (discarded due to legal/ToS risk).
- **Reason:** Legal, well-known dataset, rich in features, and periodically updated —
  allows building a real ingestion pipeline with no legal risk.

### 2026-07-12 — Geographic scope: city-agnostic
- **Decision:** The ingestion pipeline will be parametrized by city (any city in the Inside
  Airbnb catalog), instead of being tied to a single one.
- **Alternatives considered:** Hardcoding a single city (simpler, but less generalizable
  and less representative of good engineering practice).
- **Reason:** Inside Airbnb exposes data via a predictable country/region/city URL, making
  a generic download function feasible. Adds engineering value (parametrization, input
  validation) at no significant extra cost.

### 2026-07-12 — Business vs. technical framing
- **Decision:** The model's goal is to maximize predictive accuracy (technical approach),
  not to solve a specific business decision.
- **Alternatives considered:** Framing it as a "pricing assistant for hosts" or an
  "under/overpricing detector" (shelved for now — could be added later as an extension if
  the base model performs well).
- **Reason:** Explicit preference of the project's author for a technical/academic
  approach.

### 2026-07-12 — Evaluation metric and target transformation
- **Decision:** Primary metric is MAE (in euros, original scale). RMSE and MAPE as
  secondary metrics. `log(price)` will be used as the training target.
- **Alternatives considered:** RMSE as the primary metric (discarded as primary for being
  very sensitive to luxury-listing outliers, which would distort the evaluation).
- **Reason:** MAE is more robust to the long tail of the price distribution and easier to
  communicate ("on average, we're off by X€"). Log-transforming is standard practice for
  skewed price variables.

### 2026-07-12 — Development city
- **Decision:** Las Palmas de Gran Canaria as the development/test city while building the
  pipeline (the code itself remains city-agnostic).
- **Reason:** The author's local city, which makes manual sanity-checking of results easier
  ("does this price make sense for a neighbourhood I know?").
- **⚠️ Status update (same day):** Could not confirm via public documentation that Inside
  Airbnb actually covers Las Palmas de Gran Canaria / the Canary Islands — see the entry
  below and "Next steps".

### 2026-07-12 — Repository structure
- **Decision:** `src-layout` structure inspired by cookiecutter-data-science:
  `data/{raw,processed}`, `notebooks/`, `src/{data,features,models,api}`, `tests/`.
  Raw and processed data are excluded from git (`.gitignore`); only the folder structure is
  versioned (`.gitkeep`).
- **Alternatives considered:** Everything in loose notebooks with no `src/` (discarded — it
  doesn't demonstrate the ability to write reusable, production-style code); a flat
  structure with no subfolders in `src/` (discarded — less clear about each module's
  responsibility).
- **Reason:** Clearly separating ingestion / features / modeling / API makes each part
  independently testable and matches the pattern expected in a "serious" ML repo. Every
  module in `src/` already has a docstring explaining its future responsibility, so the
  design is documented before the logic is written.

### 2026-07-12 — Snapshot auto-detection via regex over the HTML page
- **Decision:** `fetch_city_catalog()` downloads Inside Airbnb's "Get the Data" page and
  extracts, using a regular expression, every URL matching the pattern
  `https://data.insideairbnb.com/{country}/{region}/{city}/{date}/data/listings.csv.gz`.
  Only the first match per city is kept (the most recent one, since the page lists the
  current snapshot before any archived ones).
- **Alternatives considered:** Parsing the HTML with BeautifulSoup and walking the DOM
  (shelved for now — the URL is self-describing, so we don't need the full HTML tree, just
  to extract the text pattern); keeping a hardcoded URL table per city (discarded — breaks
  the city-agnostic approach and would go stale).
- **Open risk:** Could not confirm that Inside Airbnb covers Las Palmas de Gran Canaria —
  it doesn't appear in the public documentation reviewed so far (other Spanish regions are
  covered: Barcelona, Girona, Euskadi). The script itself (`ingest.py`, run directly)
  checks this on startup and lists similar city slugs if it isn't found. **Needs to be
  verified next time it's run with network access** — if unavailable, we'll pick a
  different development city (see "Next steps").

### 2026-07-12 — Project language
- **Decision:** All project documentation and code comments switched to English
  (previously Spanish), to make the portfolio piece accessible to a wider audience of
  reviewers/recruiters.
- **Reason:** English is the de facto standard for software portfolios aimed at an
  international audience.

---

## Next steps

- [x] Choose data source (Inside Airbnb)
- [x] Define geographic scope (city-agnostic, dev with Las Palmas de Gran Canaria)
- [x] Define problem framing (technical, maximize accuracy)
- [x] Define success metric and baseline (MAE primary, log-transform, per-neighbourhood
      baseline)
- [x] Design the repository folder structure
- [ ] Write the generic Inside Airbnb download function (Phase 2)
- [ ] **Run `ingest.py` with network access and confirm whether Las Palmas de Gran Canaria
      is available; if not, pick an alternative development city**
- [ ] Set up virtual environment and install `requirements.txt`
- [ ] Ingest `calendar.csv.gz` and `reviews.csv.gz` as well (optional, Phase 3)
