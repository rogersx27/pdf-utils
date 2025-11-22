"""
Modelos para extracción de datos de PDFs.

Define las estructuras de datos utilizadas por ExtractorService
para representar tablas y secciones de documentos.
"""

from dataclasses import dataclass, field


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
