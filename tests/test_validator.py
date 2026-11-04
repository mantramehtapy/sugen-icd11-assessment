from app.validator import validate_codes


def test_validator_removes_unknown_codes_and_limits_three():
    valid = {"1F40.Z", "CA00"}
    assert validate_codes(["bad", "1F40.Z", "CA00", "extra"], valid) == ["1F40.Z", "CA00"]
