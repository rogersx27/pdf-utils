"""
Common FastAPI dependencies.

Provides reusable dependency functions for endpoints like
pagination, authentication, validation, etc.
"""
from typing import Optional, Annotated
from fastapi import Depends, Header, Query, Request
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import (
    PDFPasswordError,
    PDFNotFoundError,
    InvalidFilenameError
)
from app.schemas.common import PaginationParams, SortParams


# ============================================================================
# Password Dependencies
# ============================================================================

async def get_pdf_password(
    x_pdf_password: Annotated[
        Optional[str],
        Header(
            description="PDF password for encrypted files",
            alias="X-PDF-Password"
        )
    ] = None,
    password: Annotated[
        Optional[str],
        Query(description="PDF password (alternative to header)")
    ] = None
) -> Optional[str]:
    """
    Extract PDF password from header or query parameter.
    
    Priority: Header > Query > Settings default
    
    Returns:
        PDF password or None
    """
    return x_pdf_password or password or settings.pdf_password or None


async def require_pdf_password(
    password: Annotated[Optional[str], Depends(get_pdf_password)]
) -> str:
    """
    Require PDF password (raise error if not provided).
    
    Returns:
        PDF password
        
    Raises:
        PDFPasswordError: If password is not provided
    """
    if not password:
        raise PDFPasswordError(
            "PDF password required. Provide via 'X-PDF-Password' header or 'password' query parameter."
        )
    return password


# ============================================================================
# Pagination Dependencies
# ============================================================================

async def get_pagination_params(
    page: Annotated[
        int,
        Query(ge=1, description="Page number (1-indexed)")
    ] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100, description="Items per page")
    ] = 20
) -> PaginationParams:
    """
    Get pagination parameters from query.
    
    Returns:
        PaginationParams object
    """
    return PaginationParams(page=page, page_size=page_size)


# ============================================================================
# Sorting Dependencies
# ============================================================================

async def get_sort_params(
    sort_by: Annotated[
        Optional[str],
        Query(description="Field to sort by")
    ] = None,
    sort_order: Annotated[
        Optional[str],
        Query(pattern="^(asc|desc)$", description="Sort order")
    ] = "asc"
) -> SortParams:
    """
    Get sorting parameters from query.
    
    Returns:
        SortParams object
    """
    return SortParams(sort_by=sort_by, sort_order=sort_order)


# ============================================================================
# File Path Dependencies
# ============================================================================

async def validate_pdf_filename(filename: str) -> str:
    """
    Validate PDF filename format.
    
    Args:
        filename: PDF filename to validate
        
    Returns:
        Validated filename
        
    Raises:
        InvalidFilenameError: If filename format is invalid
    """
    # Basic validation
    if not filename.endswith(".pdf"):
        raise InvalidFilenameError(filename)
    
    if not filename.startswith("Extracto_"):
        raise InvalidFilenameError(filename)
    
    # Validate format: Extracto_{id}_{YYYYMM}_{tipo}_{numero}.pdf
    parts = filename.replace(".pdf", "").split("_")
    
    if len(parts) < 5:
        raise InvalidFilenameError(filename)
    
    # Validate date format (YYYYMM)
    date_part = parts[2]
    if len(date_part) != 6 or not date_part.isdigit():
        raise InvalidFilenameError(filename)
    
    return filename


async def get_pdf_path(
    filename: Annotated[str, Depends(validate_pdf_filename)]
) -> Path:
    """
    Get full path to PDF file and verify it exists.
    
    Args:
        filename: Validated PDF filename
        
    Returns:
        Path to PDF file
        
    Raises:
        PDFNotFoundError: If file doesn't exist
    """
    pdf_path = settings.data_dir / filename
    
    if not pdf_path.exists():
        raise PDFNotFoundError(filename)
    
    return pdf_path


# ============================================================================
# Request Context Dependencies
# ============================================================================

async def get_request_id(request: Request) -> str:
    """
    Get unique request ID from request state.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Request ID string
    """
    return getattr(request.state, 'request_id', 'unknown')


async def get_client_info(request: Request) -> dict[str, Optional[str]]:
    """
    Extract client information from request.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Dictionary with client info (host, user_agent, etc.)
    """
    return {
        "host": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "referer": request.headers.get("referer"),
        "request_id": await get_request_id(request)
    }


# ============================================================================
# Type Aliases for Common Dependencies
# ============================================================================

# Pagination
PaginationDep = Annotated[PaginationParams, Depends(get_pagination_params)]

# Sorting
SortingDep = Annotated[SortParams, Depends(get_sort_params)]

# Password (optional)
OptionalPasswordDep = Annotated[Optional[str], Depends(get_pdf_password)]

# Password (required)
RequiredPasswordDep = Annotated[str, Depends(require_pdf_password)]

# PDF File Path
PDFPathDep = Annotated[Path, Depends(get_pdf_path)]

# Request ID
RequestIDDep = Annotated[str, Depends(get_request_id)]

# Client Info
ClientInfoDep = Annotated[dict, Depends(get_client_info)]
