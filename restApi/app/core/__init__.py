"""
Core package - Configuration and utilities

This package provides the foundational components for the API:
- Configuration and settings
- Custom exceptions
- Response utilities
- Middleware components
- Decorators for endpoints
- Common dependencies
- Documentation HTML templates
"""

# Configuration
from .config import settings

# Exceptions
from .exceptions import (
    # Base
    PDFAnalyzerException,
    
    # Client errors (4xx)
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    UnprocessableEntityError,
    
    # PDF-specific
    PDFNotFoundError,
    PDFPasswordError,
    PDFParsingError,
    InvalidPDFFormatError,
    InvalidFilenameError,
    
    # Server errors (5xx)
    InternalServerError,
    ServiceUnavailableError,
    ExtractionError,
    ValidationError,
)

# Response utilities
from .responses import (
    APIResponse,
    success_response,
    error_response,
    paginated_response,
)

# Middleware
from .middleware import (
    ErrorHandlerMiddleware,
    RequestLoggingMiddleware,
    CORSHeadersMiddleware,
    RequestIDMiddleware,
)

# Decorators
from .decorators import (
    log_endpoint,
    require_password,
    validate_filename_format,
    cache_response,
    handle_not_found,
    require_fields,
    timing_decorator,
    handle_controller_errors,
)

# Dependencies
from .dependencies import (
    # Functions
    get_pdf_password,
    require_pdf_password,
    get_pagination_params,
    get_sort_params,
    validate_pdf_filename,
    get_pdf_path,
    get_request_id,
    get_client_info,
    
    # Type aliases
    PaginationDep,
    SortingDep,
    OptionalPasswordDep,
    RequiredPasswordDep,
    PDFPathDep,
    RequestIDDep,
    ClientInfoDep,
)

__all__ = [
    # Config
    "settings",
    
    # Exceptions
    "PDFAnalyzerException",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "ConflictError",
    "UnprocessableEntityError",
    "PDFNotFoundError",
    "PDFPasswordError",
    "PDFParsingError",
    "InvalidPDFFormatError",
    "InvalidFilenameError",
    "InternalServerError",
    "ServiceUnavailableError",
    "ExtractionError",
    "ValidationError",
    
    # Responses
    "APIResponse",
    "success_response",
    "error_response",
    "paginated_response",
    
    # Middleware
    "ErrorHandlerMiddleware",
    "RequestLoggingMiddleware",
    "CORSHeadersMiddleware",
    "RequestIDMiddleware",
    
    # Decorators
    "log_endpoint",
    "require_password",
    "validate_filename_format",
    "cache_response",
    "handle_not_found",
    "require_fields",
    "timing_decorator",
    "handle_controller_errors",
    
    # Dependencies
    "get_pdf_password",
    "require_pdf_password",
    "get_pagination_params",
    "get_sort_params",
    "validate_pdf_filename",
    "get_pdf_path",
    "get_request_id",
    "get_client_info",
    "PaginationDep",
    "SortingDep",
    "OptionalPasswordDep",
    "RequiredPasswordDep",
    "PDFPathDep",
    "RequestIDDep",
    "ClientInfoDep",
]

