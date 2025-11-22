"""
PDF Endpoints - V2 API for PDF operations

This module defines REST endpoints for PDF analysis operations
using PDFController for business logic handling.
"""
from typing import Optional, Annotated
from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse

from app.controllers import PDFController
from app.core import (
    log_endpoint,
    validate_filename_format,
    OptionalPasswordDep,
)
from app.schemas import (
    PDFDocumentSchema,
    PDFMetadataSchema,
    TextExtractionResultSchema,
    TableExtractionResultSchema,
    SearchResultSchema,
    SavingsAccountStatementSchema,
    CreditCardStatementSchema,
)


router = APIRouter(prefix="/pdfs", tags=["PDFs"])


def get_pdf_controller(password: OptionalPasswordDep = None) -> PDFController:
    """
    Dependency to create PDFController instance.
    
    Args:
        password: Optional password from dependency
        
    Returns:
        PDFController instance
    """
    return PDFController(password=password)


# ============================================================================
# PDF Listing & Information
# ============================================================================

@router.get(
    "",
    summary="List all PDFs",
    description="Retrieve a list of all PDF documents with optional filters"
)
@log_endpoint
async def list_pdfs(
    controller: PDFController = Depends(get_pdf_controller),
    tipo: Optional[str] = Query(
        None,
        description="Filter by document type (CTA_AHORROS, TARJETA_MASTERCARD, etc.)"
    ),
    fecha: Optional[str] = Query(
        None,
        description="Filter by date in YYYYMM format",
        regex=r"^\d{6}$"
    )
) -> JSONResponse:
    """
    List all available PDF documents.
    
    Supports filtering by:
    - **tipo**: Document type (CTA_AHORROS, TARJETA_MASTERCARD, COMISIONES_CONSOLIDADAS)
    - **fecha**: Date in YYYYMM format (e.g., 202309)
    
    Returns a list of PDF documents with their metadata.
    """
    return await controller.list_pdfs(tipo=tipo, fecha=fecha)


@router.get(
    "/{filename}",
    response_model=PDFDocumentSchema,
    summary="Get PDF information",
    description="Retrieve detailed information about a specific PDF document"
)
@log_endpoint
@validate_filename_format
async def get_pdf(
    filename: str,
    controller: PDFController = Depends(get_pdf_controller)
) -> JSONResponse:
    """
    Get detailed information about a PDF document.
    
    Returns document metadata including:
    - Filename and path
    - Parsed information (ID, date, type, number)
    - File size and existence
    """
    return await controller.get_pdf(filename)


# ============================================================================
# Text & Table Extraction
# ============================================================================

@router.get(
    "/{filename}/text",
    response_model=TextExtractionResultSchema,
    summary="Extract text from PDF",
    description="Extract all text content from a PDF document"
)
@log_endpoint
@validate_filename_format
async def extract_text(
    filename: str,
    controller: PDFController = Depends(get_pdf_controller),
    password: OptionalPasswordDep = None
) -> JSONResponse:
    """
    Extract text content from a PDF document.
    
    Returns:
    - Full text content
    - Page count
    - Character count
    """
    return await controller.extract_text(filename, password)


@router.get(
    "/{filename}/tables",
    response_model=TableExtractionResultSchema,
    summary="Extract tables from PDF",
    description="Extract all table structures from a PDF document"
)
@log_endpoint
@validate_filename_format
async def extract_tables(
    filename: str,
    controller: PDFController = Depends(get_pdf_controller),
    password: OptionalPasswordDep = None
) -> JSONResponse:
    """
    Extract table structures from a PDF document.
    
    Returns:
    - List of tables with their data
    - Page numbers where tables were found
    - Row and column counts
    """
    return await controller.extract_tables(filename, password)


# ============================================================================
# Search Operations
# ============================================================================

@router.get(
    "/{filename}/search",
    response_model=SearchResultSchema,
    summary="Search text in PDF",
    description="Search for specific text within a PDF document"
)
@log_endpoint
@validate_filename_format
async def search_in_pdf(
    filename: str,
    controller: PDFController = Depends(get_pdf_controller),
    query: str = Query(..., description="Search query string"),
    password: OptionalPasswordDep = None
) -> JSONResponse:
    """
    Search for text within a PDF document.
    
    Returns:
    - Search query
    - Whether text was found
    - Number of occurrences
    - Page numbers where text appears
    """
    return await controller.search_in_pdf(filename, query, password)


# ============================================================================
# Statement Extraction
# ============================================================================

@router.get(
    "/{filename}/extract/savings",
    response_model=SavingsAccountStatementSchema,
    summary="Extract savings account statement",
    description="Extract structured data from a savings account statement PDF"
)
@log_endpoint
@validate_filename_format
async def extract_savings_statement(
    filename: str,
    controller: PDFController = Depends(get_pdf_controller),
    password: OptionalPasswordDep = None
) -> JSONResponse:
    """
    Extract savings account statement data.
    
    Returns structured data including:
    - Account information
    - Financial summary
    - List of transactions
    """
    return await controller.extract_savings_statement(filename, password)


@router.get(
    "/{filename}/extract/credit-card",
    response_model=CreditCardStatementSchema,
    summary="Extract credit card statement",
    description="Extract structured data from a credit card statement PDF"
)
@log_endpoint
@validate_filename_format
async def extract_credit_card_statement(
    filename: str,
    controller: PDFController = Depends(get_pdf_controller),
    password: OptionalPasswordDep = None
) -> JSONResponse:
    """
    Extract credit card statement data.
    
    Returns structured data including:
    - Card information
    - Credit limits and balances
    - Transactions in multiple currencies (COP/USD)
    - Interest rates and payment details
    """
    return await controller.extract_credit_card_statement(filename, password)


# ============================================================================
# Metadata
# ============================================================================

@router.get(
    "/{filename}/metadata",
    response_model=PDFMetadataSchema,
    summary="Get PDF metadata",
    description="Retrieve technical metadata from a PDF document"
)
@log_endpoint
@validate_filename_format
async def get_metadata(
    filename: str,
    controller: PDFController = Depends(get_pdf_controller),
    password: OptionalPasswordDep = None
) -> JSONResponse:
    """
    Get PDF metadata.
    
    Returns technical information including:
    - PDF version
    - Page count
    - Creation/modification dates
    - Author, title, subject
    - Producer information
    """
    return await controller.get_metadata(filename, password)
