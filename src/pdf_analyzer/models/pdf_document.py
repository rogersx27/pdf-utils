"""
Modelo de dominio para representar un documento PDF.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class PDFDocumentInfo:
    """Información parseada del nombre del archivo."""

    id: str
    fecha: str
    tipo: str
    numero: str
    raw: Optional[str] = None

    @classmethod
    def from_filename(cls, filename: str) -> "PDFDocumentInfo":
        """
        Parsea la información desde el nombre del archivo.

        Formato esperado: Extracto_{id}_{fecha}_{tipo}_{numero}.pdf
        Ejemplo: Extracto_455000853_202309_CTA_AHORROS_4332.pdf
        """
        name = Path(filename).stem
        parts = name.split("_")

        if len(parts) >= 4 and parts[0] == "Extracto":
            return cls(
                id=parts[1],
                fecha=parts[2],
                tipo="_".join(parts[3:-1]),
                numero=parts[-1],
            )
        return cls(id="", fecha="", tipo="", numero="", raw=name)

    @property
    def year(self) -> Optional[int]:
        """Extrae el año de la fecha (formato YYYYMM)."""
        if self.fecha and len(self.fecha) >= 4:
            try:
                return int(self.fecha[:4])
            except ValueError:
                return None
        return None

    @property
    def month(self) -> Optional[int]:
        """Extrae el mes de la fecha (formato YYYYMM)."""
        if self.fecha and len(self.fecha) >= 6:
            try:
                return int(self.fecha[4:6])
            except ValueError:
                return None
        return None


@dataclass
class PDFDocument:
    """
    Representa un documento PDF con toda su información.

    Esta es la entidad principal del dominio que encapsula
    tanto la ubicación del archivo como sus metadatos.
    """

    path: Path
    info: PDFDocumentInfo = field(default_factory=lambda: PDFDocumentInfo("", "", "", ""))
    num_pages: int = 0
    is_encrypted: bool = False
    file_size: int = 0
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Inicialización posterior para asegurar tipos correctos."""
        if isinstance(self.path, str):
            self.path = Path(self.path)

        # Parsear info del nombre si no se proporcionó
        if not self.info.id and not self.info.raw:
            self.info = PDFDocumentInfo.from_filename(self.filename)

    @classmethod
    def from_path(cls, path: Path | str) -> "PDFDocument":
        """
        Crea un PDFDocument desde una ruta de archivo.

        Args:
            path: Ruta al archivo PDF.

        Returns:
            Instancia de PDFDocument con información básica.
        """
        path = Path(path)
        info = PDFDocumentInfo.from_filename(path.name)

        doc = cls(path=path, info=info)

        # Obtener información del sistema de archivos
        if path.exists():
            stat = path.stat()
            doc.file_size = stat.st_size
            doc.created_at = datetime.fromtimestamp(stat.st_ctime)
            doc.modified_at = datetime.fromtimestamp(stat.st_mtime)

        return doc

    @property
    def filename(self) -> str:
        """Nombre del archivo."""
        return self.path.name

    @property
    def stem(self) -> str:
        """Nombre del archivo sin extensión."""
        return self.path.stem

    @property
    def exists(self) -> bool:
        """Verifica si el archivo existe."""
        return self.path.exists()

    @property
    def tipo(self) -> str:
        """Tipo de extracto (shortcut a info.tipo)."""
        return self.info.tipo

    @property
    def fecha(self) -> str:
        """Fecha del extracto (shortcut a info.fecha)."""
        return self.info.fecha

    def to_dict(self) -> dict:
        """Convierte el documento a diccionario."""
        return {
            "path": str(self.path),
            "filename": self.filename,
            "tipo": self.tipo,
            "fecha": self.fecha,
            "num_pages": self.num_pages,
            "is_encrypted": self.is_encrypted,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        return f"PDFDocument({self.filename})"

    def __repr__(self) -> str:
        return f"PDFDocument(path={self.path!r}, tipo={self.tipo!r}, fecha={self.fecha!r})"
