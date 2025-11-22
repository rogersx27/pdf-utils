"""
FastAPI REST API for PDF Analyzer
Entry point for the PDF analysis REST API service.
"""
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from api_config import settings

# Create FastAPI app instance
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origins] if isinstance(settings.cors_origins, str) else settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response validation
class HealthResponse(BaseModel):
    status: str
    message: str
    version: str


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


# Root endpoint
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - API information"""
    return HealthResponse(
        status="online",
        message="PDF Analyzer API is running",
        version=settings.api_version
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="API is operational",
        version=settings.api_version
    )


# API v1 endpoints
@app.get("/api/v1/info")
async def api_info():
    """Get API information and available endpoints"""
    return {
        "api_name": settings.api_title,
        "version": settings.api_version,
        "environment": settings.environment,
        "endpoints": {
            "/": "Root endpoint",
            "/health": "Health check",
            "/docs": "Interactive API documentation (Swagger UI)",
            "/redoc": "Alternative API documentation (ReDoc)",
            "/api/v1/info": "API information"
        },
        "features": [
            "PDF document analysis",
            "Bank statement extraction",
            "Transaction data processing"
        ]
    }


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc)
        }
    )


# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level
    )
