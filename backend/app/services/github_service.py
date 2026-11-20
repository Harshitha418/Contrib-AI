
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


# Repository cache (30-minute expiry)
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


async def get_repository_language(repository: str):
    """
    Retrieve the primary programming language of a GitHub repository.

    Repository language information is cached for 30 minutes.
    """

    cached_data = REPOSITORY_CACHE.get(repository)

    if (
        cached_data is not None
        and time.time() - cached_data["timestamp"] < CACHE_TTL
    ):
        CACHE_STATS["hits"] += 1
        return cached_data["language"]

    CACHE_STATS["misses"] += 1

    url = f"{GITHUB_API_URL}/repos/{repository}"

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            url,
            headers=get_github_headers()
        )

        response.raise_for_status()

        repository_data = response.json()
        language = repository_data.get("language")

        REPOSITORY_CACHE[repository] = {
            "language": language,
            "timestamp": time.time()
        }

        return language


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
    sort_by: str = "created",
    keyword: str = ""
):
    """
    Search GitHub for beginner-friendly issues.

    Supports:
    - Programming language
    - Issue label
    - Sorting
    - Keyword search in issue titles and descriptions

    Verifies the actual primary language of each repository.
    Uses pagination and caching to reduce unnecessary API requests.
    """

    keyword = keyword.strip()
    per_page = min(max(per_page, 1), 100)

    # Create a unique cache key for each search configuration
    cache_key = (
        per_page,
        language.lower(),
        label.lower(),
        sort_by,
        keyword.lower()
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

    # Build GitHub search query
    query_parts = [
        "is:issue",
        "is:open",
        f'label:"{label}"',
        "no:assignee"
    ]

    # Add keyword search when provided
    if keyword:
        query_parts.insert(
            0,
            f"{keyword} in:title,body"
        )

    headers = get_github_headers()

    # GitHub Search API allows up to 100 results per page
    github_page_size = 100
    page = 1

    cleaned_issues = []
    candidates_checked = 0
    github_total_count = 0

    async with httpx.AsyncClient(timeout=20.0) as client:

        # GitHub Search API supports a maximum of 10 pages
        while page <= 10 and len(cleaned_issues) < per_page:

            params = {
                "q": " ".join(query_parts),
                "sort": sort_by,
                "order": "desc",
                "per_page": github_page_size,
                "page": page
            }

            response = await client.get(
                url,
                params=params,
                headers=headers
            )

            response.raise_for_status()

            result = response.json()

            candidate_issues = result.get("items", [])

            github_total_count = result.get("total_count", 0)

            candidates_checked += len(candidate_issues)

            # Stop if GitHub has no more results
            if not candidate_issues:
                break

            for issue in candidate_issues:

                repository = issue["repository_url"].split("/repos/")[-1]

                # Fetch the repository's actual primary language
                repository_language = await get_repository_language(
                    repository
                )

                # Keep only repositories matching the selected language
                if (
                    (repository_language or "").lower()
                    != language.lower()
                ):
                    continue

                cleaned_issues.append({
                    "title": issue["title"],
                    "repository": repository,
                    "repository_language": repository_language,
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

                # Stop once the requested number of matches is collected
                if len(cleaned_issues) >= per_page:
                    break

            # Move to the next GitHub search page
            page += 1

    data = {
        "total_count": len(cleaned_issues),
        "github_total_count": github_total_count,
        "candidates_checked": candidates_checked,
        "pages_checked": page - 1,
        "issues": cleaned_issues
    }

    # Store results in cache
    ISSUE_CACHE[cache_key] = {
        "data": data,
        "timestamp": time.time()
    }

    return data
