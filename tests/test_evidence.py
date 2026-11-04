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
