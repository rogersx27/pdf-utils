"""
API v1 router - Aggregates all v1 endpoints
"""
from fastapi import APIRouter

from app.api.v1.endpoints import health, system

api_router = APIRouter()

# Include health endpoints (at root level)
api_router.include_router(health.router, prefix="", tags=["Health"])

# Include system endpoints
api_router.include_router(system.router, prefix="/api/v1", tags=["System"])
