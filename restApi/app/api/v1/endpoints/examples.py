"""
Example endpoint - Demonstrates core features usage

This endpoint showcases how to use all the core components:
- Exceptions
- Responses
- Decorators
- Dependencies
- Schemas
"""
from fastapi import APIRouter, Query
from typing import Annotated

from app.core import (
    # Decorators
    log_endpoint,
    validate_filename_format,
    cache_response,
    handle_not_found,
    
    # Dependencies
    PaginationDep,
    SortingDep,
    OptionalPasswordDep,
    RequiredPasswordDep,
    PDFPathDep,
    RequestIDDep,
    
    # Responses
    success_response,
    paginated_response,
    APIResponse,
    
    # Exceptions
    PDFParsingError,
    InvalidFilenameError,
)
from app.schemas import BaseSchema, MessageResponse

router = APIRouter(prefix="/examples", tags=["Examples"])


# ============================================================================
# Example Schemas
# ============================================================================

class ExampleData(BaseSchema):
    """Example data schema"""
    id: int
    name: str
    description: str


class PDFInfo(BaseSchema):
    """PDF information schema"""
    filename: str
    path: str
    size_bytes: int
    exists: bool


# ============================================================================
# Example 1: Simple endpoint with logging
# ============================================================================

@router.get("/simple", response_model=MessageResponse)
@log_endpoint
async def simple_example():
    """
    Simple endpoint that demonstrates logging.
    
    The @log_endpoint decorator will automatically log:
    - When the endpoint is called
    - How long it takes to execute
    - Any errors that occur
    """
    return {
        "message": "This endpoint execution is being logged",
        "status": "success"
    }


# ============================================================================
# Example 2: Using dependencies for pagination and sorting
# ============================================================================

@router.get("/paginated")
@log_endpoint
async def paginated_example(
    pagination: PaginationDep,
    sort: SortingDep
):
    """
    Demonstrates pagination and sorting using dependencies.
    
    Try:
    - /examples/paginated?page=1&page_size=10
    - /examples/paginated?page=2&page_size=20&sort_by=name&sort_order=desc
    """
    # Simulate data
    all_items = [
        {"id": i, "name": f"Item {i}", "value": i * 10}
        for i in range(1, 101)
    ]
    
    # Apply sorting
    if sort.sort_by and sort.sort_by in ["id", "name", "value"]:
        reverse = sort.sort_order == "desc"
        all_items.sort(key=lambda x: x[sort.sort_by], reverse=reverse)
    
    # Apply pagination
    start = pagination.offset
    end = start + pagination.page_size
    page_items = all_items[start:end]
    
    return paginated_response(
        data=page_items,
        page=pagination.page,
        page_size=pagination.page_size,
        total=len(all_items),
        message="Items retrieved successfully"
    )


# ============================================================================
# Example 3: Password handling
# ============================================================================

@router.post("/with-optional-password")
@log_endpoint
async def optional_password_example(password: OptionalPasswordDep):
    """
    Demonstrates optional password handling.
    
    Try:
    - POST /examples/with-optional-password
    - POST /examples/with-optional-password?password=mypass
    - POST /examples/with-optional-password (with header X-PDF-Password: mypass)
    """
    return success_response(
        data={
            "password_provided": password is not None,
            "password_length": len(password) if password else 0
        },
        message="Optional password endpoint"
    )


@router.post("/with-required-password")
@log_endpoint
async def required_password_example(password: RequiredPasswordDep):
    """
    Demonstrates required password handling.
    
    This endpoint will return 401 if no password is provided.
    
    Try:
    - POST /examples/with-required-password (should fail)
    - POST /examples/with-required-password?password=mypass (should work)
    - POST /examples/with-required-password (with header X-PDF-Password: mypass)
    """
    return success_response(
        data={
            "password_length": len(password),
            "password_hash": hash(password)
        },
        message="Password validation successful"
    )


# ============================================================================
# Example 4: Filename validation and PDF path
# ============================================================================

