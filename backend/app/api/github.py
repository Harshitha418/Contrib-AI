from fastapi import APIRouter, HTTPException, Query
import httpx

from app.services.github_service import (
    search_java_repositories,
    search_beginner_issues
)

router = APIRouter()


@router.get("/repositories")
async def get_repositories(
    per_page: int = Query(default=10, ge=1, le=100)
):
    try:
        result = await search_java_repositories(per_page)

        return {
            "total_count": result["total_count"],
            "repositories": result["items"]
        }

    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=error.response.status_code,
            detail="GitHub API returned an error."
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to GitHub."
        )


@router.get("/issues")
async def get_issues(
    per_page: int = Query(default=10, ge=1, le=100)
):
    try:
        result = await search_beginner_issues(per_page)

        return {
            "total_count": result["total_count"],
            "candidates_checked": result["candidates_checked"],
            "issues": result["issues"]
        }

    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=error.response.status_code,
            detail="GitHub API returned an error."
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to GitHub."
        )