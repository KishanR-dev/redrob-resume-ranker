from src.honeypot import reliability_score
from src.reasoning import build_reasoning


def test_reliability_penalizes_salary_inversion():
    c = {
        "profile": {"years_of_experience": 5},
        "career_history": [{"duration_months": 60, "start_date": "2020-01-01", "end_date": "2022-01-01"}],
        "skills": [],
        "redrob_signals": {
            "expected_salary_range_inr_lpa": {"min": 30, "max": 10},
            "recruiter_response_rate": 0.5,
            "last_active_date": "2026-01-01",
        },
    }
    assert reliability_score(c) < 1.0


def test_reliability_penalizes_expert_zero_duration():
    c = {
        "profile": {"years_of_experience": 6},
        "career_history": [{"duration_months": 72, "start_date": "2018-01-01", "end_date": "2024-01-01"}],
        "skills": [
            {"name": "Embeddings", "proficiency": "expert", "duration_months": 0},
            {"name": "Retrieval", "proficiency": "expert", "duration_months": 0},
            {"name": "Ranking", "proficiency": "expert", "duration_months": 0},
        ],
        "redrob_signals": {"recruiter_response_rate": 0.6, "last_active_date": "2026-01-01"},
    }
    assert reliability_score(c) < 0.9


def test_reasoning_contains_career_facts_and_jd_link():
    c = {
        "candidate_id": "cand-123",
        "profile": {"current_title": "AI Engineer", "years_of_experience": 6, "location": "Pune"},
        "career_history": [
            {
                "company": "Swiggy",
                "title": "ML Engineer",
                "description": "Built retrieval system and improved ndcg via A/B test on recommendations shipped to users",
            },
            {
                "company": "Flipkart",
                "title": "Search Engineer",
                "description": "Owned ranking pipeline with vector search in production and online evaluation",
            },
        ],
        "redrob_signals": {
            "notice_period_days": 30,
            "recruiter_response_rate": 0.85,
            "interview_completion_rate": 0.8,
            "open_to_work_flag": True,
            "last_active_date": "2026-01-01",
        },
    }
    r = build_reasoning(
        c,
        {
            "jd_fit": 0.85,
            "skills": 0.7,
            "title_quality": 0.82,
            "location": 1.0,
            "behavior": 0.86,
            "reliability": 1.0,
        },
    )
    rl = r.lower()
    assert "swiggy" in rl or "flipkart" in rl
    assert any(k in rl for k in ["retrieval", "ranking", "vector search", "ndcg", "a/b test", "ab test"])
    assert any(k in rl for k in ["production", "shipped", "real users", "live users", "deployed", "serving"])


def test_reasoning_sparse_career_history_stays_grounded():
    c = {
        "candidate_id": "cand-sparse-1",
        "profile": {"current_title": "ML Engineer", "years_of_experience": 4, "location": "Bangalore"},
        "career_history": [],
        "redrob_signals": {
            "notice_period_days": 120,
            "recruiter_response_rate": 0.3,
            "interview_completion_rate": 0.2,
        },
        "skills": [
            {"name": "Embeddings", "proficiency": "expert", "duration_months": 0},
            {"name": "Retrieval", "proficiency": "expert", "duration_months": 0},
        ],
    }

    r = build_reasoning(
        c,
        {
            "jd_fit": 0.30,
            "skills": 0.2,
            "title_quality": 0.82,
            "location": 0.72,
            "behavior": 0.35,
            "reliability": 0.7,
        },
    )
    rl = r.lower()
    assert "limited" in rl or "thinner" in rl
    assert "notice" in rl
    assert "zero duration" in rl or "duration" in rl
