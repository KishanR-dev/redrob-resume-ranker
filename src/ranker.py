from __future__ import annotations

from typing import Dict, List

from .config import RankingConfig
from .features import behavior_score, experience_score, jd_fit_score, location_score, skills_score, title_quality_score
from .honeypot import reliability_score
from .models import CandidateScore
from .reasoning import build_reasoning


def score_candidate(candidate: Dict, cfg: RankingConfig) -> CandidateScore:
    f_jd = jd_fit_score(candidate, cfg)
    f_skills = skills_score(candidate, cfg)
    f_title = title_quality_score(candidate, cfg)
    f_loc = location_score(candidate, cfg)
    f_exp = experience_score(candidate)
    f_behavior = behavior_score(candidate)
    f_reliability = reliability_score(candidate)

    score = (
        cfg.weights["jd_fit"] * f_jd
        + cfg.weights["skills"] * f_skills
        + cfg.weights["title_quality"] * f_title
        + cfg.weights["location"] * f_loc
        + cfg.weights["experience"] * f_exp
        + cfg.weights["behavior"] * f_behavior
        + cfg.weights["reliability"] * f_reliability
    )

    score = max(min(score, 1.0), 0.0)

    breakdown = {
        "jd_fit": f_jd,
        "skills": f_skills,
        "title_quality": f_title,
        "location": f_loc,
        "experience": f_exp,
        "behavior": f_behavior,
        "reliability": f_reliability,
    }

    return CandidateScore(
        candidate_id=candidate.get("candidate_id", ""),
        score=score,
        rank=0,
        reasoning=build_reasoning(candidate, breakdown),
        feature_breakdown=breakdown,
    )


def rank_candidates(candidates: List[Dict], top_k: int = 100) -> List[CandidateScore]:
    cfg = RankingConfig()
    scored = [score_candidate(c, cfg) for c in candidates if c.get("candidate_id")]

    scored.sort(key=lambda x: (-x.score, x.candidate_id))

    top = scored[:top_k]
    for idx, c in enumerate(top, start=1):
        c.rank = idx
    return top
