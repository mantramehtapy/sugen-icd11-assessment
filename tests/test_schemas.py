from app.schemas import parse_model_codes


def test_parse_model_codes_accepts_only_codes_list():
    assert parse_model_codes('{"codes":["1F40.Z"]}') == ["1F40.Z"]


def test_parse_model_codes_rejects_extra_text_and_limits_three():
    assert parse_model_codes('{"codes":["A","B","C","D"]}') == ["A", "B", "C"]
    assert parse_model_codes("not json") == []


def test_parse_model_codes_accepts_fenced_json():
    content = "```json\n{\"codes\":[\"1F40.Z\"]}\n```"
    assert parse_model_codes(content) == ["1F40.Z"]
