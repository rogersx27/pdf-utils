"""
Base infrastructure for services.

Contains shared concerns (mixins), constants, and import configuration.
"""

from .concerns import (
    PathResolvableMixin,
    PasswordAwareMixin,
    ExceptionMapperMixin,
    OutputDirectoryMixin,
    BaseService,
    ExportableService,
    with_path_validation,
    with_exception_mapping,
)

from .imports import (
    # PDF Analyzer
    LocalPDFRepository,
    PDFDocument,
    PDFDocumentInfo,
    list_pdfs,
    extract_text,
    extract_tables,
    get_metadata,
    get_page_count,
    is_encrypted,
    search_in_pdf,
    analyze,
    SavingsAccountExtractor,
    CreditCardExtractor,
    # File Manager
    copy_pdf,
    move_pdf,
    rename_pdf,
    delete_pdf,
    get_file_info,
    PDFOrganizer,
    PDFRegistry,
    # Data Processor
    SavingsAccountProcessor,
    CreditCardProcessor,
)

# Re-export constants module for direct access
from . import constants

__all__ = [
    # Concerns
    "PathResolvableMixin",
    "PasswordAwareMixin",
    "ExceptionMapperMixin",
    "OutputDirectoryMixin",
    "BaseService",
    "ExportableService",
    "with_path_validation",
    "with_exception_mapping",
    # Constants module
    "constants",
    # Imports (most used)
    "LocalPDFRepository",
    "PDFDocument",
    "SavingsAccountExtractor",
    "CreditCardExtractor",
    "SavingsAccountProcessor",
    "CreditCardProcessor",
]
