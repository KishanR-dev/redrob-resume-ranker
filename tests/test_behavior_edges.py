from src.features import behavior_score


def test_behavior_score_very_long_notice_low_signals_is_strongly_penalized():
    severe = {
        "redrob_signals": {
            "open_to_work_flag": True,
            "recruiter_response_rate": 0.2,
            "avg_response_time_hours": 200,
            "notice_period_days": 150,
            "interview_completion_rate": 0.1,
            "last_active_date": "2024-01-01",
        }
    }
    moderate = {
        "redrob_signals": {
            "open_to_work_flag": True,
            "recruiter_response_rate": 0.65,
            "avg_response_time_hours": 48,
            "notice_period_days": 60,
            "interview_completion_rate": 0.7,
            "last_active_date": "2026-01-01",
        }
    }
    assert behavior_score(severe) < behavior_score(moderate)


def test_behavior_score_handles_missing_fields_without_crashing():
    sparse = {"redrob_signals": {"open_to_work_flag": False}}
    richer = {
        "redrob_signals": {
            "open_to_work_flag": True,
            "recruiter_response_rate": 0.75,
            "avg_response_time_hours": 24,
            "notice_period_days": 30,
            "interview_completion_rate": 0.8,
            "last_active_date": "2026-01-01",
        }
    }
    s_sparse = behavior_score(sparse)
    s_richer = behavior_score(richer)
    assert 0.0 <= s_sparse <= 1.0
    assert s_richer > s_sparse
