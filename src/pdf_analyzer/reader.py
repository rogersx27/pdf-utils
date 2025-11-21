"""
Módulo para lectura y extracción de contenido de archivos PDF.
"""

import os
from pathlib import Path
from typing import Optional

import pdfplumber
from pypdf import PdfReader

from logger import setup_logger, setup_processor_logger

# Configurar logger como procesador (sin consola, solo archivo)
logger = setup_processor_logger(setup_logger, __name__)


def get_default_password() -> Optional[str]:
    """
    Obtiene la contraseña por defecto desde variable de entorno.

    Returns:
        Contraseña o None si no está configurada.
    """
    return os.environ.get("PDF_PASSWORD")


def list_pdfs(directory: str | Path) -> list[Path]:
    """
    Lista todos los archivos PDF en un directorio.

    Args:
        directory: Ruta al directorio a escanear.

    Returns:
        Lista de rutas a archivos PDF encontrados.
    """
    path = Path(directory)
    pdfs = sorted(path.glob("*.pdf"))
    logger.debug(f"Encontrados {len(pdfs)} PDFs en {directory}")
    return pdfs


def extract_text(pdf_path: str | Path, password: Optional[str] = None) -> str:
    """
    Extrae todo el texto de un archivo PDF.

    Args:
        pdf_path: Ruta al archivo PDF.
        password: Contraseña del PDF (usa variable de entorno si no se proporciona).

    Returns:
        Texto extraído del PDF.
    """
    pwd = password or get_default_password()
    logger.debug(f"Extrayendo texto de: {pdf_path}")
    text_parts = []
    with pdfplumber.open(pdf_path, password=pwd) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
                logger.debug(f"Página {i+1}: {len(page_text)} caracteres extraídos")
    total_text = "\n".join(text_parts)
    logger.debug(f"Total extraído: {len(total_text)} caracteres de {len(text_parts)} páginas")
    return total_text


class PDFReader:
    """Clase para leer y procesar archivos PDF."""

    def __init__(self, pdf_path: str | Path, password: Optional[str] = None):
        """
        Inicializa el lector con un archivo PDF.

        Args:
            pdf_path: Ruta al archivo PDF.
            password: Contraseña del PDF (usa variable de entorno si no se proporciona).
        """
        self.path = Path(pdf_path)
        self.password = password or get_default_password()
        self._validate_path()
        logger.debug(f"PDFReader inicializado para: {self.path.name}")

    def _validate_path(self) -> None:
        """Valida que el archivo exista y sea un PDF."""
        if not self.path.exists():
            logger.error(f"Archivo no encontrado: {self.path}")
            raise FileNotFoundError(f"Archivo no encontrado: {self.path}")
        if self.path.suffix.lower() != ".pdf":
            logger.error(f"El archivo no es un PDF: {self.path}")
            raise ValueError(f"El archivo no es un PDF: {self.path}")

    def _open_pdf(self):
        """Abre el PDF con contraseña si es necesario."""
        return pdfplumber.open(self.path, password=self.password)

    @property
    def filename(self) -> str:
        """Retorna el nombre del archivo."""
        return self.path.name

    @property
    def num_pages(self) -> int:
        """Retorna el número de páginas del PDF."""
        with self._open_pdf() as pdf:
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
        logger.debug(f"Extrayendo texto de {self.filename}, página: {page_number or 'todas'}")
        with self._open_pdf() as pdf:
            if page_number is not None:
                if 0 <= page_number < len(pdf.pages):
                    text = pdf.pages[page_number].extract_text() or ""
                    logger.debug(f"Página {page_number}: {len(text)} caracteres")
                    return text
                logger.error(f"Página {page_number} fuera de rango (0-{len(pdf.pages)-1})")
                raise IndexError(f"Página {page_number} fuera de rango")
            return extract_text(self.path, self.password)

    def get_tables(self, page_number: Optional[int] = None) -> list[list[list]]:
        """
        Extrae tablas del PDF.

        Args:
            page_number: Número de página específica (0-indexed).
                        Si es None, extrae de todas las páginas.

        Returns:
            Lista de tablas encontradas.
        """
        logger.debug(f"Extrayendo tablas de {self.filename}, página: {page_number or 'todas'}")
        tables = []
        with self._open_pdf() as pdf:
            pages = [pdf.pages[page_number]] if page_number is not None else pdf.pages
            for i, page in enumerate(pages):
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
                    logger.debug(f"Página {i}: {len(page_tables)} tablas encontradas")
        logger.debug(f"Total: {len(tables)} tablas extraídas")
        return tables

    def get_metadata(self) -> dict:
        """
        Obtiene los metadatos del PDF.

        Returns:
            Diccionario con metadatos del PDF.
        """
        logger.debug(f"Obteniendo metadatos de {self.filename}")
        reader = PdfReader(self.path)
        if reader.is_encrypted:
            logger.debug("PDF encriptado, desencriptando...")
            reader.decrypt(self.password or "")
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
