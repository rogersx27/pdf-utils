"""
PDF Analyzer - Paquete para análisis de extractos bancarios en PDF.

Arquitectura basada en el patrón Repository con las siguientes capas:
    - models: Entidades de dominio (PDFDocument)
    - repositories: Acceso a datos (LocalPDFRepository)
    - services: Lógica de negocio (Reader, Analyzer, Security)
    - file_manager: Operaciones de archivos (Operations, Organizer, Registry)

Uso básico:
    from pdf_analyzer import LocalPDFRepository, AnalyzerService

    repo = LocalPDFRepository("data/")
    docs = repo.get_all()

    analyzer = AnalyzerService()
    result = analyzer.analyze(docs[0])
"""

# Models
from .models import PDFDocument, PDFDocumentInfo

# Repositories
from .repositories import BaseRepository, LocalPDFRepository

# Services
from .services import (
    ReaderService,
    AnalyzerService,
    SecurityService,
    ExtractorService,
    TableInfo,
    Section,
    # Savings Account Extractor
    SavingsAccountExtractor,
    SavingsAccountStatement,
    AccountInfo,
    FinancialSummary,
    Transaction,
    # Credit Card Extractor
    CreditCardExtractor,
    CreditCardStatement,
    CreditCardTransaction,
    CardInfo,
    CreditLimit,
    InterestRates,
    BalanceSummary,
    MinimumPayment,
    CurrencyStatement,
)

# File Manager
from .file_manager import (
    FileOperations,
    PDFOrganizer,
    PDFRegistry,
    copy_pdf,
    move_pdf,
    rename_pdf,
    delete_pdf,
    create_folder,
    delete_folder,
    get_file_info,
)

# Utils - Funciones de utilidad y conveniencia
from .utils import (
    # Utilidades generales
    get_data_path,
    parse_filename,
    ensure_directory,
    get_project_root,
    # Funciones de conveniencia para PDFs
    list_pdfs,
    extract_text,
    extract_tables,
    get_metadata,
    get_page_count,
    is_encrypted,
    remove_password,
    add_password,
    remove_password_batch,
    add_password_batch,
    analyze,
    search_in_pdf,
    compare_pdfs,
)

# =============================================================================
# ALIASES DE COMPATIBILIDAD
# =============================================================================

PDFReader = ReaderService
PDFAnalyzer = AnalyzerService
PDFSecurity = SecurityService
PDFExtractor = ExtractorService


__version__ = "1.0.0"

__all__ = [
    # Models
    "PDFDocument",
    "PDFDocumentInfo",
    # Repositories
    "BaseRepository",
    "LocalPDFRepository",
    # Services
    "ReaderService",
    "AnalyzerService",
    "SecurityService",
    "ExtractorService",
    "TableInfo",
    "Section",
    # Savings Account Extractor
    "SavingsAccountExtractor",
    "SavingsAccountStatement",
    "AccountInfo",
    "FinancialSummary",
    "Transaction",
    # Credit Card Extractor
    "CreditCardExtractor",
    "CreditCardStatement",
    "CreditCardTransaction",
    "CardInfo",
    "CreditLimit",
    "InterestRates",
    "BalanceSummary",
    "MinimumPayment",
    "CurrencyStatement",
    # File Manager
    "FileOperations",
    "PDFOrganizer",
    "PDFRegistry",
    "copy_pdf",
    "move_pdf",
    "rename_pdf",
    "delete_pdf",
    "create_folder",
    "delete_folder",
    "get_file_info",
    # Utils
    "get_data_path",
    "get_project_root",
    "ensure_directory",
    "parse_filename",
    # Funciones de conveniencia
    "list_pdfs",
    "extract_text",
    "extract_tables",
    "get_metadata",
    "get_page_count",
    "is_encrypted",
    "remove_password",
    "add_password",
    "remove_password_batch",
    "add_password_batch",
    "analyze",
    "search_in_pdf",
    "compare_pdfs",
    # Aliases de compatibilidad
    "PDFReader",
    "PDFAnalyzer",
    "PDFSecurity",
    "PDFExtractor",
]
