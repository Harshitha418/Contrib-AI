import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

GITHUB_API_URL = "https://api.github.com"

# Load the backend/.env file
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


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


async def search_beginner_issues(per_page: int = 10):
    """
    Search for beginner-friendly issues belonging to Java repositories.
    """

    url = f"{GITHUB_API_URL}/search/issues"

    params = {
        "q": 'is:issue is:open label:"good first issue" no:assignee',
        "sort": "created",
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

        java_issues = []
        checked_repositories = {}

        for issue in candidate_issues:
            repository_url = issue["repository_url"]

            if repository_url not in checked_repositories:
                repo_response = await client.get(
                    repository_url,
                    headers=headers
                )
                repo_response.raise_for_status()

                repository = repo_response.json()

                checked_repositories[repository_url] = (
                    repository.get("language")
                )

            if checked_repositories[repository_url] == "Java":
                java_issues.append(issue)

            if len(java_issues) >= per_page:
                break

        cleaned_issues = []

        for issue in java_issues:
            cleaned_issues.append({
                "title": issue["title"],
                "repository": issue["repository_url"].split("/repos/")[-1],
                "issue_number": issue["number"],
                "url": issue["html_url"],
                "labels": [
                    label["name"] for label in issue["labels"]
                ],
                "created_at": issue["created_at"]
            })

        return {
            "total_count": len(cleaned_issues),
            "candidates_checked": len(candidate_issues),
            "issues": cleaned_issues
        }
