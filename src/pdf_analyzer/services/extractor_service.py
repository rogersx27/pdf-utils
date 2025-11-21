"""
Servicio de extracción de datos de PDFs.

Proporciona funciones exploratorias para analizar la estructura
y contenido de documentos PDF antes de crear extractores específicos.
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pdfplumber

from logger import setup_logger, setup_processor_logger
from pdf_analyzer.models import PDFDocument

logger = setup_processor_logger(setup_logger, __name__)


def get_default_password() -> Optional[str]:
    """Obtiene la contraseña por defecto desde variable de entorno."""
    return os.environ.get("PDF_PASSWORD")


@dataclass
class TableInfo:
    """Información de una tabla extraída con su posición."""

    page: int
    bbox: tuple  # (x0, y0, x1, y1)
    data: list[list[str]]
    rows: int = 0
    cols: int = 0

    def __post_init__(self):
        if self.data:
            self.rows = len(self.data)
            self.cols = max(len(row) for row in self.data) if self.data else 0


@dataclass
class Section:
    """Sección o bloque detectado en el documento."""

    type: str  # "header", "body", "table", "footer", "unknown"
    content: str
    page: int
    line_start: int = 0
    line_end: int = 0
    metadata: dict = field(default_factory=dict)


class ExtractorService:
    """
    Servicio para extracción exploratoria de datos de PDFs.

    Proporciona funciones "madres" para analizar la estructura
    de los documentos antes de crear extractores específicos.
    """

    def __init__(self, password: Optional[str] = None):
        """
        Inicializa el servicio de extracción.

        Args:
            password: Contraseña para PDFs protegidos.
        """
        self._password = password or get_default_password()
        logger.debug("ExtractorService inicializado")

    def extract_text_by_page(
        self, document: PDFDocument | Path | str
    ) -> dict[int, str]:
        """
        Extrae el texto raw de cada página por separado.

        Args:
            document: Documento PDF a procesar.

        Returns:
            Diccionario con número de página (0-indexed) como clave
            y el texto de esa página como valor.
        """
        path = self._resolve_path(document)
        logger.debug(f"Extrayendo texto por página de: {path.name}")

        result: dict[int, str] = {}

        with pdfplumber.open(path, password=self._password) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                result[i] = text
                logger.debug(f"Página {i}: {len(text)} caracteres")

        logger.info(f"Texto extraído de {len(result)} páginas: {path.name}")
        return result

    def extract_tables_with_position(
        self, document: PDFDocument | Path | str
    ) -> list[TableInfo]:
        """
        Extrae todas las tablas con información de posición.

        Args:
            document: Documento PDF a procesar.

        Returns:
            Lista de TableInfo con datos de cada tabla encontrada,
            incluyendo página, bounding box y contenido.
        """
        path = self._resolve_path(document)
        logger.debug(f"Extrayendo tablas con posición de: {path.name}")

        tables: list[TableInfo] = []

        with pdfplumber.open(path, password=self._password) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_tables = page.find_tables()

                for table in page_tables:
                    # Extraer datos de la tabla
                    data = table.extract() or []

                    # Limpiar datos (reemplazar None por string vacío)
                    cleaned_data = [
                        [cell if cell is not None else "" for cell in row]
                        for row in data
                    ]

                    table_info = TableInfo(
                        page=page_num,
                        bbox=table.bbox,  # (x0, y0, x1, y1)
                        data=cleaned_data,
                    )
                    tables.append(table_info)

                logger.debug(f"Página {page_num}: {len(page_tables)} tablas")

        logger.info(f"Total {len(tables)} tablas extraídas: {path.name}")
        return tables

    def extract_structure(
        self, document: PDFDocument | Path | str
    ) -> list[Section]:
        """
        Detecta y extrae la estructura/secciones del documento.

        Analiza el texto para identificar diferentes tipos de secciones:
        - header: Encabezados y títulos
        - body: Contenido principal
        - table: Áreas de tablas
        - footer: Pie de página

        Args:
            document: Documento PDF a procesar.

        Returns:
            Lista de Section con tipo, contenido y ubicación.
        """
        path = self._resolve_path(document)
        logger.debug(f"Extrayendo estructura de: {path.name}")

        sections: list[Section] = []
        text_by_page = self.extract_text_by_page(document)

        for page_num, page_text in text_by_page.items():
            if not page_text.strip():
                continue

            lines = page_text.split("\n")
            current_section_lines: list[str] = []
            current_type = "body"
            line_start = 0

            for i, line in enumerate(lines):
                line_stripped = line.strip()

                # Detectar tipo de línea
                detected_type = self._detect_line_type(line_stripped, i, len(lines))

                # Si cambia el tipo, guardar sección actual
                if detected_type != current_type and current_section_lines:
                    section = Section(
                        type=current_type,
                        content="\n".join(current_section_lines),
                        page=page_num,
                        line_start=line_start,
                        line_end=i - 1,
                    )
                    sections.append(section)
                    current_section_lines = []
                    line_start = i

                current_type = detected_type
                if line_stripped:
                    current_section_lines.append(line_stripped)

            # Guardar última sección de la página
            if current_section_lines:
                section = Section(
                    type=current_type,
                    content="\n".join(current_section_lines),
                    page=page_num,
                    line_start=line_start,
                    line_end=len(lines) - 1,
                )
                sections.append(section)

        logger.info(f"Estructura: {len(sections)} secciones detectadas: {path.name}")
        return sections

    def _detect_line_type(self, line: str, line_num: int, total_lines: int) -> str:
        """
        Detecta el tipo de una línea basado en su contenido y posición.

        Args:
            line: Contenido de la línea.
            line_num: Número de línea en la página.
            total_lines: Total de líneas en la página.

        Returns:
            Tipo detectado: "header", "body", "footer", "table", "unknown"
        """
        if not line:
            return "body"

        # Header: primeras líneas o líneas en mayúsculas
        if line_num < 5:
            if line.isupper() or len(line) < 50:
                return "header"

        # Footer: últimas líneas o patrones de pie de página
        if line_num >= total_lines - 3:
            if re.search(r"página|page|\d+\s*de\s*\d+|www\.|@", line.lower()):
                return "footer"

        # Table: líneas con muchos separadores o formato tabular
        if line.count("|") > 2 or line.count("\t") > 2:
            return "table"

        # Patrones de datos tabulares (fechas, montos)
        if re.search(r"\d{2}[/-]\d{2}[/-]\d{2,4}.*\d+[.,]\d{2}", line):
            return "table"

        return "body"

    @staticmethod
    def _resolve_path(document: PDFDocument | Path | str) -> Path:
        """Resuelve la ruta de un documento."""
        if isinstance(document, PDFDocument):
            return document.path
        return Path(document)
