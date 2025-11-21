"""
Clase base abstracta para repositorios de PDFs.

Define la interfaz que deben implementar todos los repositorios,
permitiendo intercambiar implementaciones (local, cloud, etc.) sin
modificar el código que las usa.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Callable

from pdf_analyzer.models import PDFDocument


class BaseRepository(ABC):
    """
    Interfaz abstracta para repositorios de documentos PDF.

    Define las operaciones CRUD y de búsqueda que todo repositorio
    debe implementar.
    """

    @abstractmethod
    def get(self, identifier: str) -> Optional[PDFDocument]:
        """
        Obtiene un documento por su identificador (nombre de archivo).

        Args:
            identifier: Nombre del archivo o identificador único.

        Returns:
            PDFDocument si existe, None en caso contrario.
        """
        pass

    @abstractmethod
    def get_all(self) -> list[PDFDocument]:
        """
        Obtiene todos los documentos del repositorio.

        Returns:
            Lista de todos los PDFDocument disponibles.
        """
        pass

    @abstractmethod
    def find(
        self,
        tipo: Optional[str] = None,
        fecha: Optional[str] = None,
        year: Optional[int] = None,
        predicate: Optional[Callable[[PDFDocument], bool]] = None,
    ) -> list[PDFDocument]:
        """
        Busca documentos que cumplan los criterios especificados.

        Args:
            tipo: Filtrar por tipo de extracto (CTA_AHORROS, TARJETA_MASTERCARD, etc.)
            fecha: Filtrar por fecha exacta (formato YYYYMM).
            year: Filtrar por año.
            predicate: Función personalizada de filtrado.

        Returns:
            Lista de documentos que cumplen los criterios.
        """
        pass

    @abstractmethod
    def exists(self, identifier: str) -> bool:
        """
        Verifica si un documento existe en el repositorio.

        Args:
            identifier: Nombre del archivo o identificador.

        Returns:
            True si existe, False en caso contrario.
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Cuenta el total de documentos en el repositorio.

        Returns:
            Número total de documentos.
        """
        pass

    @abstractmethod
    def add(self, source: Path, dest_name: Optional[str] = None) -> PDFDocument:
        """
        Agrega un nuevo documento al repositorio.

        Args:
            source: Ruta del archivo a agregar.
            dest_name: Nombre destino opcional (usa el original si no se especifica).

        Returns:
            PDFDocument del archivo agregado.
        """
        pass

    @abstractmethod
    def remove(self, identifier: str) -> bool:
        """
        Elimina un documento del repositorio.

        Args:
            identifier: Nombre del archivo o identificador.

        Returns:
            True si se eliminó exitosamente, False en caso contrario.
        """
        pass

    @abstractmethod
    def refresh(self) -> None:
        """
        Actualiza la caché interna del repositorio.

        Útil cuando los archivos pueden haber cambiado externamente.
        """
        pass
