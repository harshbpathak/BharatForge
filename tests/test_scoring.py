from datetime import datetime, timedelta, timezone
import pytest

from bharatforge.scoring import priority_score

NOW = datetime(2026, 11, 1, tzinfo=timezone.utc)


def test_exact_formula_and_determinism():
    args = ("high", 80, 60, NOW - timedelta(days=90), NOW)
    result = priority_score(*args)
    assert result.score == 72.0
    assert result.age == 50
    assert result == priority_score(*args)


def test_boundaries():
    assert priority_score("critical", 1000, 1000, NOW-timedelta(days=1000), NOW).score == 100
    result = priority_score("low", -10, -100, NOW+timedelta(days=10), NOW)
    assert result.score == 10 and result.age == 0


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_rejected(value):
    with pytest.raises(ValueError):
        priority_score("high", value, 50, NOW, NOW)
