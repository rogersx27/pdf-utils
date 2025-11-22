"""
Script para agregar contraseña a PDFs.

Uso:
    python lock_pdfs.py                    # Procesa todos los PDFs en data/unlocked/
    python lock_pdfs.py archivo.pdf        # Procesa un archivo específico
    python lock_pdfs.py directorio/        # Procesa todos los PDFs en un directorio
"""

import os
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

from logger import (
    setup_logger,
    setup_cli_logger,
    log_header,
    log_success,
    log_error,
    log_info,
    log_warning,
)
from pdf_analyzer import (
    get_data_path,
    list_pdfs,
    is_encrypted,
    add_password,
    add_password_batch,
)

# Cargar variables de entorno
load_dotenv()

# Configurar logger
logger = setup_cli_logger(setup_logger, __name__)


def lock_single_file(pdf_path: Path) -> bool:
    """Agrega contraseña a un solo archivo."""
    log_info(logger, f"Procesando: {pdf_path.name}")

    if is_encrypted(pdf_path):
        log_warning(logger, f"El archivo ya está encriptado: {pdf_path.name}")
        return False

    try:
        output_path = add_password(pdf_path)
        log_success(logger, f"Guardado: {output_path.name}")
        return True
    except Exception as e:
        log_error(logger, f"Error: {e}")
        return False


def lock_all_files(input_dir: Path) -> None:
    """Agrega contraseña a todos los PDFs en un directorio."""
    pdfs = list_pdfs(input_dir)
    log_info(logger, f"PDFs encontrados: {len(pdfs)}")

    if not pdfs:
        log_warning(logger, "No se encontraron archivos PDF")
        return

    # Crear directorio de salida
    output_dir = input_dir / "locked"
    output_dir.mkdir(exist_ok=True)
    log_info(logger, f"Directorio de salida: {output_dir}")

    # Obtener contraseña del entorno
    password = os.environ.get("PDF_PASSWORD")
    if not password:
        log_error(logger, "PDF_PASSWORD no está configurada en el entorno")
        log_info(logger, "Configura la contraseña en el archivo .env")
        return

    logger.info("")

    results = add_password_batch(input_dir, output_dir, password)

    # Mostrar resumen
    logger.info("")
    logger.info("-" * 50)
    success = sum(1 for r in results if r["success"])
    failed = len(results) - success

    log_success(logger, f"Procesados exitosamente: {success}")
    if failed > 0:
        log_error(logger, f"Fallidos: {failed}")

    # Mostrar errores
    for r in results:
        if not r["success"]:
            logger.error(f"  - {r['input']}: {r['error']}")


def main():
    log_header(logger, "PDF Lock - Agregar Contraseña")

    # Verificar argumentos
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])

        if not target.exists():
            log_error(logger, f"No encontrado: {target}")
            return

        if target.is_file():
            # Procesar archivo específico
            lock_single_file(target)
        else:
            # Procesar directorio
            log_info(logger, f"Directorio: {target}")
            lock_all_files(target)
    else:
        # Procesar PDFs en data/unlocked/ por defecto
        default_dir = get_data_path() / "unlocked"

        if not default_dir.exists():
            log_warning(logger, f"Directorio no existe: {default_dir}")
            log_info(logger, "Primero ejecuta unlock_pdfs.py para crear PDFs sin contraseña")
            return

        log_info(logger, f"Directorio: {default_dir}")
        lock_all_files(default_dir)


if __name__ == "__main__":
    main()
