from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RetrievalCase:
    query: str
    expected_sources: set[str]


def precision_at_k(results: list[dict[str, Any]], expected_sources: set[str], k: int) -> float:
    top = results[:k]
    if not top:
        return 0.0
    relevant = sum(1 for r in top if r.get("source") in expected_sources)
    return relevant / len(top)


def recall_at_k(results: list[dict[str, Any]], expected_sources: set[str], k: int) -> float:
    if not expected_sources:
        return 1.0
    found = {r.get("source") for r in results[:k]}
    return len(found & expected_sources) / len(expected_sources)


async def evaluate_retriever(retriever, cases: list[RetrievalCase], k: int = 5):
    rows = []
    for case in cases:
        results = await retriever.search(case.query, top_k=k)
        raw = [r.model_dump() for r in results]
        rows.append({
            "query": case.query,
            "precision_at_k": precision_at_k(raw, case.expected_sources, k),
            "recall_at_k": recall_at_k(raw, case.expected_sources, k),
        })
    return rows
