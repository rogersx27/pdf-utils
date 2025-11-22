"""
FastAPI REST API for PDF Analyzer
Entry point for the PDF analysis REST API service.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import logging

from app.core.config import settings
from app.core.middleware import (
    ErrorHandlerMiddleware,
    RequestLoggingMiddleware,
    CORSHeadersMiddleware,
    RequestIDMiddleware
)
from app.core.docs_html import get_redoc_html, get_swagger_html
from app.api.v1.router import api_router as api_router_v1
from app.api.v2.router import api_router as api_router_v2

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# ============================================================================
# Lifespan Events (Modern FastAPI pattern)
# ============================================================================

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    This replaces the deprecated @app.on_event("startup") and 
    @app.on_event("shutdown") decorators.
    
    Args:
        app_instance: FastAPI application instance
    """
    # Startup
    logger.info("Starting %s v%s", settings.api_title, settings.api_version)
    logger.info("Environment: %s", settings.environment)
    logger.info("Data directory: %s", settings.data_dir)
    logger.info("API documentation available at: http://%s:%s/docs", settings.host, settings.port)
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("Shutting down %s", settings.api_title)

# Create FastAPI app instance
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url=None,  # Disable default docs to use custom
    redoc_url=None,  # Disable default redoc to use custom
    openapi_url="/openapi.json",  # Explicitly set OpenAPI URL
    lifespan=lifespan,  # Use lifespan context manager
    contact={
        "name": "PDF Analyzer API",
        "url": "https://github.com/rogersx27/pdf-utils",
    },
    license_info={
        "name": "MIT",
    },
    responses={
        200: {"description": "Successful response"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

# ============================================================================
# Middleware Configuration (order matters!)
# ============================================================================

# 1. CORS middleware (first to handle preflight requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origins] if isinstance(settings.cors_origins, str) else settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Request ID middleware (generate ID for tracking)
app.add_middleware(RequestIDMiddleware)

# 3. Request logging middleware (log all requests/responses)
app.add_middleware(RequestLoggingMiddleware)

# 4. Custom CORS headers middleware
app.add_middleware(CORSHeadersMiddleware)

# 5. Error handler middleware (catch all exceptions - should be last)
app.add_middleware(ErrorHandlerMiddleware)

# ============================================================================
# Router Configuration
# ============================================================================

# Include API routers
app.include_router(api_router_v1)  # V1 - Original endpoints
app.include_router(api_router_v2)  # V2 - Controller-based endpoints

# ============================================================================
# Custom Documentation Endpoints
# ============================================================================

@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def custom_swagger_ui():
    """Custom Swagger UI documentation"""
    return get_swagger_html(
        openapi_url="/openapi.json",
        title=settings.api_title
    )


@app.get("/redoc", response_class=HTMLResponse, include_in_schema=False)
async def custom_redoc():
    """Custom ReDoc documentation"""
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=settings.api_title
    )

# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "api": settings.api_title,
        "version": settings.api_version,
        "environment": settings.environment,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "health": "/health",
        "versions": {
            "v1": {
                "prefix": "/api/v1",
                "description": "Original API endpoints",
                "status": "stable"
            },
            "v2": {
                "prefix": "/api/v2",
                "description": "Controller-based API endpoints with improved architecture",
                "status": "stable",
                "features": [
                    "MVC-inspired controller pattern",
                    "Reusable business logic",
                    "Enhanced error handling",
                    "Batch operations support"
                ]
            }
        }
    }


# ============================================================================
# Run the application
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level
    )

