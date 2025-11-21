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
from .services import ReaderService, AnalyzerService, SecurityService

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

# Utils
from .utils import get_data_path, parse_filename

# =============================================================================
# COMPATIBILIDAD HACIA ATRÁS
# Estos aliases mantienen compatibilidad con el código existente
# =============================================================================

# Alias para PDFReader (ahora es ReaderService)
PDFReader = ReaderService

# Alias para PDFAnalyzer (ahora es AnalyzerService)
PDFAnalyzer = AnalyzerService

# Alias para PDFSecurity (ahora es SecurityService)
PDFSecurity = SecurityService


def list_pdfs(directory):
    """
    Lista todos los PDFs en un directorio.

    Función de compatibilidad - usa LocalPDFRepository internamente.
    """
    from pathlib import Path
    return sorted(Path(directory).glob("*.pdf"))


def extract_text(pdf_path, password=None):
    """
    Extrae texto de un PDF.

    Función de compatibilidad - usa ReaderService internamente.
    """
    reader = ReaderService(password)
    return reader.read_text(pdf_path)


def is_encrypted(pdf_path):
    """
    Verifica si un PDF está encriptado.

    Función de compatibilidad - usa SecurityService internamente.
    """
    security = SecurityService()
    return security.is_encrypted(pdf_path)


def remove_password(pdf_path, output_path=None, password=None):
    """
    Quita contraseña de un PDF.

    Función de compatibilidad - usa SecurityService internamente.
    """
    security = SecurityService(password)
    return security.remove_password(pdf_path, output_path)


def add_password(pdf_path, output_path=None, user_password=None, owner_password=None):
    """
    Agrega contraseña a un PDF.

    Función de compatibilidad - usa SecurityService internamente.
    """
    security = SecurityService()
    return security.add_password(pdf_path, output_path, user_password, owner_password)


def remove_password_batch(input_dir, output_dir=None, password=None):
    """
    Quita contraseña de múltiples PDFs.

    Función de compatibilidad.
    """
    from pathlib import Path
    docs = list(Path(input_dir).glob("*.pdf"))
    security = SecurityService(password)
    return security.batch_remove_password(docs, output_dir)


def add_password_batch(input_dir, output_dir=None, user_password=None, owner_password=None):
    """
    Agrega contraseña a múltiples PDFs.

    Función de compatibilidad.
    """
    from pathlib import Path
    results = []
    docs = list(Path(input_dir).glob("*.pdf"))
    security = SecurityService()

    for doc in docs:
        try:
            if output_dir:
                out = Path(output_dir) / doc.name
            else:
                out = None
            result = security.add_password(doc, out, user_password, owner_password)
            results.append({"input": doc.name, "success": True, "output": str(result)})
        except Exception as e:
            results.append({"input": doc.name, "success": False, "error": str(e)})

    return results


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
    "parse_filename",
    # Compatibilidad hacia atrás
    "PDFReader",
    "PDFAnalyzer",
    "PDFSecurity",
    "list_pdfs",
    "extract_text",
    "is_encrypted",
    "remove_password",
    "add_password",
    "remove_password_batch",
    "add_password_batch",
]
