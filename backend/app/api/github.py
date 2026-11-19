import httpx

from fastapi import APIRouter, HTTPException, Query

from app.services.recommendation_service import rank_issues

from app.services.github_service import (
    search_java_repositories,
    search_beginner_issues,
    CACHE_STATS,
    REPOSITORY_CACHE,
    CACHE_TTL,
    ISSUE_CACHE,
    ISSUE_CACHE_TTL
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
    per_page: int = Query(default=10, ge=1, le=100),
    language: str = Query(
        default="Java",
        min_length=1,
        max_length=50
    ),
    label: str = Query(
        default="good first issue",
        min_length=1,
        max_length=50
    ),
    sort_by: str = Query(
        default="created",
        pattern="^(created|updated|comments)$"
    ),
    keyword: str = Query(
        default="",
        max_length=100
    )
):
    try:
        result = await search_beginner_issues(
            per_page=per_page,
            language=language,
            label=label,
            sort_by=sort_by,
            keyword=keyword
        )

        ranked_issues = rank_issues(
            result["issues"],
            keyword=keyword
        )

        return {
            "language": language,
            "label": label,
            "sort_by": sort_by,
            "keyword": keyword,
            "ranking": "keyword_relevance_then_recommendation_score",
            "total_count": result["total_count"],
            "candidates_checked": result["candidates_checked"],
            "issues": ranked_issues
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


@router.get("/cache/stats")
async def get_cache_stats():
    return {
        "cache_hits": CACHE_STATS["hits"],
        "cache_misses": CACHE_STATS["misses"],
        "repositories_cached": len(REPOSITORY_CACHE),
        "issues_cached": len(ISSUE_CACHE),
        "repository_cache_ttl_seconds": CACHE_TTL,
        "issue_cache_ttl_seconds": ISSUE_CACHE_TTL
    }