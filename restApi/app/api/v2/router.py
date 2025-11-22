"""
API v2 router - Controller-based endpoints

This version uses the MVC-inspired controller pattern for better
separation of concerns, testability, and code reusability.

Key improvements over v1:
- Controllers handle business logic
- Cleaner endpoint definitions
- Reusable concerns (mixins)
- Better error handling
- Consistent response format
"""
from fastapi import APIRouter

from app.api.v2.endpoints import pdfs, files, exports

# Create main v2 router
api_router = APIRouter()

# Include all endpoint modules
api_router.include_router(
    pdfs.router,
    prefix="/api/v2",
    tags=["V2 - PDFs"]
)

api_router.include_router(
    files.router,
    prefix="/api/v2",
    tags=["V2 - Files"]
)

api_router.include_router(
    exports.router,
    prefix="/api/v2",
    tags=["V2 - Export"]
)

__all__ = ["api_router"]
