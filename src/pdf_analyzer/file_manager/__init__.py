"""
File Manager - Gestión de archivos PDF.

Submódulo para operaciones de sistema de archivos,
organización y registro de documentos PDF.
"""

from .operations import (
    FileOperations,
    copy_pdf,
    move_pdf,
    rename_pdf,
    delete_pdf,
    create_folder,
    delete_folder,
    get_file_info,
)
from .organizer import PDFOrganizer
from .registry import PDFRegistry

__all__ = [
    # Clase principal de operaciones
    "FileOperations",
    # Funciones utilitarias
    "copy_pdf",
    "move_pdf",
    "rename_pdf",
    "delete_pdf",
    "create_folder",
    "delete_folder",
    "get_file_info",
    # Organizador
    "PDFOrganizer",
    # Registro
    "PDFRegistry",
]
