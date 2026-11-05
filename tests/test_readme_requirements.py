from pathlib import Path


README = Path("README.md").read_text(encoding="utf-8")


def test_readme_contains_required_submission_sections():
    required = [
        "Development score",
        "Hidden-score estimate",
        "Data sources",
        "Evaluation beyond the 60",
        "AI-tooling error",
        "Hours spent",
        "docker compose run coder /in/notes.jsonl /out/predictions.jsonl",
    ]
    missing = [phrase for phrase in required if phrase not in README]
    assert not missing, f"missing README requirements: {missing}"
