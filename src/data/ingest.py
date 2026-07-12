"""
Data ingestion module.

Responsibility: download raw data from Inside Airbnb for a given city and
save it to data/raw/, unmodified.

Design (city-agnostic, see PROJECT_PLAN.md decision log):
Inside Airbnb's "Get the Data" page lists, per city, a self-describing
download URL of the form:

    https://data.insideairbnb.com/{country}/{region}/{city}/{date}/data/listings.csv.gz

Rather than hardcoding a URL per city, we scrape that page once, extract
every such URL with a regex, and keep only the first (i.e. most recent)
snapshot per city slug. This auto-detects the latest available date for
any city without needing to know it in advance.
"""

from __future__ import annotations

import re
from pathlib import Path

import requests

GET_DATA_URL = "https://insideairbnb.com/get-the-data/"

# Captures country / region / city slug / snapshot date from a listings.csv.gz URL.
DATA_URL_PATTERN = re.compile(
    r"https://data\.insideairbnb\.com/"
    r"(?P<country>[^/]+)/(?P<region>[^/]+)/(?P<city>[^/]+)/"
    r"(?P<date>\d{4}-\d{2}-\d{2})/data/listings\.csv\.gz"
)


def fetch_city_catalog() -> dict[str, dict[str, str]]:
    """
    Scrape the Inside Airbnb 'Get the Data' page and build a catalog of
    the latest available snapshot per city.

    Returns
    -------
    dict[str, dict]
        Mapping of city slug -> {"country", "region", "date", "url"}.
        Only the first (most recent) snapshot found per city is kept —
        the page lists the current snapshot before any archived ones.
    """
    response = requests.get(GET_DATA_URL, timeout=30)
    response.raise_for_status()

    catalog: dict[str, dict[str, str]] = {}
    for match in DATA_URL_PATTERN.finditer(response.text):
        city = match.group("city")
        if city in catalog:
            continue  # keep only the first (= latest) snapshot per city
        catalog[city] = {
            "country": match.group("country"),
            "region": match.group("region"),
            "date": match.group("date"),
            "url": match.group(0),
        }
    return catalog


def list_available_cities() -> list[str]:
    """Return the sorted list of city slugs currently available."""
    return sorted(fetch_city_catalog().keys())


def get_listings(city: str, save_dir: str = "data/raw") -> Path:
    """
    Download the latest listings.csv.gz for `city` and save it under
    `save_dir`.

    Parameters
    ----------
    city : str
        Inside Airbnb city slug, e.g. "barcelona", "amsterdam". Slugs are
        lowercase and hyphenated. Use list_available_cities() to check
        valid options and their exact spelling.
    save_dir : str
        Directory to save the downloaded file into (created if missing).

    Returns
    -------
    Path
        Path to the downloaded .csv.gz file.

    Raises
    ------
    ValueError
        If `city` is not found in the current catalog.
    """
    catalog = fetch_city_catalog()
    if city not in catalog:
        raise ValueError(
            f"City '{city}' not found in the Inside Airbnb catalog. "
            f"Call list_available_cities() to see valid options."
        )

    entry = catalog[city]
    save_dir_path = Path(save_dir)
    save_dir_path.mkdir(parents=True, exist_ok=True)
    dest = save_dir_path / f"{city}_{entry['date']}_listings.csv.gz"

    resp = requests.get(entry["url"], timeout=60, stream=True)
    resp.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    return dest


if __name__ == "__main__":
    # Quick manual check: confirm whether the chosen dev city is covered.
    # Run this locally (needs network access) before building anything
    # else on top of it.
    dev_city = "las-palmas-de-gran-canaria"
    cities = list_available_cities()
    if dev_city in cities:
        print(f"'{dev_city}' is available. Downloading...")
        path = get_listings(dev_city)
        print(f"Saved to {path}")
    else:
        print(f"'{dev_city}' was NOT found in the Inside Airbnb catalog.")
        print("Closest matches:")
        print([c for c in cities if "canaria" in c or "palmas" in c or "spain" in c])
        print(f"Total cities available: {len(cities)}")

