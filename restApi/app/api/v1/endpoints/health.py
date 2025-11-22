"""
Health check endpoints
"""
from fastapi import APIRouter

from app.schemas.common import HealthResponse
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=HealthResponse, tags=["Health"])
async def root():
    """Root endpoint - API information"""
    return HealthResponse(
        status="online",
        message="PDF Analyzer API is running",
        version=settings.api_version
    )


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="API is operational",
        version=settings.api_version
    )
