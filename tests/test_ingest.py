"""
Unit tests for src/data/ingest.py.

These tests don't hit the network — they feed a small HTML snippet
(shaped like the real Inside Airbnb page) directly into the regex-based
parser, by monkeypatching requests.get.
"""

from unittest.mock import Mock, patch

from src.data.ingest import DATA_URL_PATTERN, fetch_city_catalog

SAMPLE_HTML = """
<a href="https://data.insideairbnb.com/spain/catalonia/barcelona/2026-06-24/data/listings.csv.gz">listings.csv.gz</a>
<a href="https://data.insideairbnb.com/spain/catalonia/barcelona/2026-03-15/data/listings.csv.gz">listings.csv.gz</a>
<a href="https://data.insideairbnb.com/the-netherlands/north-holland/amsterdam/2026-06-15/data/listings.csv.gz">listings.csv.gz</a>
"""


def test_pattern_extracts_expected_fields():
    match = DATA_URL_PATTERN.search(SAMPLE_HTML)
    assert match is not None
    assert match.group("country") == "spain"
    assert match.group("region") == "catalonia"
    assert match.group("city") == "barcelona"
    assert match.group("date") == "2026-06-24"


@patch("src.data.ingest.requests.get")
def test_fetch_city_catalog_keeps_only_latest_per_city(mock_get):
    mock_response = Mock()
    mock_response.text = SAMPLE_HTML
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    catalog = fetch_city_catalog()

    # Two Barcelona snapshots in the HTML -> only the first (latest) kept.
    assert catalog["barcelona"]["date"] == "2026-06-24"
    assert "amsterdam" in catalog
    assert len(catalog) == 2
