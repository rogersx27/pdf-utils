"""
Mixin para resolución de rutas de documentos PDF.

Permite que las clases acepten PDFDocument, Path o str como entrada
y resuelvan automáticamente la ruta del archivo.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from pdf_analyzer.models import PDFDocument


class PathResolvableMixin:
    """
    Mixin que provee resolución de rutas desde PDFDocument|Path|str.

    Uso:
        class MyService(PathResolvableMixin):
            def process(self, document: PDFDocument | Path | str):
                path = self._resolve_path(document)
                # usar path...
    """

    @staticmethod
    def _resolve_path(document: Union["PDFDocument", Path, str]) -> Path:
        """
        Resuelve la ruta de un documento.

        Args:
            document: PDFDocument, Path o string con la ruta.

        Returns:
            Path al archivo PDF.
        """
        # Import aquí para evitar circular imports
        from pdf_analyzer.models import PDFDocument

        if isinstance(document, PDFDocument):
            return document.path
        return Path(document)
