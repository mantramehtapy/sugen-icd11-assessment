from pathlib import Path


DECISIONS = Path("DECISIONS.md").read_text(encoding="utf-8")


def test_decisions_log_has_real_commits_and_required_fields():
    assert "Commit: pending" not in DECISIONS
    assert DECISIONS.count("- Decision:") >= 8
    assert DECISIONS.count("- Options considered:") >= 8
    assert DECISIONS.count("- Evidence:") >= 8
    assert DECISIONS.count("- Revisit:") >= 8
