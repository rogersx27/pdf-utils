"""
Pydantic schemas for request/response validation.

Provides base models and common schemas used across the API.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Optional, Generic, TypeVar
from datetime import datetime

# Generic type for response data
T = TypeVar('T')


# ============================================================================
# Base Models
# ============================================================================

class BaseSchema(BaseModel):
    """
    Base schema with common configuration.
    
    All schemas should inherit from this to ensure consistent behavior.
    """
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True
    )


# ============================================================================
# Response Wrappers
# ============================================================================

class SuccessResponse(BaseSchema, Generic[T]):
    """
    Standard success response wrapper.
    
    Wraps all successful API responses with consistent structure.
    """
    success: bool = Field(default=True, description="Indicates request success")
    message: str = Field(description="Human-readable success message")
    data: T = Field(description="Response payload data")
    meta: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional metadata (pagination, etc.)"
    )


class ErrorDetail(BaseSchema):
    """Error detail structure"""
    code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error message")
    details: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="Additional error details"
    )


class ErrorResponse(BaseSchema):
    """
    Standard error response.
    
    Used for all error responses across the API.
    """
    success: bool = Field(default=False, description="Always false for errors")
    error: ErrorDetail = Field(description="Error information")


# ============================================================================
# Pagination
# ============================================================================

class PaginationMeta(BaseSchema):
    """Pagination metadata"""
    page: int = Field(ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(ge=1, le=100, description="Number of items per page")
    total_items: int = Field(ge=0, description="Total number of items")
    total_pages: int = Field(ge=0, description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_previous: bool = Field(description="Whether there is a previous page")


class PaginatedResponse(BaseSchema, Generic[T]):
    """
    Paginated response wrapper.
    
    Used for endpoints that return lists with pagination.
    """
    success: bool = Field(default=True, description="Indicates request success")
    message: str = Field(default="Success", description="Success message")
    data: list[T] = Field(description="List of items for current page")
    meta: dict[str, PaginationMeta] = Field(description="Pagination metadata")


# ============================================================================
# Common Response Schemas
# ============================================================================

class HealthResponse(BaseSchema):
    """Health check response schema"""
    status: str = Field(description="Service status (healthy/unhealthy)")
    message: str = Field(description="Health check message")
    version: str = Field(description="API version")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Health check timestamp"
    )


class APIInfoResponse(BaseSchema):
    """API information response schema"""
    api_name: str = Field(description="API name")
    version: str = Field(description="API version")
    environment: str = Field(description="Environment (development/production)")
    endpoints: dict[str, Any] = Field(description="Available endpoints")
    features: list[str] = Field(description="Available features")


class MessageResponse(BaseSchema):
    """Simple message response"""
    message: str = Field(description="Response message")
    status: Optional[str] = Field(default="success", description="Status indicator")


# ============================================================================
# Request Schemas
# ============================================================================

class PaginationParams(BaseSchema):
    """
    Standard pagination parameters.
    
    Use this for endpoints that support pagination.
    """
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page"
    )
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.page_size


class SortParams(BaseSchema):
    """
    Standard sorting parameters.
    
    Use this for endpoints that support sorting.
    """
    sort_by: Optional[str] = Field(
        default=None,
        description="Field to sort by"
    )
    sort_order: Optional[str] = Field(
        default="asc",
        pattern="^(asc|desc)$",
        description="Sort order (asc/desc)"
    )


class FilterParams(BaseSchema):
    """
    Base class for filter parameters.
    
    Extend this for domain-specific filters.
    """
    pass
