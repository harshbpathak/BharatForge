"""Deterministic heuristic; age reaches its maximum after 180 days."""
from datetime import datetime, timezone
import math

from .schemas import Priority

SEVERITY = {"critical": 100, "high": 75, "medium": 50, "low": 25}
MAX_AGE_DAYS = 180


def clamp(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError("Score inputs must be finite")
    return max(0.0, min(100.0, value))


def priority_score(severity: str, impact: float, reproducibility: float,
                   created_at: datetime, now: datetime | None = None) -> Priority:
    now = now or datetime.now(timezone.utc)
    age = clamp((now - created_at).total_seconds() / 86400 / MAX_AGE_DAYS * 100)
    components = dict(severity=float(SEVERITY[severity]), impact=clamp(impact),
                      reproducibility=clamp(reproducibility), age=age)
    score = round(.40 * components["severity"] + .35 * components["impact"]
                  + .15 * components["reproducibility"] + .10 * age, 2)
    return Priority(score=score, **components)
