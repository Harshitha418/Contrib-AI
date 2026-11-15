
# Issue recommendation scoring criteria

SCORING_WEIGHTS = {
    "good_first_issue": 30,
    "help_wanted": 20,
    "detailed_description": 25,
    "clear_title": 10,
    "recent_activity": 15
}


def get_recommendation_level(score: int):
    """
    Classify an issue based on its recommendation score.
    """

    if score >= 80:
        return "Excellent match"

    elif score >= 60:
        return "Good match"

    elif score >= 40:
        return "Moderate match"

    return "Low match"


from datetime import datetime, timezone


def score_issue(issue: dict):
    """
    Calculate a recommendation score for a GitHub issue.
    Returns the score, recommendation level and reasons.
    """

    score = 0
    reasons = []

    labels = [
        label.lower()
        for label in issue.get("labels", [])
    ]

    title = issue.get("title", "").strip()
    description = issue.get("body", "") or ""

    # 1. Beginner-friendly label: +30
    if "good first issue" in labels:
        score += SCORING_WEIGHTS["good_first_issue"]
        reasons.append("Marked as a good first issue")

    # 2. Help wanted label: +20
    if "help wanted" in labels:
        score += SCORING_WEIGHTS["help_wanted"]
        reasons.append("Maintainers are looking for contributors")

    # 3. Detailed description: +25
    if len(description.strip()) >= 300:
        score += SCORING_WEIGHTS["detailed_description"]
        reasons.append("Contains a detailed issue description")

    # 4. Clear title: +10
    if len(title) >= 15 and not title.lower().startswith(
        ("help", "question", "issue", "bug report")
    ):
        score += SCORING_WEIGHTS["clear_title"]
        reasons.append("Has a descriptive issue title")

    # 5. Recent activity: +15
    updated_at = issue.get("updated_at")

    if updated_at:
        try:
            updated_date = datetime.fromisoformat(
                updated_at.replace("Z", "+00:00")
            )

            days_since_update = (
                datetime.now(timezone.utc) - updated_date
            ).days

            if 0 <= days_since_update <= 30:
                score += SCORING_WEIGHTS["recent_activity"]
                reasons.append("Updated within the last 30 days")

        except (ValueError, TypeError):
            pass

    return {
        "score": score,
        "recommendation": get_recommendation_level(score),
        "reasons": reasons
    }

def rank_issues(issues: list):
    """
    Score and rank GitHub issues from highest to lowest relevance.
    """

    ranked_issues = []

    for issue in issues:
        recommendation = score_issue(issue)

        ranked_issue = {
            **issue,
            "recommendation_score": recommendation["score"],
            "recommendation_level": recommendation["recommendation"],
            "recommendation_reasons": recommendation["reasons"]
        }

        ranked_issues.append(ranked_issue)

    # Sort issues by recommendation score (highest first)
    ranked_issues.sort(
        key=lambda issue: issue["recommendation_score"],
        reverse=True
    )

    return ranked_issues
