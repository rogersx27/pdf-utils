"""
Export Endpoints - V2 API for data export operations

This module defines REST endpoints for exporting PDF data to various formats
using ExportController for business logic handling.
"""
from typing import Annotated, Optional, Literal, List
from fastapi import APIRouter, Query, Path, Depends
from fastapi.responses import JSONResponse, FileResponse

from app.controllers import ExportController
from app.core import (
    log_endpoint,
    validate_filename_format,
    OptionalPasswordDep,
)
from app.schemas import (
    DataExportResponse,
    ValidationResultSchema,
    BatchAnalysisResultSchema,
)


router = APIRouter(prefix="/export", tags=["Data Export"])


def get_export_controller(password: OptionalPasswordDep = None) -> ExportController:
    """
    Dependency to create ExportController instance.
    
    Args:
        password: Optional password from dependency
        
    Returns:
        ExportController instance
    """
    return ExportController(password=password)


# ============================================================================
# Savings Account Export
# ============================================================================

@router.post(
    "/savings/{filename}",
    response_model=DataExportResponse,
    summary="Export savings account data",
    description="Extract and export savings account statement to CSV or Excel"
)
@log_endpoint
@validate_filename_format()
async def export_savings_account(
    filename: str,
    export_format: Literal["csv", "excel"] = Query(
        "excel",
        description="Export format (csv or excel)"
    ),
    output_filename: Optional[str] = Query(
        None,
        description="Custom output filename (without extension)"
    ),
    return_file: bool = Query(
        False,
        description="Return file for download instead of JSON response"
    ),
    controller: ExportController = Depends(get_export_controller),
    password: OptionalPasswordDep = None
) -> JSONResponse | FileResponse:
    """
    Export savings account statement data.
    
    Extracts transaction data and exports to:
    - **CSV**: Simple comma-separated values
    - **Excel**: Formatted spreadsheet with multiple sheets
    
    Args:
    - **filename**: Source PDF filename
    - **export_format**: Output format (csv or excel)
    - **output_filename**: Optional custom output name
    - **return_file**: If true, downloads file directly
    
    Returns export details or file download.
    """
    return await controller.export_savings_account(
        filename=filename,
        export_format=export_format,
        output_filename=output_filename,
        return_file=return_file
    )


@router.post(
    "/savings/{filename}/validate",
    response_model=ValidationResultSchema,
    summary="Validate savings account data",
    description="Validate extracted savings account data before export"
)
@log_endpoint
@validate_filename_format()
async def validate_savings_data(
    filename: str,
    controller: ExportController = Depends(get_export_controller),
    password: OptionalPasswordDep = None
) -> JSONResponse:
    """
    Validate savings account statement data.
    
    Checks:
    - Data completeness
    - Balance calculations
    - Transaction integrity
    - Required fields presence
    
    Returns validation results with any errors or warnings.
    """
    return await controller.validate_savings_data(filename, password)


# ============================================================================
# Credit Card Export
# ============================================================================

@router.post(
    "/credit-card/{filename}",
    response_model=DataExportResponse,
    summary="Export credit card data",
    description="Extract and export credit card statement to CSV or Excel"
)
@log_endpoint
@validate_filename_format()
async def export_credit_card(
    filename: str,
    export_format: Literal["csv", "excel"] = Query(
        "excel",
        description="Export format (csv or excel)"
    ),
    output_filename: Optional[str] = Query(
        None,
        description="Custom output filename (without extension)"
    ),
    return_file: bool = Query(
        False,
        description="Return file for download instead of JSON response"
    ),
    controller: ExportController = Depends(get_export_controller),
    password: OptionalPasswordDep = None
) -> JSONResponse | FileResponse:
    """
    Export credit card statement data.
    
    Extracts transaction data in multiple currencies and exports to:
    - **CSV**: Separate files for COP and USD transactions
    - **Excel**: Multi-sheet workbook with currency separation
    
    Args:
    - **filename**: Source PDF filename
    - **export_format**: Output format (csv or excel)
    - **output_filename**: Optional custom output name
    - **return_file**: If true, downloads file directly
    
    Returns export details or file download.
    """
    return await controller.export_credit_card(
        filename=filename,
        export_format=export_format,
        output_filename=output_filename,
        return_file=return_file
    )


