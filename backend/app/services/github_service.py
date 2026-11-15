
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

# Repository language cache (30-minute expiry)
REPOSITORY_CACHE = {}
CACHE_TTL = 30 * 60

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
        "per_page": per_page
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
    Search for beginner-friendly issues belonging to repositories
    written primarily in the requested programming language.
    """

    url = f"{GITHUB_API_URL}/search/issues"

    params = {
        "q": (
            f'is:issue is:open label:"{label}" '
            f'no:assignee language:{language}'
        ),
        "sort": sort_by,
        "order": "desc",
        "per_page": 100
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
        candidate_issues = result["items"]

        matching_issues = []
        checked_repositories = {}

        for issue in candidate_issues:
            repository_url = issue["repository_url"]

            if repository_url not in checked_repositories:
                cached_data = REPOSITORY_CACHE.get(repository_url)

                # Reuse cached information if it is still valid
                if (
                    cached_data is not None
                    and time.time() - cached_data["timestamp"] < CACHE_TTL
                ):
                    CACHE_STATS["hits"] += 1
                    repository_language = cached_data["language"]

                else:
                    CACHE_STATS["misses"] += 1

                    repo_response = await client.get(
                        repository_url,
                        headers=headers
                    )

                    repo_response.raise_for_status()

                    repository = repo_response.json()
                    repository_language = repository.get("language")

                    # Store fresh repository information
                    REPOSITORY_CACHE[repository_url] = {
                        "language": repository_language,
                        "timestamp": time.time()
                    }

                checked_repositories[repository_url] = repository_language

            repository_language = checked_repositories[repository_url]

            if (
                repository_language
                and repository_language.lower() == language.lower()
            ):
                matching_issues.append(issue)

            if len(matching_issues) >= per_page:
                break

        # Prepare a clean response
        cleaned_issues = []

        for issue in matching_issues:
            cleaned_issues.append({
                "title": issue["title"],
                "repository": issue["repository_url"].split("/repos/")[-1],
                "issue_number": issue["number"],
                "url": issue["html_url"],
                "labels": [
                    label["name"] for label in issue["labels"]
                ],
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "body": issue.get("body") or ""
            })

        return {
            "total_count": len(cleaned_issues),
            "candidates_checked": len(candidate_issues),
            "issues": cleaned_issues
        }
