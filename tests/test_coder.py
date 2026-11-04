import json
import subprocess
import sys


def test_cli_emits_one_line_per_input(tmp_path):
    source = tmp_path / "notes.jsonl"
    output = tmp_path / "predictions.jsonl"
    source.write_text(json.dumps({"id": "n1", "text": "fever"}) + "\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "app", str(source), str(output)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    rows = [json.loads(line) for line in output.read_text().splitlines()]
    assert rows[0]["id"] == "n1"
    assert 1 <= len(rows[0]["codes"]) <= 3
