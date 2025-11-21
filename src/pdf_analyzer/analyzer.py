"""
Módulo para análisis de contenido extraído de PDFs.
"""

from pathlib import Path
from typing import Optional

from pdf_analyzer.reader import PDFReader
from logger import setup_logger, setup_coordinator_logger

# Configurar logger como coordinador (con consola y archivo)
logger = setup_coordinator_logger(setup_logger, __name__)


class PDFAnalyzer:
    """Clase para analizar el contenido de archivos PDF."""

    def __init__(self, pdf_path: str | Path, password: Optional[str] = None):
        """
        Inicializa el analizador con un archivo PDF.

        Args:
            pdf_path: Ruta al archivo PDF.
            password: Contraseña del PDF (usa variable de entorno si no se proporciona).
        """
        logger.info(f"Iniciando análisis de: {Path(pdf_path).name}")
        self.reader = PDFReader(pdf_path, password=password)
        self._text: Optional[str] = None
        self._tables: Optional[list] = None

    @property
    def text(self) -> str:
        """Obtiene el texto del PDF (con caché)."""
        if self._text is None:
            logger.debug("Extrayendo texto (primera vez)...")
            self._text = self.reader.get_text()
            logger.debug(f"Texto cacheado: {len(self._text)} caracteres")
        return self._text

    @property
    def tables(self) -> list:
        """Obtiene las tablas del PDF (con caché)."""
        if self._tables is None:
            logger.debug("Extrayendo tablas (primera vez)...")
            self._tables = self.reader.get_tables()
            logger.debug(f"Tablas cacheadas: {len(self._tables)} tablas")
        return self._tables

    def get_summary(self) -> dict:
        """
        Obtiene un resumen básico del documento.

        Returns:
            Diccionario con información resumida del PDF.
        """
        logger.info(f"Generando resumen de: {self.reader.filename}")
        summary = {
            "filename": self.reader.filename,
            "num_pages": self.reader.num_pages,
            "num_tables": len(self.tables),
            "text_length": len(self.text),
            "metadata": self.reader.get_metadata(),
        }
        logger.info(f"Resumen: {summary['num_pages']} páginas, {summary['num_tables']} tablas")
        return summary

    def search_text(self, query: str, case_sensitive: bool = False) -> list[str]:
        """
        Busca un texto en el contenido del PDF.

        Args:
            query: Texto a buscar.
            case_sensitive: Si la búsqueda debe ser sensible a mayúsculas.

        Returns:
            Lista de líneas que contienen el texto buscado.
        """
        logger.debug(f"Buscando '{query}' (case_sensitive={case_sensitive})")
        lines = self.text.split("\n")
        if case_sensitive:
            results = [line for line in lines if query in line]
        else:
            query_lower = query.lower()
            results = [line for line in lines if query_lower in line.lower()]
        logger.info(f"Búsqueda '{query}': {len(results)} coincidencias encontradas")
        return results
