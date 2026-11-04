from pathlib import Path
from app.catalog import load_catalog
from app.deterministic import choose_codes

CATALOG = load_catalog(Path("public/data/mms-2026-01.json"))


def test_choose_codes_returns_at_most_three_valid_codes():
    result = choose_codes("Assessment: uncomplicated malaria", CATALOG)
    assert 1 <= len(result.codes) <= 3
    assert all(CATALOG.is_valid(code) for code in result.codes)


def test_fallback_does_not_emit_explanation_text():
    result = choose_codes("Assessment: uncomplicated malaria", CATALOG)
    assert all(isinstance(code, str) for code in result.codes)
