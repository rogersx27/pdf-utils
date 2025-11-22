"""
Import configuration for pdf_analyzer and data_processor modules.

This module handles the sys.path configuration needed to import from src/
and provides centralized imports for all services.

Usage:
    from app.services.setup_imports import (
        # PDF Analyzer imports
        LocalPDFRepository, PDFDocument, PDFDocumentInfo,
        list_pdfs, extract_text, extract_tables, ...

        # File Manager imports
        copy_pdf, move_pdf, PDFOrganizer, PDFRegistry, ...

        # Data Processor imports
        SavingsAccountProcessor, CreditCardProcessor,
    )
"""
import sys
from pathlib import Path

# Configure sys.path once for all services
_project_root = Path(__file__).parent.parent.parent.parent.parent  # EXTRACTOS/
_src_path = _project_root / "src"

if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

# =============================================================================
# PDF Analyzer Imports
# =============================================================================

from pdf_analyzer import (
    # Repository
    LocalPDFRepository,
    PDFDocument,
    PDFDocumentInfo,
    # Convenience functions
    list_pdfs,
    extract_text,
    extract_tables,
    get_metadata,
    get_page_count,
    is_encrypted,
    search_in_pdf,
    analyze,
    # Extractors
    SavingsAccountExtractor,
    CreditCardExtractor,
)

# =============================================================================
# File Manager Imports
# =============================================================================

from pdf_analyzer.file_manager import (
    copy_pdf,
    move_pdf,
    rename_pdf,
    delete_pdf,
    get_file_info,
    PDFOrganizer,
    PDFRegistry,
)

# =============================================================================
# Data Processor Imports
# =============================================================================

from data_processor import (
    SavingsAccountProcessor,
    CreditCardProcessor,
)

# =============================================================================
# Export all imports for easy access
# =============================================================================

__all__ = [
    # PDF Analyzer - Repository
    "LocalPDFRepository",
    "PDFDocument",
    "PDFDocumentInfo",
    # PDF Analyzer - Convenience functions
    "list_pdfs",
    "extract_text",
    "extract_tables",
    "get_metadata",
    "get_page_count",
    "is_encrypted",
    "search_in_pdf",
    "analyze",
    # PDF Analyzer - Extractors
    "SavingsAccountExtractor",
    "CreditCardExtractor",
    # File Manager
    "copy_pdf",
    "move_pdf",
    "rename_pdf",
    "delete_pdf",
    "get_file_info",
    "PDFOrganizer",
    "PDFRegistry",
    # Data Processor
    "SavingsAccountProcessor",
    "CreditCardProcessor",
]
