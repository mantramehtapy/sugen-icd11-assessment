import json
from app.io import iter_notes, write_prediction


def test_iter_notes_skips_blank_lines_but_preserves_ids(tmp_path):
    path = tmp_path / "notes.jsonl"
    path.write_text('{"id":"a","text":"fever"}\n\n{"id":"b","text":"cough"}\n', encoding="utf-8")
    assert [row["id"] for row in iter_notes(path)] == ["a", "b"]


def test_write_prediction_limits_codes_to_three(tmp_path):
    path = tmp_path / "pred.jsonl"
    write_prediction(path, "a", ["1A00", "1A01", "1A02", "1A03"])
    row = json.loads(path.read_text(encoding="utf-8"))
    assert row == {"id": "a", "codes": ["1A00", "1A01", "1A02"]}
