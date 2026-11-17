
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv


GITHUB_API_URL = "https://api.github.com"

# Load the backend/.env file
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


# Repository cache (kept for compatibility with cache statistics)
REPOSITORY_CACHE = {}
CACHE_TTL = 30 * 60

# Issue search cache (5-minute expiry)
ISSUE_CACHE = {}
ISSUE_CACHE_TTL = 5 * 60

# Cache statistics
CACHE_STATS = {
    "hits": 0,
    "misses": 0
}


def get_github_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    return headers


async def search_java_repositories(per_page: int = 10):
    """
    Search GitHub for active public Java repositories.
    """

    url = f"{GITHUB_API_URL}/search/repositories"

    params = {
        "q": "language:Java stars:>50 archived:false",
        "sort": "updated",
        "order": "desc",
        "per_page": min(per_page, 100)
    }

    headers = get_github_headers()

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            url,
            params=params,
            headers=headers
        )

        response.raise_for_status()

        return response.json()


async def search_beginner_issues(
    per_page: int = 10,
    language: str = "Java",
    label: str = "good first issue",
    sort_by: str = "created"
):
    """
    Search GitHub for beginner-friendly issues.

    Uses GitHub's language search qualifier and caches results
    to reduce unnecessary API requests.
    """

    # Create a unique cache key for each search configuration
    cache_key = (
        per_page,
        language.lower(),
        label.lower(),
        sort_by
    )

    # Check whether valid cached results exist
    cached_data = ISSUE_CACHE.get(cache_key)

    if (
        cached_data is not None
        and time.time() - cached_data["timestamp"] < ISSUE_CACHE_TTL
    ):
        CACHE_STATS["hits"] += 1
        return cached_data["data"]

    CACHE_STATS["misses"] += 1

    url = f"{GITHUB_API_URL}/search/issues"

    params = {
        "q": (
            f'is:issue is:open label:"{label}" '
            f'no:assignee language:{language}'
        ),
        "sort": sort_by,
        "order": "desc",
        "per_page": min(per_page, 100)
    }

    headers = get_github_headers()

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            url,
            params=params,
            headers=headers
        )

        response.raise_for_status()

        result = response.json()
        candidate_issues = result.get("items", [])

        # Prepare a clean response
        cleaned_issues = []

        for issue in candidate_issues:
            cleaned_issues.append({
                "title": issue["title"],
                "repository": issue["repository_url"].split("/repos/")[-1],
                "issue_number": issue["number"],
                "url": issue["html_url"],
                "labels": [
                    issue_label["name"]
                    for issue_label in issue.get("labels", [])
                ],
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "body": issue.get("body") or ""
            })

        data = {
            "total_count": len(cleaned_issues),
            "candidates_checked": len(candidate_issues),
            "issues": cleaned_issues
        }

        # Store results in cache
        ISSUE_CACHE[cache_key] = {
            "data": data,
            "timestamp": time.time()
        }

        return data
