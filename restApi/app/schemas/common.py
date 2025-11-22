"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional


class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str
    message: str
    version: str


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None


class APIInfoResponse(BaseModel):
    """API information response schema"""
    api_name: str
    version: str
    environment: str
    endpoints: dict
    features: list[str]
