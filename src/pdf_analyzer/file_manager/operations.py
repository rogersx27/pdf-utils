"""
Operaciones de sistema de archivos para PDFs.

Proporciona funciones atómicas para manipular archivos y directorios.
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from logger import setup_logger, setup_processor_logger

logger = setup_processor_logger(setup_logger, __name__)


class FileOperationError(Exception):
    """Excepción para errores en operaciones de archivo."""

    pass


def get_file_info(path: Path | str) -> dict:
    """
    Obtiene información detallada de un archivo.

    Args:
        path: Ruta al archivo.

    Returns:
        Diccionario con información del archivo.

    Raises:
        FileNotFoundError: Si el archivo no existe.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")

    stat = path.stat()

    return {
        "name": path.name,
        "stem": path.stem,
        "suffix": path.suffix,
        "path": str(path.absolute()),
        "parent": str(path.parent),
        "size": stat.st_size,
        "size_human": _format_size(stat.st_size),
        "created": datetime.fromtimestamp(stat.st_ctime),
        "modified": datetime.fromtimestamp(stat.st_mtime),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
    }


def _format_size(size: int) -> str:
    """Formatea un tamaño en bytes a formato legible."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def copy_pdf(
    source: Path | str,
    dest: Path | str,
    overwrite: bool = False,
) -> Path:
    """
    Copia un archivo PDF a un destino.

    Args:
        source: Ruta del archivo origen.
        dest: Ruta o directorio destino.
        overwrite: Si es True, sobrescribe archivos existentes.

    Returns:
        Ruta del archivo copiado.

    Raises:
        FileNotFoundError: Si el origen no existe.
        FileOperationError: Si el destino ya existe y overwrite=False.
    """
    source = Path(source)
    dest = Path(dest)

    if not source.exists():
        logger.error(f"Archivo origen no existe: {source}")
        raise FileNotFoundError(f"Archivo no encontrado: {source}")

    # Si dest es un directorio, mantener el nombre original
    if dest.is_dir():
        dest = dest / source.name

    if dest.exists() and not overwrite:
        logger.error(f"Archivo destino ya existe: {dest}")
        raise FileOperationError(f"El archivo ya existe: {dest}")

    # Asegurar que el directorio destino existe
    dest.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(source, dest)
    logger.info(f"Copiado: {source.name} -> {dest}")

    return dest


def move_pdf(
    source: Path | str,
    dest: Path | str,
    overwrite: bool = False,
) -> Path:
    """
    Mueve un archivo PDF a un destino.

    Args:
        source: Ruta del archivo origen.
        dest: Ruta o directorio destino.
        overwrite: Si es True, sobrescribe archivos existentes.

    Returns:
        Ruta del archivo movido.

    Raises:
        FileNotFoundError: Si el origen no existe.
        FileOperationError: Si el destino ya existe y overwrite=False.
    """
    source = Path(source)
    dest = Path(dest)

    if not source.exists():
        logger.error(f"Archivo origen no existe: {source}")
        raise FileNotFoundError(f"Archivo no encontrado: {source}")

    # Si dest es un directorio, mantener el nombre original
    if dest.is_dir():
        dest = dest / source.name

    if dest.exists() and not overwrite:
        logger.error(f"Archivo destino ya existe: {dest}")
        raise FileOperationError(f"El archivo ya existe: {dest}")

    # Asegurar que el directorio destino existe
    dest.parent.mkdir(parents=True, exist_ok=True)

    shutil.move(str(source), str(dest))
    logger.info(f"Movido: {source.name} -> {dest}")

    return dest


def rename_pdf(
    source: Path | str,
    new_name: str,
) -> Path:
    """
    Renombra un archivo PDF.

    Args:
        source: Ruta del archivo a renombrar.
        new_name: Nuevo nombre (con o sin extensión .pdf).

    Returns:
        Ruta del archivo renombrado.

    Raises:
        FileNotFoundError: Si el origen no existe.
        FileOperationError: Si ya existe un archivo con el nuevo nombre.
    """
    source = Path(source)

    if not source.exists():
        logger.error(f"Archivo no existe: {source}")
        raise FileNotFoundError(f"Archivo no encontrado: {source}")

    # Asegurar extensión .pdf
    if not new_name.lower().endswith(".pdf"):
        new_name = f"{new_name}.pdf"

    dest = source.parent / new_name

    if dest.exists():
        logger.error(f"Ya existe un archivo con ese nombre: {new_name}")
        raise FileOperationError(f"El archivo ya existe: {new_name}")

    source.rename(dest)
    logger.info(f"Renombrado: {source.name} -> {new_name}")

    return dest


def delete_pdf(path: Path | str) -> bool:
    """
    Elimina un archivo PDF.

    Args:
        path: Ruta del archivo a eliminar.

    Returns:
        True si se eliminó exitosamente.

    Raises:
        FileNotFoundError: Si el archivo no existe.
    """
    path = Path(path)

    if not path.exists():
        logger.warning(f"Archivo no existe: {path}")
        raise FileNotFoundError(f"Archivo no encontrado: {path}")

    path.unlink()
    logger.info(f"Eliminado: {path.name}")

    return True


def create_folder(path: Path | str) -> Path:
    """
    Crea un directorio (y padres si es necesario).

    Args:
        path: Ruta del directorio a crear.

    Returns:
        Ruta del directorio creado.
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

    if path.exists():
        logger.debug(f"Directorio creado/existente: {path}")
    else:
        logger.info(f"Directorio creado: {path}")

    return path


