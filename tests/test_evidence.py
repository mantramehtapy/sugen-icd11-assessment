from app.evidence import extract_evidence


def test_assessment_has_priority_over_history_and_negation():
    evidence = extract_evidence(
        "History of asthma. No fever. Assessment: moderate asthma attack."
    )
    assert evidence.assessment == ["moderate asthma attack"]
    assert "fever" in evidence.negated
    assert "asthma" in evidence.history