@router.post(
    "/credit-card/{filename}/validate",
    response_model=ValidationResultSchema,
    summary="Validate credit card data",
    description="Validate extracted credit card data before export"
)
@log_endpoint
@validate_filename_format()
async def validate_credit_card_data(
    filename: str,
    controller: ExportController = Depends(get_export_controller),
    password: OptionalPasswordDep = None
) -> JSONResponse:
    """
    Validate credit card statement data.
    
    Checks:
    - Data completeness for both currencies
    - Balance calculations
    - Transaction integrity
    - Required fields presence
    - Currency consistency
    
    Returns validation results with any errors or warnings.
    """
    return await controller.validate_credit_card_data(filename, password)


# ============================================================================
# Batch Export Operations
# ============================================================================

@router.post(
    "/batch/savings",
    response_model=BatchAnalysisResultSchema,
    summary="Batch export savings accounts",
    description="Export multiple savings account statements at once"
)
@log_endpoint
async def batch_export_savings(
    filenames: List[str] = Query(..., description="List of PDF filenames to export"),
    export_format: Literal["csv", "excel"] = Query(
        "excel",
        description="Export format for all files"
    ),
    output_dir: Optional[str] = Query(
        None,
        description="Custom output directory"
    ),
    controller: ExportController = Depends(get_export_controller),
    password: OptionalPasswordDep = None
) -> JSONResponse:
    """
    Batch export multiple savings account statements.
    
    Processes multiple PDFs and exports each to the specified format.
    
    Args:
    - **filenames**: List of PDF filenames
    - **export_format**: Output format (csv or excel)
    - **output_dir**: Optional output directory
    
    Returns:
    - Total processed count
    - Success/failure breakdown
    - List of exported files
    - Any errors encountered
    """
    return await controller.batch_export_savings(
        filenames=filenames,
        export_format=export_format,
        output_dir=output_dir,
        password=password
    )


@router.post(
    "/batch/credit-cards",
    response_model=BatchAnalysisResultSchema,
    summary="Batch export credit cards",
    description="Export multiple credit card statements at once"
)
@log_endpoint
async def batch_export_credit_cards(
    filenames: List[str] = Query(..., description="List of PDF filenames to export"),
    export_format: Literal["csv", "excel"] = Query(
        "excel",
        description="Export format for all files"
    ),
    output_dir: Optional[str] = Query(
        None,
        description="Custom output directory"
    ),
    controller: ExportController = Depends(get_export_controller),
    password: OptionalPasswordDep = None
) -> JSONResponse:
    """
    Batch export multiple credit card statements.
    
    Processes multiple PDFs and exports each to the specified format.
    
    Args:
    - **filenames**: List of PDF filenames
    - **export_format**: Output format (csv or excel)
    - **output_dir**: Optional output directory
    
    Returns:
    - Total processed count
    - Success/failure breakdown
    - List of exported files
    - Any errors encountered
    """
    return await controller.batch_export_credit_cards(
        filenames=filenames,
        export_format=export_format,
        output_dir=output_dir,
        password=password
    )


# ============================================================================
# Export Templates & Formats
# ============================================================================

@router.get(
    "/formats",
    summary="Get available export formats",
    description="List all available export formats and their capabilities"
)
@log_endpoint
async def get_export_formats(
    controller: ExportController = Depends(get_export_controller)
) -> JSONResponse:
    """
    Get information about available export formats.
    
    Returns:
    - Supported formats
    - Format capabilities
    - File extensions
    - Recommended use cases
    """
    return await controller.get_export_formats()


@router.get(
    "/template/{document_type}",
    summary="Get export template",
    description="Download a template showing the export structure"
)
@log_endpoint
async def get_export_template(
    document_type: Literal["savings", "credit_card"],
    export_format: Literal["csv", "excel"] = Query(
        "excel",
        description="Template format"
    ),
    controller: ExportController = Depends(get_export_controller)
) -> FileResponse:
    """
    Download an export template.
    
    Provides a sample template showing:
    - Column structure
    - Data types
    - Expected formats
    - Sample data
    
    Useful for understanding the export format before processing.
    """
    return await controller.get_export_template(document_type, export_format)
