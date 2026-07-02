from __future__ import annotations

from datetime import datetime
from typing import Dict, List


def _safe_float(v, default=0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default


def _parse_date(s: str):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        return None


def reliability_score(candidate: Dict) -> float:
    penalty = 0.0
    profile = candidate.get("profile", {})
    career: List[Dict] = candidate.get("career_history", [])
    skills: List[Dict] = candidate.get("skills", [])
    signals = candidate.get("redrob_signals", {})

    yoe = _safe_float(profile.get("years_of_experience", 0))

    total_career_months = 0.0
    parsed_ranges = []
    for role in career:
        total_career_months += _safe_float(role.get("duration_months", 0))
        sd = _parse_date(role.get("start_date", ""))
        ed = _parse_date(role.get("end_date", "")) if role.get("end_date") else datetime.utcnow()
        if sd and ed:
            if sd > ed:
                penalty += 0.15
            else:
                parsed_ranges.append((sd, ed))

    if yoe > 0:
        expected_months = yoe * 12.0
        if total_career_months > expected_months * 1.8:
            penalty += 0.25
        elif total_career_months < expected_months * 0.45:
            penalty += 0.18

    parsed_ranges.sort(key=lambda x: x[0])
    for i in range(1, len(parsed_ranges)):
        prev_start, prev_end = parsed_ranges[i - 1]
        cur_start, cur_end = parsed_ranges[i]
        if cur_start < prev_end:
            overlap_days = (prev_end - cur_start).days
            if overlap_days > 120:
                penalty += 0.10
                break

    exp_salary = signals.get("expected_salary_range_inr_lpa", {})
    min_sal = _safe_float(exp_salary.get("min", 0))
    max_sal = _safe_float(exp_salary.get("max", 0))
    if max_sal < min_sal:
        penalty += 0.30

    expert_zero_duration = 0
    advanced_zero_duration = 0
    for sk in skills:
        prof = (sk.get("proficiency", "") or "").lower()
        duration = _safe_float(sk.get("duration_months", 0))
        if prof == "expert" and duration <= 0:
            expert_zero_duration += 1
        if prof == "advanced" and duration <= 0:
            advanced_zero_duration += 1

    if expert_zero_duration >= 3:
        penalty += 0.25
    elif expert_zero_duration >= 1:
        penalty += 0.12

    if advanced_zero_duration >= 4:
        penalty += 0.16
    elif advanced_zero_duration >= 2:
        penalty += 0.08

    response_rate = _safe_float(signals.get("recruiter_response_rate", 0))
    active = signals.get("last_active_date")
    if active:
        ad = _parse_date(active)
        if ad:
            stale_days = (datetime.utcnow() - ad).days
            if stale_days > 180 and response_rate < 0.1:
                penalty += 0.20
            elif stale_days > 120 and response_rate < 0.2:
                penalty += 0.10

    return max(1.0 - penalty, 0.0)
