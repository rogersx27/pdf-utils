"""
Módulo para lectura y extracción de contenido de archivos PDF.
"""

from pathlib import Path
from typing import Optional

import pdfplumber
from pypdf import PdfReader


def list_pdfs(directory: str | Path) -> list[Path]:
    """
    Lista todos los archivos PDF en un directorio.

    Args:
        directory: Ruta al directorio a escanear.

    Returns:
        Lista de rutas a archivos PDF encontrados.
    """
    path = Path(directory)
    return sorted(path.glob("*.pdf"))


def extract_text(pdf_path: str | Path) -> str:
    """
    Extrae todo el texto de un archivo PDF.

    Args:
        pdf_path: Ruta al archivo PDF.

    Returns:
        Texto extraído del PDF.
    """
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


class PDFReader:
    """Clase para leer y procesar archivos PDF."""

    def __init__(self, pdf_path: str | Path):
        """
        Inicializa el lector con un archivo PDF.

        Args:
            pdf_path: Ruta al archivo PDF.
        """
        self.path = Path(pdf_path)
        self._validate_path()

    def _validate_path(self) -> None:
        """Valida que el archivo exista y sea un PDF."""
        if not self.path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {self.path}")
        if self.path.suffix.lower() != ".pdf":
            raise ValueError(f"El archivo no es un PDF: {self.path}")

    @property
    def filename(self) -> str:
        """Retorna el nombre del archivo."""
        return self.path.name

    @property
    def num_pages(self) -> int:
        """Retorna el número de páginas del PDF."""
        with pdfplumber.open(self.path) as pdf:
            return len(pdf.pages)

    def get_text(self, page_number: Optional[int] = None) -> str:
        """
        Extrae texto del PDF.

        Args:
            page_number: Número de página específica (0-indexed).
                        Si es None, extrae todas las páginas.

        Returns:
            Texto extraído.
        """
        with pdfplumber.open(self.path) as pdf:
            if page_number is not None:
                if 0 <= page_number < len(pdf.pages):
                    return pdf.pages[page_number].extract_text() or ""
                raise IndexError(f"Página {page_number} fuera de rango")
            return extract_text(self.path)

    def get_tables(self, page_number: Optional[int] = None) -> list[list[list]]:
        """
        Extrae tablas del PDF.

        Args:
            page_number: Número de página específica (0-indexed).
                        Si es None, extrae de todas las páginas.

        Returns:
            Lista de tablas encontradas.
        """
        tables = []
        with pdfplumber.open(self.path) as pdf:
            pages = [pdf.pages[page_number]] if page_number is not None else pdf.pages
            for page in pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
        return tables

    def get_metadata(self) -> dict:
        """
        Obtiene los metadatos del PDF.

        Returns:
            Diccionario con metadatos del PDF.
        """
        reader = PdfReader(self.path)
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
