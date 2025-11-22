"""
Implementación local del repositorio de PDFs.

Gestiona documentos PDF almacenados en el sistema de archivos local.
"""

import shutil
from pathlib import Path
from typing import Optional, Callable

from logger import setup_logger, setup_processor_logger

from pdf_analyzer.models import PDFDocument
from pdf_analyzer.repositories.base import BaseRepository
from pdf_analyzer.concerns import CacheableMixin

logger = setup_processor_logger(setup_logger, __name__)


class LocalPDFRepository(BaseRepository, CacheableMixin):
    """
    Repositorio de PDFs en sistema de archivos local.

    Implementa la interfaz BaseRepository para gestionar documentos
    PDF almacenados localmente.
    """

    def __init__(self, base_dir: Path | str):
        """
        Inicializa el repositorio con un directorio base.

        Args:
            base_dir: Directorio raíz donde se almacenan los PDFs.
        """
        self._base_dir = Path(base_dir)
        self._init_cache()
        self._ensure_directory()
        self.refresh()
        logger.debug(f"LocalPDFRepository inicializado en: {self._base_dir}")

    def _ensure_directory(self) -> None:
        """Asegura que el directorio base exista."""
        if not self._base_dir.exists():
            self._base_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directorio creado: {self._base_dir}")

    @property
    def base_dir(self) -> Path:
        """Directorio base del repositorio."""
        return self._base_dir

    def get(self, identifier: str) -> Optional[PDFDocument]:
        """
        Obtiene un documento por su nombre de archivo.

        Args:
            identifier: Nombre del archivo PDF.

        Returns:
            PDFDocument si existe, None en caso contrario.
        """
        # Normalizar el identificador
        if not identifier.lower().endswith(".pdf"):
            identifier = f"{identifier}.pdf"

        doc = self._get_cached(identifier)
        if doc is None:
            logger.debug(f"Documento no encontrado en caché: {identifier}")
        return doc

    def get_all(self) -> list[PDFDocument]:
        """
        Obtiene todos los documentos del repositorio.

        Returns:
            Lista de todos los PDFDocument.
        """
        return list(self._cache.values())  # Acceso directo al dict del mixin

    def find(
        self,
        tipo: Optional[str] = None,
        fecha: Optional[str] = None,
        year: Optional[int] = None,
        predicate: Optional[Callable[[PDFDocument], bool]] = None,
    ) -> list[PDFDocument]:
        """
        Busca documentos que cumplan los criterios.

        Args:
            tipo: Filtrar por tipo de extracto.
            fecha: Filtrar por fecha exacta (YYYYMM).
            year: Filtrar por año.
            predicate: Función personalizada de filtrado.

        Returns:
            Lista de documentos que cumplen los criterios.
        """
        results = self.get_all()

        if tipo:
            results = [d for d in results if d.tipo == tipo]
            logger.debug(f"Filtrado por tipo '{tipo}': {len(results)} documentos")

        if fecha:
            results = [d for d in results if d.fecha == fecha]
            logger.debug(f"Filtrado por fecha '{fecha}': {len(results)} documentos")

        if year:
            results = [d for d in results if d.info.year == year]
            logger.debug(f"Filtrado por año {year}: {len(results)} documentos")

        if predicate:
            results = [d for d in results if predicate(d)]
            logger.debug(f"Filtrado por predicate: {len(results)} documentos")

        return results

    def exists(self, identifier: str) -> bool:
        """
        Verifica si un documento existe.

        Args:
            identifier: Nombre del archivo.

        Returns:
            True si existe.
        """
        return self.get(identifier) is not None

    def count(self) -> int:
        """
        Cuenta el total de documentos.

        Returns:
            Número de documentos.
        """
        return self.cache_size  # Usar propiedad del mixin

    def add(self, source: Path | str, dest_name: Optional[str] = None) -> PDFDocument:
        """
        Agrega un documento al repositorio (copia el archivo).

        Args:
            source: Ruta del archivo origen.
            dest_name: Nombre destino opcional.

        Returns:
            PDFDocument del archivo agregado.

        Raises:
            FileNotFoundError: Si el archivo origen no existe.
            ValueError: Si ya existe un archivo con el mismo nombre.
        """
        source = Path(source)

        if not source.exists():
            logger.error(f"Archivo origen no existe: {source}")
            raise FileNotFoundError(f"Archivo no encontrado: {source}")

        dest_name = dest_name or source.name
        if not dest_name.lower().endswith(".pdf"):
            dest_name = f"{dest_name}.pdf"

        dest_path = self._base_dir / dest_name

        if dest_path.exists():
            logger.error(f"Ya existe un archivo con ese nombre: {dest_name}")
            raise ValueError(f"El archivo ya existe: {dest_name}")

        shutil.copy2(source, dest_path)
        logger.info(f"Archivo agregado: {dest_name}")

        # Crear y cachear el documento
        doc = PDFDocument.from_path(dest_path)
        self._set_cached(dest_name, doc)

        return doc

    def remove(self, identifier: str) -> bool:
        """
        Elimina un documento del repositorio.

        Args:
            identifier: Nombre del archivo.

        Returns:
            True si se eliminó exitosamente.
        """
        doc = self.get(identifier)
        if doc is None:
            logger.warning(f"Documento no encontrado para eliminar: {identifier}")
            return False

        try:
            doc.path.unlink()
            self._remove_cached(doc.filename)
            logger.info(f"Documento eliminado: {doc.filename}")
            return True
        except Exception as e:
            logger.error(f"Error al eliminar {identifier}: {e}")
            return False

    def refresh(self) -> None:
        """
        Actualiza la caché escaneando el directorio.
        """
        self.clear_cache()
        pdf_files = sorted(self._base_dir.glob("*.pdf"))

        for pdf_path in pdf_files:
            doc = PDFDocument.from_path(pdf_path)
            self._set_cached(doc.filename, doc)

        logger.debug(f"Caché actualizada: {self.cache_size} documentos")

    def get_types(self) -> list[str]:
        """
        Obtiene todos los tipos de extracto únicos.

        Returns:
            Lista de tipos únicos.
        """
        tipos = set(doc.tipo for doc in self.get_all() if doc.tipo)
        return sorted(tipos)

    def get_years(self) -> list[int]:
        """
        Obtiene todos los años únicos.

        Returns:
            Lista de años únicos.
        """
        years = set(doc.info.year for doc in self.get_all() if doc.info.year)
        return sorted(years)

    def get_by_type(self) -> dict[str, list[PDFDocument]]:
        """
        Agrupa documentos por tipo.

        Returns:
            Diccionario con tipo como clave y lista de documentos como valor.
        """
        result: dict[str, list[PDFDocument]] = {}
        for doc in self.get_all():
            tipo = doc.tipo or "OTROS"
            if tipo not in result:
                result[tipo] = []
            result[tipo].append(doc)
        return result

    def get_by_year(self) -> dict[int, list[PDFDocument]]:
        """
        Agrupa documentos por año.

        Returns:
            Diccionario con año como clave y lista de documentos como valor.
        """
        result: dict[int, list[PDFDocument]] = {}
        for doc in self.get_all():
            year = doc.info.year or 0
            if year not in result:
                result[year] = []
            result[year].append(doc)
        return result

    def summary(self) -> dict:
        """
        Genera un resumen del repositorio.

        Returns:
            Diccionario con estadísticas.
        """
        docs = self.get_all()
        by_type = self.get_by_type()
        by_year = self.get_by_year()

        return {
            "total": len(docs),
            "by_type": {k: len(v) for k, v in by_type.items()},
            "by_year": {k: len(v) for k, v in by_year.items()},
            "types": self.get_types(),
            "years": self.get_years(),
            "total_size": sum(doc.file_size for doc in docs),
        }
