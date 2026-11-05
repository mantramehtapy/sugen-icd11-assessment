from app.aliases import expand_aliases


def test_common_abbreviation_expands_to_catalog_terms():
    expanded = expand_aliases("known HTN and DM2")
    assert "hypertension" in expanded
    assert "type 2 diabetes mellitus" in expanded


def test_spanish_hypertension_alias_is_supported():
    expanded = expand_aliases("hipertensión")
    assert "hypertension" in expanded
