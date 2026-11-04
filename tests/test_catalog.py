from pathlib import Path
from app.catalog import load_catalog

CATALOG = Path("public/data/mms-2026-01.json")


def test_loads_expected_catalog_size():
    catalog = load_catalog(CATALOG)
    assert len(catalog.rows) == 18_375
    assert catalog.rows[0].code == "1A00"


def test_validates_codes():
    catalog = load_catalog(CATALOG)
    assert catalog.is_valid("1A00")
    assert not catalog.is_valid("NOT-A-CODE")
