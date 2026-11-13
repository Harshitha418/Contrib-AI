
import asyncio
from app.services.github_service import search_beginner_issues


async def main():
    print("Searching for beginner-friendly GitHub issues...\n")

    try:
        result = await search_beginner_issues(per_page=5)

        print(f"Total issues found: {result['total_count']}\n")

        for issue in result["items"]:
            print(f"Title: {issue['title']}")
            print(f"Repository: {issue['repository_url'].split('/repos/')[-1]}")
            print(f"URL: {issue['html_url']}")
            print("-" * 50)

    except Exception as error:
        print(f"Something went wrong: {error}")


if __name__ == "__main__":
    asyncio.run(main())
