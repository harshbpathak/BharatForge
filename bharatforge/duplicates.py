"""Two-stage candidate generation. Similarity is never proof of duplication."""
import re
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .schemas import DuplicatePair, DuplicateVerdict, Issue


@dataclass(frozen=True)
class Candidate:
    first: int
    second: int
    similarity: float


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text.casefold())).strip()


def find_candidates(issues: list[Issue], threshold: float = .35, max_pairs: int = 8):
    if not 0 <= threshold <= 1 or not 0 <= max_pairs <= 8:
        raise ValueError("Invalid duplicate detection limits")
    if len(issues) < 2 or max_pairs == 0:
        return []
    texts = [normalize(f"{issue.title} {issue.body}") for issue in issues]
    try:
        matrix = TfidfVectorizer(stop_words="english", max_features=10000,
                                  sublinear_tf=True).fit_transform(texts)
    except ValueError:  # Empty vocabulary, including stop-word-only issues.
        return []
    similarities = cosine_similarity(matrix)
    pairs = [Candidate(issues[i].number, issues[j].number,
                       float(min(1, max(0, similarities[i, j]))))
             for i in range(len(issues)) for j in range(i + 1, len(issues))
             if similarities[i, j] >= threshold]
    return sorted(pairs, key=lambda p: (-p.similarity, p.first, p.second))[:max_pairs]


def confirm_candidate(candidate, issues_by_number, ai):
    pair = [issues_by_number[candidate.first], issues_by_number[candidate.second]]
    verdict = ai.request(
        "Assess whether these issues describe the same underlying problem. Shared words alone "
        "are insufficient. Give a cautious reason and confidence. Do not assume missing details.",
        [{"number": issue.number, "title": issue.title, "body": issue.body} for issue in pair],
        DuplicateVerdict, budget=1200)
    return DuplicatePair(first=candidate.first, second=candidate.second,
                         similarity=candidate.similarity, verdict=verdict)
