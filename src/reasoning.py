from __future__ import annotations

import random
import re
from typing import Dict, List, Tuple


def _norm(text: str) -> str:
    return (text or "").strip().lower()


def _safe_float(v, default=0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default


def _clean_text(text: str) -> str:
    t = re.sub(r"\s+", " ", (text or "").strip())
    return t.strip(" ,;:-")


def _split_sentences(desc: str) -> List[str]:
    text = _clean_text(desc)
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+|[;\n]+", text)
    out = []
    for p in parts:
        c = _clean_text(p)
        if len(c) >= 12:
            out.append(c)
    return out


def _extract_clean_clause(text: str, term: str, window: int = 120) -> str:
    lowered = text.lower()
    idx = lowered.find(term.lower())
    if idx < 0:
        return ""

    # Anchor to word boundaries near the match to avoid mid-word truncation.
    start = max(0, idx - window // 2)
    end = min(len(text), idx + window // 2)

    while start > 0 and text[start - 1].isalnum():
        start -= 1
    while end < len(text) and text[end:end + 1].isalnum():
        end += 1

    snippet = _clean_text(text[start:end])
    # Prefer trimming to nearby punctuation boundaries if available.
    left_cut = max(snippet.rfind(". "), snippet.rfind("; "), snippet.rfind(": "))
    if left_cut >= 0 and left_cut < len(snippet) - 15:
        snippet = _clean_text(snippet[left_cut + 2 :])

    if len(snippet) > 140:
        words = snippet.split()
        trimmed = []
        total = 0
        for w in words:
            if total + len(w) + (1 if trimmed else 0) > 140:
                break
            trimmed.append(w)
            total += len(w) + (1 if trimmed else 0)
        snippet = " ".join(trimmed)

    return snippet


def _pick_description_phrase(desc: str) -> str:
    if not desc:
        return ""

    text = _clean_text(desc)
    if not text:
        return ""

    def _to_continuation(phrase: str) -> str:
        p = _clean_text(phrase)
        if not p:
            return ""

        lower = p.lower()
        # avoid awkward continuations after "where they ..."
        bad_starts = ("the ", "how ", "what ", "why ", "when ", "where ", "who ", "pairs ")
        if lower.startswith(bad_starts):
            return ""
        if p[:1].isupper():
            p = p[:1].lower() + p[1:]
        return p

    priority_terms = [
        "retrieval",
        "ranking",
        "relevance",
        "recommendation",
        "recommender",
        "embedding",
        "vector search",
        "a/b test",
        "ab test",
        "ndcg",
        "mrr",
        "map",
        "production",
        "deployed",
        "shipped",
        "serving",
        "live",
    ]

    sentences = _split_sentences(text)
    for term in priority_terms:
        for s in sentences:
            if term in s.lower():
                raw = s if len(s) <= 150 else _extract_clean_clause(s, term, window=120)
                cont = _to_continuation(raw)
                if cont:
                    return cont

    for term in priority_terms:
        phrase = _extract_clean_clause(text, term, window=130)
        if phrase and len(phrase) >= 14:
            cont = _to_continuation(phrase)
            if cont:
                return cont

    if sentences:
        first = sentences[0]
        if len(first) > 150:
            words = first.split()
            clipped = []
            total = 0
            for w in words:
                if total + len(w) + (1 if clipped else 0) > 140:
                    break
                clipped.append(w)
                total += len(w) + (1 if clipped else 0)
            first = " ".join(clipped)
        cont = _to_continuation(first)
        if cont:
            return cont

    return ""


def _fact_from_role(role: Dict) -> Tuple[str, int]:
    company = _clean_text(role.get("company", ""))
    title = _clean_text(role.get("title", ""))
    desc = _clean_text(role.get("description", ""))
    industry = _clean_text(role.get("industry", ""))

    base: List[str] = []
    weight = 0

    if company and title:
        base.append(f"{title} at {company}")
    elif title:
        base.append(title)
    elif company:
        base.append(f"role at {company}")

    phrase = _pick_description_phrase(desc)
    if phrase:
        base.append(f"where they {phrase}")
    elif desc:
        base.append(f"— {_clean_text(desc)[:140]}")
    elif industry:
        base.append(f"in {industry}")

    desc_l = _norm(desc)
    if any(k in desc_l for k in ["ranking", "retrieval", "relevance", "recommendation", "recommender", "search"]):
        weight += 3
    if any(k in desc_l for k in ["production", "deployed", "shipped", "serving", "live", "users"]):
        weight += 2
    if any(k in desc_l for k in ["ndcg", "mrr", "map", "a/b test", "ab test", "experiment"]):
        weight += 2
    if any(k in desc_l for k in ["improved", "increased", "reduced", "lift", "uplift"]):
        weight += 1

    if not base:
        return "", 0
    return ", ".join(base), weight


def _collect_role_facts(candidate: Dict) -> List[str]:
    career = candidate.get("career_history", []) or []
    weighted_facts: List[Tuple[int, str]] = []
    for role in career:
        fact, w = _fact_from_role(role)
        if fact:
            weighted_facts.append((w, fact))
    weighted_facts.sort(key=lambda x: x[0], reverse=True)

    unique = []
    seen = set()
    for _, fact in weighted_facts:
        k = fact.lower()
        if k in seen:
            continue
        seen.add(k)
        unique.append(fact)
        if len(unique) >= 5:
            break
    return unique


def _behavior_note(signals: Dict, rng: random.Random) -> str:
    rr = _safe_float(signals.get("recruiter_response_rate", 0.0), 0.0)
    notice = _safe_float(signals.get("notice_period_days", 180), 180.0)
    interview = _safe_float(signals.get("interview_completion_rate", 0.0), 0.0)
    last_active = (signals.get("last_active_date", "") or "").strip()

    notes: List[str] = []

    if rr >= 0.82 and interview >= 0.72:
        notes.append(
            rng.choice(
                [
                    f"Engagement appears strong with response rate around {rr:.2f} and interview completion near {interview:.2f}.",
                    f"High recruiter responsiveness ({rr:.2f}) and steady interview follow-through ({interview:.2f}) support execution confidence.",
                    f"Interaction signals are a plus: response rate {rr:.2f} with interview completion at {interview:.2f}.",
                ]
            )
        )
    elif rr <= 0.35:
        notes.append(
            rng.choice(
                [
                    f"Recruiter response rate is only {rr:.2f}, which could slow scheduling cadence.",
                    f"A response rate near {rr:.2f} suggests lower outreach responsiveness.",
                    f"Low responsiveness ({rr:.2f}) may create process friction.",
                ]
            )
        )

    if notice > 120:
        notes.append(
            rng.choice(
                [
                    f"The {int(notice)}-day notice period is a concrete risk for near-term hiring timelines.",
                    f"Notice at roughly {int(notice)} days materially delays potential onboarding.",
                    f"A {int(notice)}-day notice window is long for roles needing quick ramp-up.",
                ]
            )
        )
    elif notice > 90:
        notes.append(
            rng.choice(
                [
                    f"Notice period of {int(notice)} days is longer than ideal for a fast close.",
                    f"The {int(notice)}-day notice horizon may affect offer-to-join speed.",
                ]
            )
        )

    if interview <= 0.30 and interview > 0:
        notes.append(
            rng.choice(
                [
                    f"Interview completion is modest at {interview:.2f}, so drop-off risk should be monitored.",
                    f"Completion rate around {interview:.2f} indicates weaker process consistency.",
                ]
            )
        )

    if last_active and rr >= 0.82 and interview >= 0.72 and notice <= 60:
        notes.append(
            rng.choice(
                [
                    f"Recent platform activity ({last_active}) also aligns with active job-search intent.",
                    f"Last active on {last_active}, consistent with otherwise proactive signals.",
                ]
            )
        )

    return " ".join(notes[:2]).strip()


def _reliability_concern(candidate: Dict) -> str:
    signals = candidate.get("redrob_signals", {}) or {}
    skills = candidate.get("skills", []) or []

    sal = signals.get("expected_salary_range_inr_lpa", {}) or {}
    smin = _safe_float(sal.get("min", 0), 0)
    smax = _safe_float(sal.get("max", 0), 0)
    if smax > 0 and smin > 0 and smin > smax:
        return "Expected salary range appears inverted (min above max), so compensation data needs verification."

    expert_zero = 0
    for sk in skills:
        prof = _norm(sk.get("proficiency", ""))
        dur = _safe_float(sk.get("duration_months", 0), 0)
        if prof in {"expert", "advanced"} and dur <= 0:
            expert_zero += 1
    if expert_zero >= 2:
        return f"{expert_zero} advanced/expert skills show zero duration, which weakens confidence in self-reported depth."

    return ""


def build_reasoning(candidate: Dict, feature_breakdown: Dict[str, float]) -> str:
    profile = candidate.get("profile", {}) or {}
    signals = candidate.get("redrob_signals", {}) or {}

    facts = _collect_role_facts(candidate)
    jd = feature_breakdown.get("jd_fit", 0.0)
    reliability = feature_breakdown.get("reliability", 1.0)

    chosen = facts[:3] if len(facts) >= 3 else facts[:2] if len(facts) >= 2 else facts[:1]
    if chosen:
        career_block = " | ".join(chosen)
    else:
        title = _clean_text(profile.get("current_title", "current role")) or "current role"
        career_block = f"{title}; limited concrete historical retrieval/ranking evidence"

    if jd >= 0.72:
        jd_block = "Strong production retrieval/ranking fit; evaluation/shipping evidence present"
    elif jd >= 0.55:
        jd_block = "Moderate fit; partial production and evaluation evidence"
    else:
        jd_block = "Partial fit; weaker direct evidence of shipped production ranking/retrieval ownership"

    behavior_bits: List[str] = []
    rr = _safe_float(signals.get("recruiter_response_rate", 0.0), 0.0)
    notice = _safe_float(signals.get("notice_period_days", 180), 180.0)
    interview = _safe_float(signals.get("interview_completion_rate", 0.0), 0.0)
    last_active = (signals.get("last_active_date", "") or "").strip()

    if rr >= 0.8:
        behavior_bits.append(f"high response_rate={rr:.2f}")
    elif rr <= 0.35:
        behavior_bits.append(f"low response_rate={rr:.2f}")

    if notice > 120:
        behavior_bits.append(f"notice={int(notice)}d (high)")
    elif notice > 90:
        behavior_bits.append(f"notice={int(notice)}d (elevated)")
    elif notice <= 45:
        behavior_bits.append(f"notice={int(notice)}d")

    if interview >= 0.7:
        behavior_bits.append(f"interview_completion={interview:.2f}")
    elif interview > 0 and interview <= 0.3:
        behavior_bits.append(f"interview_completion={interview:.2f} (low)")

    if last_active and (rr >= 0.8 or rr <= 0.35 or notice > 90):
        behavior_bits.append(f"last_active={last_active}")

    behavior_block = " | ".join(behavior_bits) if behavior_bits else "neutral"

    risks: List[str] = []
    rel_flag = _reliability_concern(candidate)
    if rel_flag and reliability < 0.95:
        risks.append(rel_flag)
    if jd < 0.45 and not chosen:
        risks.append("limited concrete career evidence of production ranking/retrieval execution")

    risk_block = " | ".join(risks) if risks else "none"

    return f"Career: {career_block}; JD Fit: {jd_block}; Behavior: {behavior_block}; Risk: {risk_block}"