@router.get("/pdf/{filename}")
@log_endpoint
@validate_filename_format(param_name="filename")
async def pdf_validation_example(
    filename: str,
    pdf_path: PDFPathDep
):
    """
    Demonstrates filename validation and path resolution.
    
    Try:
    - GET /examples/pdf/invalid_name.pdf (should fail - invalid format)
    - GET /examples/pdf/Extracto_123_202401_CTA_AHORROS_1234.pdf (should fail if not exists)
    - GET /examples/pdf/Extracto_455000853_202309_CTA_AHORROS_4332.pdf (should work)
    """
    return success_response(
        data={
            "filename": filename,
            "path": str(pdf_path),
            "exists": pdf_path.exists(),
            "size_bytes": pdf_path.stat().st_size if pdf_path.exists() else 0
        },
        message="PDF validation successful"
    )


# ============================================================================
# Example 5: Cached responses
# ============================================================================

@router.get("/cached")
@log_endpoint
@cache_response(ttl_seconds=60)
async def cached_example():
    """
    Demonstrates response caching.
    
    The first call will execute the function.
    Subsequent calls within 60 seconds will return cached result.
    
    Try calling this endpoint multiple times and watch the logs.
    """
    import time
    timestamp = time.time()
    
    return success_response(
        data={
            "timestamp": timestamp,
            "message": "This response is cached for 60 seconds"
        },
        message="Cached endpoint"
    )


# ============================================================================
# Example 6: Handle not found
# ============================================================================

@router.get("/find/{item_id}")
@log_endpoint
@handle_not_found(resource_name="Item")
async def handle_not_found_example(item_id: int):
    """
    Demonstrates automatic 404 handling.
    
    Try:
    - GET /examples/find/1 (exists - will return data)
    - GET /examples/find/999 (doesn't exist - will return 404)
    """
    # Simulate database lookup
    items = {
        1: {"id": 1, "name": "Item 1"},
        2: {"id": 2, "name": "Item 2"},
        3: {"id": 3, "name": "Item 3"}
    }
    
    # If item_id not found, returns None -> automatic 404
    item = items.get(item_id)
    
    if item:
        return success_response(data=item, message="Item found")
    
    return None  # Will be converted to 404 by @handle_not_found


# ============================================================================
# Example 7: Request tracking
# ============================================================================

@router.post("/tracked")
@log_endpoint
async def request_tracking_example(request_id: RequestIDDep):
    """
    Demonstrates request ID tracking.
    
    Each request gets a unique ID for tracking.
    Check the response headers for X-Request-ID.
    """
    return success_response(
        data={
            "request_id": request_id,
            "message": "Check response headers for X-Request-ID"
        },
        message="Request tracked successfully"
    )


# ============================================================================
# Example 8: Exception handling
# ============================================================================

@router.get("/error-demo")
@log_endpoint
async def error_demo_example(
    error_type: Annotated[
        str,
        Query(
            description="Type of error to demonstrate",
            pattern="^(parsing|invalid_filename|none)$"
        )
    ] = "none"
):
    """
    Demonstrates custom exception handling.
    
    Try:
    - GET /examples/error-demo?error_type=parsing
    - GET /examples/error-demo?error_type=invalid_filename
    - GET /examples/error-demo?error_type=none
    """
    if error_type == "parsing":
        raise PDFParsingError("Simulated PDF parsing error")
    
    elif error_type == "invalid_filename":
        raise InvalidFilenameError("bad_filename.pdf")
    
    return success_response(
        data={"error_type": error_type},
        message="No error raised"
    )


# ============================================================================
# Example 9: Different response types
# ============================================================================

@router.post("/create-resource")
@log_endpoint
async def create_resource_example():
    """
    Demonstrates 201 Created response.
    """
    new_resource = {
        "id": 123,
        "name": "New Resource",
        "created_at": "2025-11-22T10:00:00Z"
    }
    
    return APIResponse.created(
        data=new_resource,
        message="Resource created successfully"
    )


@router.post("/async-operation")
@log_endpoint
async def async_operation_example():
    """
    Demonstrates 202 Accepted response for async operations.
    """
    operation_id = "op_123456"
    
    return APIResponse.accepted(
        data={
            "operation_id": operation_id,
            "status": "processing",
            "check_status_url": f"/api/v1/operations/{operation_id}"
        },
        message="Operation accepted for processing"
    )


@router.delete("/resource/{id}")
@log_endpoint
async def delete_resource_example(id: int):
    """
    Demonstrates 204 No Content response.
    """
    # Simulate deletion
    return APIResponse.no_content()
