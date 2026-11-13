from fastapi import FastAPI

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