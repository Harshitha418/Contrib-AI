
from fastapi import FastAPI
from app.api.github import router as github_router

app = FastAPI(
    title="ContribAI",
    description="AI-powered Open Source Contribution Assistant",
    version="0.1.0"
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to ContribAI!",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "application": "ContribAI"
    }


app.include_router(
    github_router,
    prefix="/api/v1/github",
    tags=["GitHub"]
)
