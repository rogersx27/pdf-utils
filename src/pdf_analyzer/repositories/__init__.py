"""
Repositorios para acceso a datos de PDFs.
"""

from .base import BaseRepository
from .pdf_repository import LocalPDFRepository

__all__ = ["BaseRepository", "LocalPDFRepository"]
