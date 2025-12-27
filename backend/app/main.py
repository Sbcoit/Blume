"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title="Blume API",
    description="Personal secretary agent platform API",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Blume API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Import routers
from app.api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")

