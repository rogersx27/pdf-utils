"""
System information endpoints
"""
from fastapi import APIRouter

from app.schemas.common import APIInfoResponse
from app.core.config import settings

router = APIRouter()


@router.get("/info", response_model=APIInfoResponse, tags=["System"])
async def api_info():
    """Get API information and available endpoints"""
    return APIInfoResponse(
        api_name=settings.api_title,
        version=settings.api_version,
        environment=settings.environment,
        endpoints={
            "/": "Root endpoint",
            "/health": "Health check",
            "/docs": "Interactive API documentation (Swagger UI)",
            "/redoc": "Alternative API documentation (ReDoc)",
            "/api/v1/info": "API information"
        },
        features=[
            "PDF document analysis",
            "Bank statement extraction",
            "Transaction data processing"
        ]
    )
