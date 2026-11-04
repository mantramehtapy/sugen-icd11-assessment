from app.normalize import normalize_text, tokenize


def test_normalize_text():
    assert normalize_text("  Fever\nWITH chills. ") == "fever with chills."


def test_keep_negation_tokens():
    tokens = tokenize("No cough, fever excluded")
    assert {"no", "cough", "fever", "excluded"}.issubset(tokens)