def delete_folder(path: Path | str, force: bool = False) -> bool:
    """
    Elimina un directorio.

    Args:
        path: Ruta del directorio a eliminar.
        force: Si es True, elimina aunque contenga archivos.

    Returns:
        True si se eliminó exitosamente.

    Raises:
        FileNotFoundError: Si el directorio no existe.
        FileOperationError: Si el directorio no está vacío y force=False.
    """
    path = Path(path)

    if not path.exists():
        logger.warning(f"Directorio no existe: {path}")
        raise FileNotFoundError(f"Directorio no encontrado: {path}")

    if not path.is_dir():
        raise FileOperationError(f"No es un directorio: {path}")

    # Verificar si está vacío
    contents = list(path.iterdir())
    if contents and not force:
        raise FileOperationError(
            f"El directorio no está vacío ({len(contents)} elementos). "
            "Usa force=True para eliminar de todos modos."
        )

    if force:
        shutil.rmtree(path)
    else:
        path.rmdir()

    logger.info(f"Directorio eliminado: {path}")
    return True


class FileOperations:
    """
    Clase para gestionar operaciones de archivos en un directorio base.

    Proporciona una interfaz orientada a objetos para las operaciones
    de archivos, manteniendo un contexto de directorio base.
    """

    def __init__(self, base_dir: Path | str):
        """
        Inicializa el gestor de operaciones.

        Args:
            base_dir: Directorio base para las operaciones.
        """
        self._base_dir = Path(base_dir)
        self._ensure_base_dir()
        logger.debug(f"FileOperations inicializado en: {self._base_dir}")

    def _ensure_base_dir(self) -> None:
        """Asegura que el directorio base exista."""
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, path: Path | str) -> Path:
        """Resuelve una ruta relativa al directorio base."""
        path = Path(path)
        if not path.is_absolute():
            path = self._base_dir / path
        return path

    @property
    def base_dir(self) -> Path:
        """Directorio base."""
        return self._base_dir

    def copy(self, source: str, dest: str, overwrite: bool = False) -> Path:
        """Copia un archivo."""
        src = self._resolve_path(source)
        dst = self._resolve_path(dest)
        return copy_pdf(src, dst, overwrite)

    def move(self, source: str, dest: str, overwrite: bool = False) -> Path:
        """Mueve un archivo."""
        src = self._resolve_path(source)
        dst = self._resolve_path(dest)
        return move_pdf(src, dst, overwrite)

    def rename(self, source: str, new_name: str) -> Path:
        """Renombra un archivo."""
        src = self._resolve_path(source)
        return rename_pdf(src, new_name)

    def delete(self, path: str) -> bool:
        """Elimina un archivo."""
        return delete_pdf(self._resolve_path(path))

    def create_folder(self, name: str) -> Path:
        """Crea una carpeta."""
        return create_folder(self._base_dir / name)

    def delete_folder(self, name: str, force: bool = False) -> bool:
        """Elimina una carpeta."""
        return delete_folder(self._base_dir / name, force)

    def list_folders(self) -> list[Path]:
        """Lista todas las carpetas en el directorio base."""
        return sorted([p for p in self._base_dir.iterdir() if p.is_dir()])

    def list_files(self, pattern: str = "*.pdf") -> list[Path]:
        """Lista archivos que coinciden con un patrón."""
        return sorted(self._base_dir.glob(pattern))

    def get_info(self, path: str) -> dict:
        """Obtiene información de un archivo."""
        return get_file_info(self._resolve_path(path))
