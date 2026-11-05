from app.evidence import extract_evidence


def test_assessment_has_priority_over_history_and_negation():
    evidence = extract_evidence(
        "History of asthma. No fever. Assessment: moderate asthma attack."
    )
    assert evidence.assessment == ["moderate asthma attack"]
    assert "fever" in evidence.negated
    assert "asthma" in evidence.history


def test_assessment_marker_supports_clinical_a_prefix():
    evidence = extract_evidence("A: uncomplicated falciparum malaria")
    assert evidence.assessment == ["uncomplicated falciparum malaria"]


def test_sections_do_not_merge_history_into_assessment():
    note = "Assessment: hypertension. History: prior ocular hypertension."
    evidence = extract_evidence(note)
    assert evidence.assessment == ["hypertension"]
    assert evidence.history == ["prior ocular hypertension"]


def test_negated_condition_is_not_positive_evidence():
    note = "Assessment: hypertension. Denies headache and chest pain."
    evidence = extract_evidence(note)
    assert "headache" in evidence.negated
    assert "chest pain" in evidence.negated
    assert "headache" not in evidence.positive_terms
    assert "chest pain" not in evidence.positive_terms
