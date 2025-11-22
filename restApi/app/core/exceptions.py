"""
Custom exceptions for the PDF Analyzer API.

This module defines domain-specific exceptions that provide clear error handling
and HTTP status code mapping for different error scenarios.
"""
from typing import Any, Optional
from fastapi import HTTPException, status


class PDFAnalyzerException(HTTPException):
    """
    Base exception for PDF Analyzer API.
    
    All custom exceptions should inherit from this class to ensure
    consistent error handling across the application.
    """
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or self.__class__.__name__


# ============================================================================
# Client Errors (4xx)
# ============================================================================

class BadRequestError(PDFAnalyzerException):
    """Raised when the request is malformed or invalid."""
    
    def __init__(self, detail: str = "Bad request", error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code or "BAD_REQUEST"
        )


class UnauthorizedError(PDFAnalyzerException):
    """Raised when authentication is required but not provided."""
    
    def __init__(self, detail: str = "Unauthorized", error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code or "UNAUTHORIZED",
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenError(PDFAnalyzerException):
    """Raised when the user doesn't have permission to access the resource."""
    
    def __init__(self, detail: str = "Forbidden", error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code or "FORBIDDEN"
        )


class NotFoundError(PDFAnalyzerException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, detail: str = "Resource not found", error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code or "NOT_FOUND"
        )


class ConflictError(PDFAnalyzerException):
    """Raised when there's a conflict with the current state."""
    
    def __init__(self, detail: str = "Conflict", error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code or "CONFLICT"
        )


class UnprocessableEntityError(PDFAnalyzerException):
    """Raised when the request is well-formed but semantically incorrect."""
    
    def __init__(self, detail: str = "Unprocessable entity", error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code or "UNPROCESSABLE_ENTITY"
        )


# ============================================================================
# PDF-Specific Errors
# ============================================================================

class PDFNotFoundError(NotFoundError):
    """Raised when a PDF file is not found."""
    
    def __init__(self, filename: str):
        super().__init__(
            detail=f"PDF file not found: {filename}",
            error_code="PDF_NOT_FOUND"
        )


class PDFPasswordError(UnauthorizedError):
    """Raised when PDF password is incorrect or required."""
    
    def __init__(self, detail: str = "Invalid or missing PDF password"):
        super().__init__(
            detail=detail,
            error_code="PDF_PASSWORD_ERROR"
        )


class PDFParsingError(UnprocessableEntityError):
    """Raised when PDF parsing fails."""
    
    def __init__(self, detail: str = "Failed to parse PDF"):
        super().__init__(
            detail=detail,
            error_code="PDF_PARSING_ERROR"
        )


class InvalidPDFFormatError(BadRequestError):
    """Raised when PDF format is invalid or unsupported."""
    
    def __init__(self, detail: str = "Invalid PDF format"):
        super().__init__(
            detail=detail,
            error_code="INVALID_PDF_FORMAT"
        )


class InvalidFilenameError(BadRequestError):
    """Raised when PDF filename doesn't match expected format."""
    
    def __init__(self, filename: str):
        super().__init__(
            detail=f"Invalid filename format: {filename}. Expected format: Extracto_{{id}}_{{YYYYMM}}_{{tipo}}_{{numero}}.pdf",
            error_code="INVALID_FILENAME"
        )


# ============================================================================
# Server Errors (5xx)
# ============================================================================

class InternalServerError(PDFAnalyzerException):
    """Raised when an unexpected server error occurs."""
    
    def __init__(self, detail: str = "Internal server error", error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code or "INTERNAL_SERVER_ERROR"
        )


class ServiceUnavailableError(PDFAnalyzerException):
    """Raised when a service is temporarily unavailable."""
    
    def __init__(self, detail: str = "Service unavailable", error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code=error_code or "SERVICE_UNAVAILABLE"
        )


# ============================================================================
# Processing Errors
# ============================================================================

class ExtractionError(InternalServerError):
    """Raised when data extraction from PDF fails."""
    
    def __init__(self, detail: str = "Failed to extract data from PDF"):
        super().__init__(
            detail=detail,
            error_code="EXTRACTION_ERROR"
        )


class ValidationError(UnprocessableEntityError):
    """Raised when data validation fails."""
    
    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            detail=detail,
            error_code="VALIDATION_ERROR"
        )
