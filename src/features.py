from __future__ import annotations

import re
from datetime import datetime
from typing import Dict, List, Tuple

from .config import RankingConfig


def _norm(text: str) -> str:
    return (text or "").strip().lower()


def _safe_float(v, default=0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default


def _days_since(date_str: str) -> int:
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return max((datetime.utcnow() - d).days, 0)
    except Exception:
        return 3650


def _contains_any(text: str, keywords: List[str]) -> bool:
    return any(k in text for k in keywords)


def _role_duration_months(role: Dict) -> float:
    return _safe_float(role.get("duration_months", 0.0), 0.0)


def _career_evidence_from_role(role: Dict, cfg: RankingConfig) -> Tuple[float, Dict[str, bool]]:
    company = _norm(role.get("company", ""))
    industry = _norm(role.get("industry", ""))
    title = _norm(role.get("title", ""))
    desc = _norm(role.get("description", ""))
    text = f"{title} {desc}".strip()

    retrieval_terms = [
        "retrieval",
        "ranking",
        "relevance",
        "recommendation",
        "recommender",
        "vector search",
        "embedding",
        "embeddings",
        "search",
        "learning to rank",
        "learning-to-rank",
        "l2r",
    ]
    production_terms = [
        "production",
        "deployed",
        "deploy",
        "shipped",
        "launched",
        "live",
        "serving",
        "served",
        "serves",
        "real users",
        "user traffic",
        "online",
        "latency",
        "sla",
        "uptime",
        "inference service",
    ]
    evaluation_terms = [
        "ndcg",
        "mrr",
        "map",
        "precision",
        "recall",
        "auc",
        "offline evaluation",
        "online evaluation",
        "ab test",
        "a/b test",
        "experiment",
        "experimentation",
    ]
    ownership_terms = [
        "owned",
        "owner",
        "led",
        "lead",
        "architected",
        "built",
        "designed",
        "end-to-end",
        "end to end",
    ]
    impact_terms = [
        "improved",
        "improvement",
        "increased",
        "reduced",
        "lift",
        "uplift",
        "decrease",
        "optimized",
    ]
    scale_regex = re.compile(r"\b(\d+(\.\d+)?)\s*(m|million|k|billion|qps|rps|users|requests)\b")

    has_domain = _contains_any(text, retrieval_terms)
    has_production = _contains_any(text, production_terms)
    has_eval = _contains_any(text, evaluation_terms)
    has_ownership = _contains_any(text, ownership_terms)
    has_impact = _contains_any(text, impact_terms)
    has_scale = bool(scale_regex.search(text))

    is_product_company = any(i in industry for i in cfg.preferred_industries)
    is_consulting = company in cfg.consulting_companies

    role_score = 0.0
    if has_domain:
        role_score += 0.26
    if has_production:
        role_score += 0.18
    if has_eval:
        role_score += 0.14
    if has_ownership:
        role_score += 0.11
    if has_impact:
        role_score += 0.09
    if has_scale:
        role_score += 0.07
    if is_product_company:
        role_score += 0.09

    if not has_domain and has_production:
        role_score -= 0.06
    if is_consulting:
        role_score -= 0.06

    role_score = max(min(role_score, 1.0), 0.0)
    evidence = {
        "has_domain": has_domain,
        "has_production": has_production,
        "has_eval": has_eval,
        "has_ownership": has_ownership,
        "has_impact": has_impact,
        "has_scale": has_scale,
        "is_product_company": is_product_company,
        "is_consulting": is_consulting,
    }
    return role_score, evidence


def title_quality_score(candidate: Dict, cfg: RankingConfig) -> float:
    profile = candidate.get("profile", {})
    title = _norm(profile.get("current_title", ""))
    headline = _norm(profile.get("headline", ""))
    text = f"{title} {headline}".strip()

    if any(k in text for k in cfg.title_tier_off_target):
        return 0.0
    if any(k in text for k in cfg.title_tier_gold):
        return 1.0
    if any(k in text for k in cfg.title_tier_strong):
        return 0.82
    if any(k in text for k in cfg.title_tier_adjacent):
        return 0.52
    if any(k in text for k in cfg.title_tier_risky_ai):
        return 0.30
    if any(k in text for k in cfg.target_role_keywords):
        return 0.7
    return 0.35


def location_score(candidate: Dict, cfg: RankingConfig) -> float:
    profile = candidate.get("profile", {})
    loc = _norm(profile.get("location", ""))
    if not loc:
        return 0.35

    if any(city in loc for city in cfg.preferred_locations_strong):
        return 1.0
    if any(city in loc for city in cfg.preferred_locations_secondary):
        return 0.72
    if any(city in loc for city in cfg.non_preferred_global_locations):
        return 0.10

    if "india" in loc:
        return 0.62
    return 0.18


def jd_fit_score(candidate: Dict, cfg: RankingConfig) -> float:
    profile = candidate.get("profile", {})
    title = _norm(profile.get("current_title", ""))
    summary = _norm(profile.get("summary", ""))
    headline = _norm(profile.get("headline", ""))
    career: List[Dict] = candidate.get("career_history", [])

    score = 0.0

    # Title contributes, but no longer dominates without historical corroboration.
    title_signal = 0.0
    if any(k in title for k in cfg.target_role_keywords):
        title_signal += 0.14
    if any(k in headline for k in cfg.target_role_keywords):
        title_signal += 0.08
    if any(x in summary for x in ["ranking", "retrieval", "embeddings", "recommendation", "search", "relevance"]):
        title_signal += 0.08

    role_scores: List[float] = []
    product_domain_roles = 0
    consulting_hits = 0
    domain_roles = 0
    production_roles = 0
    eval_roles = 0
    sustained_months = 0.0

    company_role_count: Dict[str, int] = {}

    for role in career:
        role_score, ev = _career_evidence_from_role(role, cfg)
        role_scores.append(role_score)

        company = _norm(role.get("company", ""))
        if company:
            company_role_count[company] = company_role_count.get(company, 0) + 1

        if ev["is_consulting"]:
            consulting_hits += 1
        if ev["has_domain"]:
            domain_roles += 1
            sustained_months += _role_duration_months(role)
        if ev["has_production"]:
            production_roles += 1
        if ev["has_eval"]:
            eval_roles += 1
        if ev["is_product_company"] and ev["has_domain"]:
            product_domain_roles += 1

    top_roles = sorted(role_scores, reverse=True)[:3]
    role_evidence_score = sum(top_roles) / max(len(top_roles), 1)
    score += 0.43 * role_evidence_score

    if product_domain_roles >= 2:
        score += 0.12
    elif product_domain_roles == 1:
        score += 0.06

    if domain_roles >= 2 and production_roles >= 1:
        score += 0.10
    elif domain_roles >= 1:
        score += 0.05

    if eval_roles >= 1:
        score += 0.07
    if eval_roles >= 2:
        score += 0.03

    # Sustained evidence over time.
    if sustained_months >= 36:
        score += 0.10
    elif sustained_months >= 18:
        score += 0.06
    elif sustained_months >= 9:
        score += 0.03

    # Progression via multiple relevant roles at same company.
    progression_hits = sum(1 for _, count in company_role_count.items() if count >= 2)
    if progression_hits > 0 and domain_roles >= 2:
        score += min(0.08, 0.04 * progression_hits)

    # Title signal only gets full strength if there is at least some corroborating role evidence.
    if domain_roles >= 1:
        score += title_signal
    else:
        score += 0.30 * title_signal

    score -= min(consulting_hits * 0.05, 0.18)

    if any(bad in title for bad in cfg.negative_title_keywords):
        score -= 0.25

    return max(min(score, 1.0), 0.0)


def skills_score(candidate: Dict, cfg: RankingConfig) -> float:
    skills = candidate.get("skills", [])
    if not skills:
        return 0.0

    total = 0.0
    max_possible = 0.0

    for sk in skills:
        name = _norm(sk.get("name", ""))
        endorsements = _safe_float(sk.get("endorsements", 0))
        duration = _safe_float(sk.get("duration_months", 0))
        prof = _norm(sk.get("proficiency", ""))

        base = 0.0
        for k, w in cfg.positive_skill_weights.items():
            if k in name:
                base = max(base, w)

        if base == 0.0:
            continue

        trust = 0.4 + min(endorsements / 50.0, 0.3) + min(duration / 60.0, 0.2)
        if prof in {"advanced", "expert"}:
            trust += 0.1

        total += min(base * trust, 1.0)
        max_possible += 1.0

    if max_possible == 0:
        return 0.0
    return max(min(total / max_possible, 1.0), 0.0)


def experience_score(candidate: Dict) -> float:
    yoe = _safe_float(candidate.get("profile", {}).get("years_of_experience", 0))
    if yoe < 3:
        return 0.2
    if 5 <= yoe <= 9:
        return 1.0
    if 4 <= yoe < 5 or 9 < yoe <= 11:
        return 0.75
    return 0.45


def behavior_score(candidate: Dict) -> float:
    s = candidate.get("redrob_signals", {})
    if not s:
        return 0.0

    open_to_work = 1.0 if s.get("open_to_work_flag", False) else 0.20
    response_rate = _safe_float(s.get("recruiter_response_rate", 0))
    response_time = _safe_float(s.get("avg_response_time_hours", 999))
    notice_days = _safe_float(s.get("notice_period_days", 180))
    interview_completion = _safe_float(s.get("interview_completion_rate", 0))
    last_active_days = _days_since(s.get("last_active_date", ""))

    recency = 1.0 if last_active_days <= 30 else 0.65 if last_active_days <= 90 else 0.25
    response_time_factor = 1.0 if response_time <= 48 else 0.7 if response_time <= 120 else 0.25
    if notice_days <= 30:
        notice_factor = 1.0
    elif notice_days <= 60:
        notice_factor = 0.70
    elif notice_days <= 90:
        notice_factor = 0.35
    elif notice_days <= 120:
        notice_factor = 0.12
    else:
        notice_factor = 0.03

    score = (
        0.25 * open_to_work
        + 0.20 * response_rate
        + 0.15 * response_time_factor
        + 0.15 * notice_factor
        + 0.15 * interview_completion
        + 0.10 * recency
    )

    # Stricter long-notice penalty when the rest of behavior is only average.
    avg_signal = (response_rate + interview_completion + recency) / 3.0
    if notice_days > 90 and avg_signal <= 0.72:
        score -= 0.08
    if notice_days > 120 and avg_signal <= 0.60:
        score -= 0.06

    return max(min(score, 1.0), 0.0)
