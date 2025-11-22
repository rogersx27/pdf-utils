"""
Schemas package - Pydantic models for validation

This package contains all request/response schemas for the API.
All schemas inherit from BaseSchema for consistent configuration.
"""

from .common import (
    # Base
    BaseSchema,
    
    # Response wrappers
    SuccessResponse,
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
    
    # Pagination
    PaginationMeta,
    
    # Common responses
    HealthResponse,
    APIInfoResponse,
    MessageResponse,
    
    # Request parameters
    PaginationParams,
    SortParams,
    FilterParams,
)

__all__ = [
    # Base
    "BaseSchema",
    
    # Response wrappers
    "SuccessResponse",
    "ErrorDetail",
    "ErrorResponse",
    "PaginatedResponse",
    
    # Pagination
    "PaginationMeta",
    
    # Common responses
    "HealthResponse",
    "APIInfoResponse",
    "MessageResponse",
    
    # Request parameters
    "PaginationParams",
    "SortParams",
    "FilterParams",
]

