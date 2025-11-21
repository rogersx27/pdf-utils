"""
Utilidades comunes para el paquete pdf_analyzer.
"""

from pathlib import Path

from logger import setup_logger, setup_utils_logger

# Configurar logger como utilidad (solo WARNING+, sin consola)
logger = setup_utils_logger(setup_logger, __name__)


def get_project_root() -> Path:
    """
    Obtiene la ruta raíz del proyecto.

    Returns:
        Ruta al directorio raíz del proyecto.
    """
    return Path(__file__).parent.parent.parent


def get_data_path() -> Path:
    """
    Obtiene la ruta a la carpeta de datos.

    Returns:
        Ruta al directorio 'data'.
    """
    data_path = get_project_root() / "data"
    if not data_path.exists():
        logger.warning(f"Carpeta de datos no existe: {data_path}")
    return data_path


def ensure_directory(path: str | Path) -> Path:
    """
    Asegura que un directorio exista, creándolo si es necesario.

    Args:
        path: Ruta al directorio.

    Returns:
        Objeto Path del directorio.
    """
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directorio creado: {path}")
    return path


def parse_filename(filename: str) -> dict:
    """
    Parsea el nombre de archivo de un extracto bancario.

    Formato esperado: Extracto_{id}_{fecha}_{tipo}_{numero}.pdf
    Ejemplo: Extracto_455000853_202309_CTA_AHORROS_4332.pdf

    Args:
        filename: Nombre del archivo PDF.

    Returns:
        Diccionario con los componentes del nombre.
    """
    name = Path(filename).stem
    parts = name.split("_")

    if len(parts) >= 4 and parts[0] == "Extracto":
        return {
            "id": parts[1],
            "fecha": parts[2],
            "tipo": "_".join(parts[3:-1]),
            "numero": parts[-1],
        }
    logger.warning(f"Formato de nombre no reconocido: {filename}")
    return {"raw": name}
