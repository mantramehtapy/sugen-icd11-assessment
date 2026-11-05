from pathlib import Path
from app.catalog import load_catalog
from app.retrieval import retrieve

CATALOG = load_catalog(Path("public/data/mms-2026-01.json"))


def test_retrieve_returns_only_catalog_rows():
    rows = retrieve("Assessment: uncomplicated malaria", CATALOG, limit=10)
    assert 1 <= len(rows) <= 10
    assert all(CATALOG.is_valid(row.code) for row in rows)


def test_retrieval_is_deterministic():
    first = [x.code for x in retrieve("moderate asthma attack", CATALOG, limit=5)]
    second = [x.code for x in retrieve("moderate asthma attack", CATALOG, limit=5)]
    assert first == second


def test_retrieval_expands_common_abbreviations():
    rows = retrieve("known HTN", CATALOG, limit=20)
    assert any(row.code == "BA00.Z" for row in rows)
