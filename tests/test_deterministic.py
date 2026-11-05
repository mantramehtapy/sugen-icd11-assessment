from pathlib import Path
from app.catalog import load_catalog
from app.deterministic import choose_codes

CATALOG = load_catalog(Path("public/data/mms-2026-01.json"))


def test_choose_codes_returns_at_most_three_valid_codes():
    result = choose_codes("Assessment: uncomplicated malaria", CATALOG)
    assert 1 <= len(result.codes) <= 3
    assert all(CATALOG.is_valid(code) for code in result.codes)


def test_assessment_prefers_uncomplicated_falciparum_unspecified_code():
    result = choose_codes("A: uncomplicated falciparum malaria", CATALOG)
    assert result.codes[0] == "1F40.Z"


def test_simple_hypertension_does_not_select_ocular_hypertension():
    result = choose_codes("Assessment: hypertension.", CATALOG)
    assert result.codes[0] == "BA00.Z"
