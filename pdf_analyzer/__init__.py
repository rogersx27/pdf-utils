"""
PDF Analyzer - Paquete para análisis de extractos bancarios en PDF.

Módulos:
    - reader: Lectura y extracción de texto de PDFs
    - analyzer: Análisis del contenido extraído
    - utils: Utilidades comunes
"""

from pdf_analyzer.reader import PDFReader, list_pdfs, extract_text
from pdf_analyzer.analyzer import PDFAnalyzer
from pdf_analyzer.utils import get_data_path

__version__ = "0.1.0"
__all__ = [
    "PDFReader",
    "PDFAnalyzer",
    "list_pdfs",
    "extract_text",
    "get_data_path",
]
