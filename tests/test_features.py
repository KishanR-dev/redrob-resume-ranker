from src.config import RankingConfig
from src.features import behavior_score, experience_score, jd_fit_score, location_score, skills_score, title_quality_score


def test_jd_fit_high_for_relevant_title():
    cfg = RankingConfig()
    c = {
        "profile": {
            "current_title": "Recommendation Systems Engineer",
            "headline": "Search and Ranking",
            "summary": "Built retrieval and ranking systems",
        },
        "career_history": [
            {
                "company": "Swiggy",
                "industry": "Food Delivery",
                "title": "ML Engineer",
                "duration_months": 24,
                "description": "Built ranking and retrieval in production, improved ndcg with A/B test",
            }
        ],
    }
    assert jd_fit_score(c, cfg) > 0.6


def test_jd_fit_prefers_production_and_eval_evidence():
    cfg = RankingConfig()
    strong = {
        "profile": {
            "current_title": "ML Engineer",
            "headline": "Search systems",
            "summary": "Relevance and retrieval",
        },
        "career_history": [
            {
                "company": "Flipkart",
                "industry": "E-commerce",
                "title": "Search Engineer",
                "duration_months": 30,
                "description": "Owned ranking pipeline in production, ran A/B test, improved ndcg and served live users",
            },
            {
                "company": "Flipkart",
                "industry": "E-commerce",
                "title": "Senior Search Engineer",
                "duration_months": 24,
                "description": "Led vector search and retrieval deployment with online evaluation and latency improvements",
            },
        ],
    }
    weak = {
        "profile": {
            "current_title": "ML Engineer",
            "headline": "General ML",
            "summary": "Worked on models",
        },
        "career_history": [
            {
                "company": "ConsultCo",
                "industry": "Consulting",
                "title": "Data Scientist",
                "duration_months": 12,
                "description": "Built dashboards and ad-hoc analyses",
            }
        ],
    }
    assert jd_fit_score(strong, cfg) > jd_fit_score(weak, cfg)


def test_jd_fit_mixed_product_consulting_vs_consulting_only():
    cfg = RankingConfig()
    mixed = {
        "profile": {
            "current_title": "Search Engineer",
            "headline": "Ranking and retrieval",
            "summary": "Worked on recommendations",
        },
        "career_history": [
            {
                "company": "TCS",
                "industry": "IT Services",
                "title": "Data Scientist",
                "duration_months": 18,
                "description": "Analytics and model support",
            },
            {
                "company": "Swiggy",
                "industry": "Food Delivery",
                "title": "ML Engineer",
                "duration_months": 28,
                "description": "Built retrieval and ranking in production, improved ndcg through A/B testing and shipped to users",
            },
        ],
    }
    consulting_only = {
        "profile": {
            "current_title": "Search Engineer",
            "headline": "Ranking and retrieval",
            "summary": "Worked on recommendations",
        },
        "career_history": [
            {
                "company": "Infosys",
                "industry": "IT Services",
                "title": "Data Scientist",
                "duration_months": 24,
                "description": "Client analytics delivery and reporting",
            },
            {
                "company": "Accenture",
                "industry": "Consulting",
                "title": "ML Engineer",
                "duration_months": 20,
                "description": "Built generic ML solutions without production ranking ownership",
            },
        ],
    }
    assert jd_fit_score(mixed, cfg) > jd_fit_score(consulting_only, cfg)


def test_skills_score_positive():
    cfg = RankingConfig()
    c = {
        "skills": [
            {"name": "Embeddings", "proficiency": "expert", "endorsements": 40, "duration_months": 48},
            {"name": "Pinecone", "proficiency": "advanced", "endorsements": 20, "duration_months": 24},
        ]
    }
    assert skills_score(c, cfg) > 0.5


def test_experience_band():
    assert experience_score({"profile": {"years_of_experience": 6.0}}) == 1.0
    assert experience_score({"profile": {"years_of_experience": 2.0}}) < 0.5


def test_location_score_prefers_pune_noida():
    cfg = RankingConfig()
    pune = {"profile": {"location": "Pune, India"}}
    london = {"profile": {"location": "London, UK"}}
    assert location_score(pune, cfg) > location_score(london, cfg)


def test_title_quality_tiers():
    cfg = RankingConfig()
    gold = {"profile": {"current_title": "Ranking Engineer"}}
    off_target = {"profile": {"current_title": "Marketing Manager"}}
    assert title_quality_score(gold, cfg) > title_quality_score(off_target, cfg)


def test_behavior_score_penalizes_long_notice():
    good = {
        "redrob_signals": {
            "open_to_work_flag": True,
            "recruiter_response_rate": 0.7,
            "avg_response_time_hours": 24,
            "notice_period_days": 30,
            "interview_completion_rate": 0.8,
            "last_active_date": "2026-01-01",
        }
    }
    long_notice = {
        "redrob_signals": {
            "open_to_work_flag": True,
            "recruiter_response_rate": 0.7,
            "avg_response_time_hours": 24,
            "notice_period_days": 120,
            "interview_completion_rate": 0.8,
            "last_active_date": "2026-01-01",
        }
    }
    assert behavior_score(good) > behavior_score(long_notice)
