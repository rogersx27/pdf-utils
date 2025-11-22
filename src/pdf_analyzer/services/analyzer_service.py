"""
Servicio de análisis de PDFs.

Proporciona funcionalidades para analizar el contenido
de documentos PDF.
"""

from pathlib import Path
from typing import Optional

from logger import setup_logger, setup_coordinator_logger

from pdf_analyzer.models import PDFDocument
from pdf_analyzer.services.reader_service import ReaderService
from pdf_analyzer.concerns import PathResolvableMixin, CacheableMixin

logger = setup_coordinator_logger(setup_logger, __name__)


class AnalyzerService(PathResolvableMixin, CacheableMixin):
    """
    Servicio para análisis de contenido de PDFs.

    Proporciona análisis, búsqueda y resumen de documentos PDF.
    """

    def __init__(self, password: Optional[str] = None):
        """
        Inicializa el servicio de análisis.

        Args:
            password: Contraseña para PDFs protegidos.
        """
        self._reader = ReaderService(password)
        self._init_cache()
        logger.debug("AnalyzerService inicializado")

    def analyze(self, document: PDFDocument | Path | str) -> dict:
        """
        Analiza un documento PDF y retorna un resumen completo.

        Args:
            document: Documento a analizar.

        Returns:
            Diccionario con análisis completo.
        """
        path = self._resolve_path(document)
        cache_key = str(path)

        # Verificar caché
        cached = self._get_cached(cache_key)
        if cached is not None:
            logger.debug(f"Usando caché para: {path.name}")
            return cached

        logger.info(f"Analizando: {path.name}")

        text = self._reader.read_text(path)
        tables = self._reader.read_tables(path)
        metadata = self._reader.read_metadata(path)
        num_pages = self._reader.get_page_count(path)

        analysis = {
            "filename": path.name,
            "path": str(path),
            "num_pages": num_pages,
            "text_length": len(text),
            "word_count": len(text.split()),
            "line_count": len(text.split("\n")),
            "num_tables": len(tables),
            "is_encrypted": self._reader.is_encrypted(path),
            "metadata": metadata,
        }

        # Cachear resultado
        self._set_cached(cache_key, analysis)

        logger.info(f"Análisis completado: {num_pages} páginas, {len(tables)} tablas")
        return analysis

    def get_text(self, document: PDFDocument | Path | str) -> str:
        """
        Obtiene el texto completo de un documento.

        Args:
            document: Documento a leer.

        Returns:
            Texto del documento.
        """
        return self._reader.read_text(document)

    def get_tables(self, document: PDFDocument | Path | str) -> list:
        """
        Obtiene las tablas de un documento.

        Args:
            document: Documento a leer.

        Returns:
            Lista de tablas.
        """
        return self._reader.read_tables(document)

    def search(
        self,
        document: PDFDocument | Path | str,
        query: str,
        case_sensitive: bool = False,
    ) -> list[str]:
        """
        Busca texto en un documento.

        Args:
            document: Documento donde buscar.
            query: Texto a buscar.
            case_sensitive: Si distinguir mayúsculas/minúsculas.

        Returns:
            Lista de líneas que contienen el texto.
        """
        logger.debug(f"Buscando '{query}' (case_sensitive={case_sensitive})")

        text = self._reader.read_text(document)
        lines = text.split("\n")

        if case_sensitive:
            results = [line for line in lines if query in line]
        else:
            query_lower = query.lower()
            results = [line for line in lines if query_lower in line.lower()]

        logger.info(f"Búsqueda '{query}': {len(results)} coincidencias")
        return results

    def search_all(
        self,
        documents: list[PDFDocument | Path | str],
        query: str,
        case_sensitive: bool = False,
    ) -> dict[str, list[str]]:
        """
        Busca texto en múltiples documentos.

        Args:
            documents: Lista de documentos.
            query: Texto a buscar.
            case_sensitive: Si distinguir mayúsculas/minúsculas.

        Returns:
            Diccionario con filename como clave y coincidencias como valor.
        """
        results = {}

        for doc in documents:
            path = self._resolve_path(doc)
            matches = self.search(doc, query, case_sensitive)
            if matches:
                results[path.name] = matches

        logger.info(f"Búsqueda en {len(documents)} docs: {len(results)} con coincidencias")
        return results

    def compare(
        self,
        doc1: PDFDocument | Path | str,
        doc2: PDFDocument | Path | str,
    ) -> dict:
        """
        Compara dos documentos PDF.

        Args:
            doc1: Primer documento.
            doc2: Segundo documento.

        Returns:
            Diccionario con comparación.
        """
        analysis1 = self.analyze(doc1)
        analysis2 = self.analyze(doc2)

        return {
            "doc1": analysis1["filename"],
            "doc2": analysis2["filename"],
            "comparison": {
                "pages": {
                    "doc1": analysis1["num_pages"],
                    "doc2": analysis2["num_pages"],
                    "diff": analysis1["num_pages"] - analysis2["num_pages"],
                },
                "text_length": {
                    "doc1": analysis1["text_length"],
                    "doc2": analysis2["text_length"],
                    "diff": analysis1["text_length"] - analysis2["text_length"],
                },
                "tables": {
                    "doc1": analysis1["num_tables"],
                    "doc2": analysis2["num_tables"],
                    "diff": analysis1["num_tables"] - analysis2["num_tables"],
                },
            },
        }

