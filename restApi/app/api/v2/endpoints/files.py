"""
File Management Endpoints - V2 API for file operations

This module defines REST endpoints for file management operations
using FileController for business logic handling.
"""
from typing import Annotated, Optional
from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse

from app.controllers import FileController
from app.core import (
    log_endpoint,
    validate_filename_format,
)
from app.schemas import (
    FileOperationResponse,
    OrganizationResultSchema,
    PDFRegistrySchema,
)


router = APIRouter(prefix="/files", tags=["File Management"])


def get_file_controller() -> FileController:
    """
    Dependency to create FileController instance.
    
    Returns:
        FileController instance
    """
    return FileController()


# ============================================================================
# File Operations
# ============================================================================

@router.post(
    "/copy",
    response_model=FileOperationResponse,
    summary="Copy a PDF file",
    description="Copy a PDF file to a new location"
)
@log_endpoint
async def copy_file(
    source: str = Query(..., description="Source filename"),
    destination: str = Query(..., description="Destination path"),
    overwrite: bool = Query(False, description="Overwrite if file exists"),
    controller: FileController = Depends(get_file_controller)
) -> JSONResponse:
    """
    Copy a PDF file.
    
    Args:
    - **source**: Source PDF filename
    - **destination**: Destination path (can be filename or directory)
    - **overwrite**: Whether to overwrite if destination exists
    
    Returns operation status and details.
    """
    return await controller.copy_file(source, destination, overwrite)


@router.post(
    "/move",
    response_model=FileOperationResponse,
    summary="Move a PDF file",
    description="Move a PDF file to a new location"
)
@log_endpoint
async def move_file(
    source: str = Query(..., description="Source filename"),
    destination: str = Query(..., description="Destination path"),
    overwrite: bool = Query(False, description="Overwrite if file exists"),
    controller: FileController = Depends(get_file_controller)
) -> JSONResponse:
    """
    Move a PDF file.
    
    Args:
    - **source**: Source PDF filename
    - **destination**: Destination path (can be filename or directory)
    - **overwrite**: Whether to overwrite if destination exists
    
    Returns operation status and details.
    """
    return await controller.move_file(source, destination, overwrite)


@router.post(
    "/rename",
    response_model=FileOperationResponse,
    summary="Rename a PDF file",
    description="Rename a PDF file within the same directory"
)
@log_endpoint
@validate_filename_format()
async def rename_file(
    source: str = Query(..., description="Source filename"),
    new_name: str = Query(..., description="New filename"),
    controller: FileController = Depends(get_file_controller)
) -> JSONResponse:
    """
    Rename a PDF file.
    
    Args:
    - **source**: Current filename
    - **new_name**: New filename (must follow Extracto_* format)
    
    Returns operation status and details.
    """
    return await controller.rename_file(source, new_name)


@router.delete(
    "/{filename}",
    response_model=FileOperationResponse,
    summary="Delete a PDF file",
    description="Permanently delete a PDF file"
)
@log_endpoint
@validate_filename_format()
async def delete_file(
    filename: str,
    controller: FileController = Depends(get_file_controller)
) -> JSONResponse:
    """
    Delete a PDF file.
    
    **Warning**: This operation is permanent and cannot be undone.
    
    Args:
    - **filename**: PDF filename to delete
    
    Returns operation status.
    """
    return await controller.delete_file(filename)


# ============================================================================
# Organization Operations
# ============================================================================

@router.post(
    "/organize",
    response_model=OrganizationResultSchema,
    summary="Organize PDFs by criteria",
    description="Organize PDF files into folders by type and/or year"
)
@log_endpoint
async def organize_files(
    by_type: bool = Query(True, description="Organize by document type"),
    by_year: bool = Query(True, description="Organize by year"),
    dry_run: bool = Query(False, description="Preview changes without applying"),
    controller: FileController = Depends(get_file_controller)
) -> JSONResponse:
    """
    Organize PDF files into a structured folder hierarchy.
    
    Organization options:
    - **by_type**: Group by document type (CTA_AHORROS, TARJETA_MASTERCARD, etc.)
    - **by_year**: Group by year extracted from date
    - **dry_run**: Preview the organization without actually moving files
    
    Returns:
    - Number of files organized
    - Folder structure created
    - List of file movements
    """
    return await controller.organize_files(by_type, by_year, dry_run)


# ============================================================================
# Registry & Inventory
# ============================================================================

@router.post(
    "/registry/create",
    response_model=PDFRegistrySchema,
    summary="Create file registry",
    description="Generate an inventory of all PDF files"
)
@log_endpoint
async def create_registry(
    output_format: str = Query(
        "json",
        description="Output format (json, csv, excel)",
        regex="^(json|csv|excel)$"
    ),
    output_filename: Optional[str] = Query(None, description="Custom output filename"),
    controller: FileController = Depends(get_file_controller)
) -> JSONResponse:
    """
    Create a complete registry/inventory of all PDF files.
    
    Generates a structured inventory with:
    - Filename and path
    - Document metadata (ID, date, type, number)
    - File size
    - Last modified date
    
    Export formats:
    - **json**: JSON file
    - **csv**: CSV spreadsheet
    - **excel**: Excel workbook
    
    Returns registry details and download information.
    """
    return await controller.create_registry(output_format, output_filename)


@router.get(
    "/stats",
    summary="Get file statistics",
    description="Retrieve statistics about PDF files in the repository"
)
@log_endpoint
async def get_file_stats(
    controller: FileController = Depends(get_file_controller)
) -> JSONResponse:
    """
    Get statistics about the PDF file collection.
    
    Returns:
    - Total file count
    - Files by document type
    - Files by year
    - Total storage size
    - Date range coverage
    """
    return await controller.get_file_stats()
