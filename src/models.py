from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class CandidateScore:
    candidate_id: str
    score: float
    rank: int
    reasoning: str
    feature_breakdown: Dict[str, float]


CandidateRecord = Dict[str, Any]
CandidateList = List[CandidateRecord]
