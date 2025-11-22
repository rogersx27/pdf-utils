"""
Standard HTTP response utilities for the PDF Analyzer API.

Provides consistent response formatting with proper HTTP status codes
and standardized structure across all endpoints.
"""
from typing import Any, Optional
from fastapi import status
from fastapi.responses import JSONResponse


class APIResponse:
    """
    Factory class for creating standardized API responses.
    
    All responses follow a consistent structure with proper HTTP status codes
    and optional metadata.
    """
    
    @staticmethod
    def success(
        data: Any,
        message: str = "Success",
        status_code: int = status.HTTP_200_OK,
        meta: Optional[dict[str, Any]] = None
    ) -> JSONResponse:
        """
        Create a success response.
        
        Args:
            data: The response data
            message: Success message
            status_code: HTTP status code (default: 200)
            meta: Optional metadata (pagination, etc.)
            
        Returns:
            JSONResponse with standardized structure
        """
        content = {
            "success": True,
            "message": message,
            "data": data
        }
        
        if meta:
            content["meta"] = meta
            
        return JSONResponse(
            status_code=status_code,
            content=content
        )
    
    @staticmethod
    def created(
        data: Any,
        message: str = "Resource created successfully",
        meta: Optional[dict[str, Any]] = None
    ) -> JSONResponse:
        """Create a 201 Created response."""
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED,
            meta=meta
        )
    
    @staticmethod
    def accepted(
        data: Any = None,
        message: str = "Request accepted for processing",
        meta: Optional[dict[str, Any]] = None
    ) -> JSONResponse:
        """Create a 202 Accepted response (for async operations)."""
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_202_ACCEPTED,
            meta=meta
        )
    
    @staticmethod
    def no_content() -> JSONResponse:
        """Create a 204 No Content response."""
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
    
    @staticmethod
    def error(
        detail: str,
        error_code: Optional[str] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        errors: Optional[list[dict[str, Any]]] = None
    ) -> JSONResponse:
        """
        Create an error response.
        
        Args:
            detail: Error description
            error_code: Machine-readable error code
            status_code: HTTP status code
            errors: List of specific validation errors
            
        Returns:
            JSONResponse with error structure
        """
        content = {
            "success": False,
            "error": {
                "code": error_code or "ERROR",
                "message": detail
            }
        }
        
        if errors:
            content["error"]["details"] = errors
            
        return JSONResponse(
            status_code=status_code,
            content=content
        )
    
    @staticmethod
    def bad_request(
        detail: str = "Bad request",
        error_code: str = "BAD_REQUEST",
        errors: Optional[list[dict[str, Any]]] = None
    ) -> JSONResponse:
        """Create a 400 Bad Request response."""
        return APIResponse.error(
            detail=detail,
            error_code=error_code,
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=errors
        )
    
    @staticmethod
    def unauthorized(
        detail: str = "Unauthorized",
        error_code: str = "UNAUTHORIZED"
    ) -> JSONResponse:
        """Create a 401 Unauthorized response."""
        return APIResponse.error(
            detail=detail,
            error_code=error_code,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden(
        detail: str = "Forbidden",
        error_code: str = "FORBIDDEN"
    ) -> JSONResponse:
        """Create a 403 Forbidden response."""
        return APIResponse.error(
            detail=detail,
            error_code=error_code,
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def not_found(
        detail: str = "Resource not found",
        error_code: str = "NOT_FOUND"
    ) -> JSONResponse:
        """Create a 404 Not Found response."""
        return APIResponse.error(
            detail=detail,
            error_code=error_code,
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def conflict(
        detail: str = "Conflict",
        error_code: str = "CONFLICT"
    ) -> JSONResponse:
        """Create a 409 Conflict response."""
        return APIResponse.error(
            detail=detail,
            error_code=error_code,
            status_code=status.HTTP_409_CONFLICT
        )
    
    @staticmethod
    def unprocessable_entity(
        detail: str = "Unprocessable entity",
        error_code: str = "UNPROCESSABLE_ENTITY",
        errors: Optional[list[dict[str, Any]]] = None
    ) -> JSONResponse:
        """Create a 422 Unprocessable Entity response."""
        return APIResponse.error(
            detail=detail,
            error_code=error_code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            errors=errors
        )
    
    @staticmethod
    def internal_server_error(
        detail: str = "Internal server error",
        error_code: str = "INTERNAL_SERVER_ERROR"
    ) -> JSONResponse:
        """Create a 500 Internal Server Error response."""
        return APIResponse.error(
            detail=detail,
            error_code=error_code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @staticmethod
    def service_unavailable(
        detail: str = "Service unavailable",
        error_code: str = "SERVICE_UNAVAILABLE"
    ) -> JSONResponse:
        """Create a 503 Service Unavailable response."""
        return APIResponse.error(
            detail=detail,
            error_code=error_code,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


# Convenience functions for common responses
def success_response(
    data: Any,
    message: str = "Success",
    meta: Optional[dict[str, Any]] = None
) -> JSONResponse:
    """Shorthand for successful response."""
    return APIResponse.success(data=data, message=message, meta=meta)


def error_response(
    detail: str,
    error_code: Optional[str] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> JSONResponse:
    """Shorthand for error response."""
    return APIResponse.error(detail=detail, error_code=error_code, status_code=status_code)


def paginated_response(
    data: list[Any],
    page: int,
    page_size: int,
    total: int,
    message: str = "Success"
) -> JSONResponse:
    """
    Create a paginated response with metadata.
    
    Args:
        data: List of items for current page
        page: Current page number (1-indexed)
        page_size: Number of items per page
        total: Total number of items
        message: Success message
        
    Returns:
        JSONResponse with pagination metadata
    """
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    meta = {
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
    }
    
    return APIResponse.success(data=data, message=message, meta=meta)
