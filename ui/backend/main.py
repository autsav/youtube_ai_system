from __future__ import annotations

import sys
from pathlib import Path

# Add repo root to path (2 levels up from ui/backend/main.py)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.pipeline import router as pipeline_router
from api.projects import router as projects_router

app = FastAPI(
    title="YouTube AI Pipeline API",
    description="FastAPI backend for AI YouTube content generation pipeline",
    version="0.1.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects_router)
app.include_router(pipeline_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
