"""
Módulo para análisis de contenido extraído de PDFs.
"""

from pathlib import Path
from typing import Optional

from pdf_analyzer.reader import PDFReader


class PDFAnalyzer:
    """Clase para analizar el contenido de archivos PDF."""

    def __init__(self, pdf_path: str | Path):
        """
        Inicializa el analizador con un archivo PDF.

        Args:
            pdf_path: Ruta al archivo PDF.
        """
        self.reader = PDFReader(pdf_path)
        self._text: Optional[str] = None
        self._tables: Optional[list] = None

    @property
    def text(self) -> str:
        """Obtiene el texto del PDF (con caché)."""
        if self._text is None:
            self._text = self.reader.get_text()
        return self._text

    @property
    def tables(self) -> list:
        """Obtiene las tablas del PDF (con caché)."""
        if self._tables is None:
            self._tables = self.reader.get_tables()
        return self._tables

    def get_summary(self) -> dict:
        """
        Obtiene un resumen básico del documento.

        Returns:
            Diccionario con información resumida del PDF.
        """
        return {
            "filename": self.reader.filename,
            "num_pages": self.reader.num_pages,
            "num_tables": len(self.tables),
            "text_length": len(self.text),
            "metadata": self.reader.get_metadata(),
        }

    def search_text(self, query: str, case_sensitive: bool = False) -> list[str]:
        """
        Busca un texto en el contenido del PDF.

        Args:
            query: Texto a buscar.
            case_sensitive: Si la búsqueda debe ser sensible a mayúsculas.

        Returns:
            Lista de líneas que contienen el texto buscado.
        """
        lines = self.text.split("\n")
        if case_sensitive:
            return [line for line in lines if query in line]
        query_lower = query.lower()
        return [line for line in lines if query_lower in line.lower()]
