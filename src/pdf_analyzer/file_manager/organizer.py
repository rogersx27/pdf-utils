"""
Organizador de archivos PDF.

Proporciona funcionalidades para organizar automáticamente
los PDFs en carpetas según diferentes criterios.
"""

from pathlib import Path
from typing import Callable, Optional

from logger import setup_logger, setup_coordinator_logger

from pdf_analyzer.models import PDFDocument
from pdf_analyzer.repositories.base import BaseRepository
from .operations import create_folder, move_pdf

logger = setup_coordinator_logger(setup_logger, __name__)


class PDFOrganizer:
    """
    Organizador de documentos PDF.

    Permite organizar automáticamente los PDFs en carpetas
    según tipo, fecha, año u otros criterios personalizados.
    """

    def __init__(self, repository: BaseRepository):
        """
        Inicializa el organizador con un repositorio.

        Args:
            repository: Repositorio de PDFs a organizar.
        """
        self._repository = repository
        self._base_dir = repository.base_dir
        logger.debug(f"PDFOrganizer inicializado para: {self._base_dir}")

    def organize_by_type(
        self,
        move_files: bool = True,
        dry_run: bool = False,
    ) -> dict[str, list[Path]]:
        """
        Organiza los PDFs en carpetas por tipo de extracto.

        Crea carpetas como: CTA_AHORROS/, TARJETA_MASTERCARD/, etc.

        Args:
            move_files: Si es True, mueve los archivos. Si es False, solo copia.
            dry_run: Si es True, solo muestra qué haría sin ejecutar.

        Returns:
            Diccionario con tipo como clave y lista de archivos procesados.
        """
        logger.info("Organizando PDFs por tipo...")
        return self._organize_by_key(
            key_func=lambda doc: doc.tipo or "OTROS",
            move_files=move_files,
            dry_run=dry_run,
        )

    def organize_by_year(
        self,
        move_files: bool = True,
        dry_run: bool = False,
    ) -> dict[str, list[Path]]:
        """
        Organiza los PDFs en carpetas por año.

        Crea carpetas como: 2023/, 2024/, 2025/, etc.

        Args:
            move_files: Si es True, mueve los archivos. Si es False, solo copia.
            dry_run: Si es True, solo muestra qué haría sin ejecutar.

        Returns:
            Diccionario con año como clave y lista de archivos procesados.
        """
        logger.info("Organizando PDFs por año...")
        return self._organize_by_key(
            key_func=lambda doc: str(doc.info.year) if doc.info.year else "SIN_FECHA",
            move_files=move_files,
            dry_run=dry_run,
        )

    def organize_by_month(
        self,
        move_files: bool = True,
        dry_run: bool = False,
    ) -> dict[str, list[Path]]:
        """
        Organiza los PDFs en carpetas por año/mes.

        Crea carpetas como: 2024/01/, 2024/02/, etc.

        Args:
            move_files: Si es True, mueve los archivos. Si es False, solo copia.
            dry_run: Si es True, solo muestra qué haría sin ejecutar.

        Returns:
            Diccionario con año/mes como clave y lista de archivos procesados.
        """
        logger.info("Organizando PDFs por mes...")

        def get_year_month(doc: PDFDocument) -> str:
            if doc.info.year and doc.info.month:
                return f"{doc.info.year}/{doc.info.month:02d}"
            return "SIN_FECHA"

        return self._organize_by_key(
            key_func=get_year_month,
            move_files=move_files,
            dry_run=dry_run,
        )

    def organize_by_custom(
        self,
        key_func: Callable[[PDFDocument], str],
        move_files: bool = True,
        dry_run: bool = False,
    ) -> dict[str, list[Path]]:
        """
        Organiza los PDFs usando una función personalizada.

        Args:
            key_func: Función que recibe un PDFDocument y retorna el nombre de carpeta.
            move_files: Si es True, mueve los archivos. Si es False, solo copia.
            dry_run: Si es True, solo muestra qué haría sin ejecutar.

        Returns:
            Diccionario con carpeta como clave y lista de archivos procesados.
        """
        logger.info("Organizando PDFs con criterio personalizado...")
        return self._organize_by_key(key_func, move_files, dry_run)

    def _organize_by_key(
        self,
        key_func: Callable[[PDFDocument], str],
        move_files: bool,
        dry_run: bool,
    ) -> dict[str, list[Path]]:
        """
        Método interno para organizar por una clave.

        Args:
            key_func: Función que genera la clave/carpeta.
            move_files: Mover o copiar archivos.
            dry_run: Solo simular.

        Returns:
            Diccionario con resultados.
        """
        results: dict[str, list[Path]] = {}
        documents = self._repository.get_all()

        for doc in documents:
            folder_name = key_func(doc)

            if folder_name not in results:
                results[folder_name] = []

            dest_folder = self._base_dir / folder_name

            if dry_run:
                logger.info(f"[DRY-RUN] {doc.filename} -> {folder_name}/")
                results[folder_name].append(doc.path)
                continue

            # Crear carpeta si no existe
            create_folder(dest_folder)

            # Mover o copiar el archivo
            dest_path = dest_folder / doc.filename

            if dest_path.exists():
                logger.warning(f"Archivo ya existe en destino: {dest_path}")
                continue

            try:
                if move_files:
                    move_pdf(doc.path, dest_path)
                else:
                    from .operations import copy_pdf
                    copy_pdf(doc.path, dest_path)

                results[folder_name].append(dest_path)
            except Exception as e:
                logger.error(f"Error procesando {doc.filename}: {e}")

        # Actualizar repositorio si se movieron archivos
        if move_files and not dry_run:
            self._repository.refresh()

        # Resumen
        total = sum(len(files) for files in results.values())
        logger.info(f"Organización completada: {total} archivos en {len(results)} carpetas")

        return results

    def flatten(self, dry_run: bool = False) -> list[Path]:
        """
        Mueve todos los PDFs de subcarpetas al directorio raíz.

        Args:
            dry_run: Si es True, solo muestra qué haría.

        Returns:
            Lista de archivos movidos.
        """
        logger.info("Aplanando estructura de carpetas...")
        moved_files = []

        # Buscar PDFs en subcarpetas
        for pdf_path in self._base_dir.rglob("*.pdf"):
            if pdf_path.parent == self._base_dir:
                continue  # Ya está en el directorio raíz

            dest_path = self._base_dir / pdf_path.name

            if dry_run:
                logger.info(f"[DRY-RUN] {pdf_path} -> {dest_path}")
                moved_files.append(pdf_path)
                continue

            if dest_path.exists():
                logger.warning(f"Archivo ya existe: {dest_path.name}")
                continue

            try:
                move_pdf(pdf_path, dest_path)
                moved_files.append(dest_path)
            except Exception as e:
                logger.error(f"Error moviendo {pdf_path.name}: {e}")

        if not dry_run:
            self._repository.refresh()

        logger.info(f"Aplanado completado: {len(moved_files)} archivos movidos")
        return moved_files

    def preview_organization(
        self,
        by: str = "type",
    ) -> dict[str, list[str]]:
        """
        Previsualiza cómo quedarían organizados los archivos.

        Args:
            by: Criterio de organización ("type", "year", "month").

        Returns:
            Diccionario con la organización propuesta.
        """
        if by == "type":
            key_func = lambda doc: doc.tipo or "OTROS"
        elif by == "year":
            key_func = lambda doc: str(doc.info.year) if doc.info.year else "SIN_FECHA"
        elif by == "month":
            key_func = lambda doc: (
                f"{doc.info.year}/{doc.info.month:02d}"
                if doc.info.year and doc.info.month
                else "SIN_FECHA"
            )
        else:
            raise ValueError(f"Criterio no soportado: {by}")

        preview: dict[str, list[str]] = {}
        for doc in self._repository.get_all():
            folder = key_func(doc)
            if folder not in preview:
                preview[folder] = []
            preview[folder].append(doc.filename)

        return preview
