
from app.services.recommendation_service import (
    score_issue,
    get_recommendation_level
)


def test_perfect_issue_score():
    issue = {
        "title": "Add user authentication validation",
        "body": "This is a detailed issue description. " * 15,
        "labels": ["good first issue", "help wanted"],
        "updated_at": "2026-11-15T10:00:00Z"
    }

    result = score_issue(issue)

    assert result["score"] == 100
    assert result["recommendation"] == "Excellent match"


def test_recommendation_levels():
    assert get_recommendation_level(90) == "Excellent match"
    assert get_recommendation_level(70) == "Good match"
    assert get_recommendation_level(50) == "Moderate match"
    assert get_recommendation_level(20) == "Low match"


def test_issue_with_no_matching_criteria():
    issue = {
        "title": "Bug",
        "body": "",
        "labels": [],
        "updated_at": "2020-01-01T10:00:00Z"
    }

    result = score_issue(issue)

    assert result["score"] == 0
    assert result["recommendation"] == "Low match"
