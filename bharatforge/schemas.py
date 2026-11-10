"""Bounded, strict contracts for source data, model output, and reports."""
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Category = Literal["bug", "feature", "documentation", "question", "maintenance", "other"]
Severity = Literal["critical", "high", "medium", "low"]
ShortText = Annotated[str, Field(min_length=1, max_length=1000)]
Score = Annotated[float, Field(ge=0, le=100, allow_inf_nan=False)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Issue(StrictModel):
    number: int = Field(gt=0)
    title: str = Field(max_length=500)
    body: str = Field(max_length=12000)
    labels: list[str] = Field(max_length=50)
    created_at: datetime
    updated_at: datetime
    comments: int = Field(ge=0)
    url: str
    truncated: bool = False

    @field_validator("created_at", "updated_at")
    @classmethod
    def timezone_required(cls, value):
        if value.tzinfo is None:
            raise ValueError("Dates must include a timezone")
        return value


class Repository(StrictModel):
    full_name: str
    description: str
    stars: int = Field(ge=0)
    open_items: int = Field(ge=0)
    url: str


class IssueAnalysis(StrictModel):
    number: int = Field(gt=0)
    category: Category
    severity: Severity
    summary: ShortText
    impact: Score
    reproducibility: Score
    confidence: float = Field(ge=0, le=1, allow_inf_nan=False)
    observed_facts: list[ShortText] = Field(max_length=6)
    inferred_conclusions: list[ShortText] = Field(max_length=6)
    missing_information: list[ShortText] = Field(max_length=8)
    suggested_action: ShortText
    evidence: list[Annotated[str, Field(min_length=1, max_length=300)]] = Field(max_length=5)


class AnalysisBatch(StrictModel):
    issues: list[IssueAnalysis] = Field(max_length=5)


class Priority(StrictModel):
    score: Score
    severity: Score
    impact: Score
    reproducibility: Score
    age: Score


class AnalyzedIssue(StrictModel):
    issue: Issue
    analysis: IssueAnalysis
    priority: Priority


class DuplicateVerdict(StrictModel):
    same_problem: bool
    reason: ShortText
    confidence: float = Field(ge=0, le=1, allow_inf_nan=False)


class DuplicatePair(StrictModel):
    first: int
    second: int
    similarity: float = Field(ge=0, le=1, allow_inf_nan=False)
    verdict: DuplicateVerdict | None


class BacklogOverview(StrictModel):
    summary: ShortText
    observations: list[ShortText] = Field(max_length=6)


class AnalysisReport(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    mode: Literal["demo", "live"]
    generated_at: datetime
    repository: Repository
    issues: list[AnalyzedIssue] = Field(max_length=50)
    duplicates: list[DuplicatePair] = Field(max_length=8)
    overview: BacklogOverview
    warnings: list[str]
    request_count: int = Field(ge=0)
    latency_seconds: float = Field(ge=0)
    model: str
