
import httpx

GITHUB_API_URL = "https://api.github.com"


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

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

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
    Search GitHub for open beginner-friendly issues
    that have not been assigned yet.
    """

    url = f"{GITHUB_API_URL}/search/issues"

    params = {
        "q": 'is:issue is:open label:"good first issue" no:assignee',
        "sort": "created",
        "order": "desc",
        "per_page": per_page
    }

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            url,
            params=params,
            headers=headers
        )

        response.raise_for_status()

        return response.json()
