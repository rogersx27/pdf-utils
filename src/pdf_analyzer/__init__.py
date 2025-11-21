"""
PDF Analyzer - Paquete para análisis de extractos bancarios en PDF.

Módulos:
    - reader: Lectura y extracción de texto de PDFs
    - analyzer: Análisis del contenido extraído
    - utils: Utilidades comunes
"""

from .reader import PDFReader, list_pdfs, extract_text
from .analyzer import PDFAnalyzer
from .utils import get_data_path, parse_filename

__version__ = "0.2.0"
__all__ = [
    "PDFReader",
    "PDFAnalyzer",
    "list_pdfs",
    "extract_text",
    "get_data_path",
    "parse_filename",
]
