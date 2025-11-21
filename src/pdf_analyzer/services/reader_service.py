"""
Servicio de lectura de PDFs.

Proporciona funcionalidades para extraer texto, tablas y
metadatos de documentos PDF.
"""

import os
from pathlib import Path
from typing import Optional

import pdfplumber
from pypdf import PdfReader

from logger import setup_logger, setup_processor_logger

from pdf_analyzer.models import PDFDocument

logger = setup_processor_logger(setup_logger, __name__)


def get_default_password() -> Optional[str]:
    """Obtiene la contraseña por defecto desde variable de entorno."""
    return os.environ.get("PDF_PASSWORD")


class ReaderService:
    """
    Servicio para lectura y extracción de contenido de PDFs.

    Encapsula las operaciones de lectura de texto, tablas y
    metadatos de documentos PDF.
    """

    def __init__(self, password: Optional[str] = None):
        """
        Inicializa el servicio de lectura.

        Args:
            password: Contraseña para PDFs protegidos.
                     Usa PDF_PASSWORD del entorno si no se especifica.
        """
        self._password = password or get_default_password()
        logger.debug("ReaderService inicializado")

    def _open_pdf(self, path: Path):
        """Abre un PDF con contraseña si es necesario."""
        return pdfplumber.open(path, password=self._password)

    def read_text(
        self,
        document: PDFDocument | Path | str,
        page_number: Optional[int] = None,
    ) -> str:
        """
        Extrae texto de un documento PDF.

        Args:
            document: PDFDocument, Path o ruta al PDF.
            page_number: Número de página específica (0-indexed).
                        Si es None, extrae todas las páginas.

        Returns:
            Texto extraído del PDF.
        """
        path = self._resolve_path(document)
        logger.debug(f"Extrayendo texto de: {path.name}")

        text_parts = []
        with self._open_pdf(path) as pdf:
            if page_number is not None:
                if 0 <= page_number < len(pdf.pages):
                    page_text = pdf.pages[page_number].extract_text() or ""
                    logger.debug(f"Página {page_number}: {len(page_text)} caracteres")
                    return page_text
                raise IndexError(f"Página {page_number} fuera de rango (0-{len(pdf.pages)-1})")

            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                    logger.debug(f"Página {i+1}: {len(page_text)} caracteres")

        total_text = "\n".join(text_parts)
        logger.debug(f"Total: {len(total_text)} caracteres de {len(text_parts)} páginas")
        return total_text

    def read_tables(
        self,
        document: PDFDocument | Path | str,
        page_number: Optional[int] = None,
    ) -> list[list[list]]:
        """
        Extrae tablas de un documento PDF.

        Args:
            document: PDFDocument, Path o ruta al PDF.
            page_number: Número de página específica (0-indexed).
                        Si es None, extrae de todas las páginas.

        Returns:
            Lista de tablas encontradas.
        """
        path = self._resolve_path(document)
        logger.debug(f"Extrayendo tablas de: {path.name}")

        tables = []
        with self._open_pdf(path) as pdf:
            pages = [pdf.pages[page_number]] if page_number is not None else pdf.pages

            for i, page in enumerate(pages):
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
                    logger.debug(f"Página {i}: {len(page_tables)} tablas")

        logger.debug(f"Total: {len(tables)} tablas extraídas")
        return tables

    def read_metadata(self, document: PDFDocument | Path | str) -> dict:
        """
        Obtiene los metadatos de un PDF.

        Args:
            document: PDFDocument, Path o ruta al PDF.

        Returns:
            Diccionario con metadatos.
        """
        path = self._resolve_path(document)
        logger.debug(f"Obteniendo metadatos de: {path.name}")

        reader = PdfReader(path)
        if reader.is_encrypted:
            logger.debug("PDF encriptado, desencriptando...")
            reader.decrypt(self._password or "")

        metadata = reader.metadata
        if metadata:
            return {
                "author": metadata.author,
                "creator": metadata.creator,
                "producer": metadata.producer,
                "subject": metadata.subject,
                "title": metadata.title,
            }
        return {}

    def get_page_count(self, document: PDFDocument | Path | str) -> int:
        """
        Obtiene el número de páginas de un PDF.

        Args:
            document: PDFDocument, Path o ruta al PDF.

        Returns:
            Número de páginas.
        """
        path = self._resolve_path(document)
        with self._open_pdf(path) as pdf:
            return len(pdf.pages)

    def is_encrypted(self, document: PDFDocument | Path | str) -> bool:
        """
        Verifica si un PDF está encriptado.

        Args:
            document: PDFDocument, Path o ruta al PDF.

        Returns:
            True si está encriptado.
        """
        path = self._resolve_path(document)
        reader = PdfReader(path)
        return reader.is_encrypted

    def enrich_document(self, document: PDFDocument) -> PDFDocument:
        """
        Enriquece un PDFDocument con información adicional.

        Lee el PDF y actualiza num_pages, is_encrypted y metadata.

        Args:
            document: PDFDocument a enriquecer.

        Returns:
            El mismo documento con información actualizada.
        """
        document.num_pages = self.get_page_count(document)
        document.is_encrypted = self.is_encrypted(document)
        document.metadata = self.read_metadata(document)
        return document

    @staticmethod
    def _resolve_path(document: PDFDocument | Path | str) -> Path:
        """Resuelve la ruta de un documento."""
        if isinstance(document, PDFDocument):
            return document.path
        return Path(document)
