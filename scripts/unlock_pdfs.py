"""
Script para quitar contraseña de los PDFs protegidos.

Uso:
    python unlock_pdfs.py              # Procesa todos los PDFs en data/
    python unlock_pdfs.py archivo.pdf  # Procesa un archivo específico
"""

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
    remove_password,
    remove_password_batch,
)

# Cargar variables de entorno
load_dotenv()

# Configurar logger
logger = setup_cli_logger(setup_logger, __name__)


def unlock_single_file(pdf_path: Path) -> bool:
    """Quita la contraseña de un solo archivo."""
    log_info(logger, f"Procesando: {pdf_path.name}")

    if not is_encrypted(pdf_path):
        log_warning(logger, f"El archivo no está encriptado: {pdf_path.name}")
        return False

    try:
        output_path = remove_password(pdf_path)
        log_success(logger, f"Guardado: {output_path.name}")
        return True
    except Exception as e:
        log_error(logger, f"Error: {e}")
        return False


def unlock_all_files(data_dir: Path) -> None:
    """Quita la contraseña de todos los PDFs en un directorio."""
    pdfs = list_pdfs(data_dir)
    log_info(logger, f"PDFs encontrados: {len(pdfs)}")

    if not pdfs:
        log_warning(logger, "No se encontraron archivos PDF")
        return

    # Crear directorio de salida
    output_dir = data_dir / "unlocked"
    output_dir.mkdir(exist_ok=True)
    log_info(logger, f"Directorio de salida: {output_dir}")

    logger.info("")

    results = remove_password_batch(data_dir, output_dir)

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
    log_header(logger, "PDF Unlock - Quitar Contraseña")

    # Verificar argumentos
    if len(sys.argv) > 1:
        # Procesar archivo específico
        pdf_path = Path(sys.argv[1])
        if not pdf_path.exists():
            log_error(logger, f"Archivo no encontrado: {pdf_path}")
            return
        unlock_single_file(pdf_path)
    else:
        # Procesar todos los PDFs en data/
        data_dir = get_data_path()
        log_info(logger, f"Directorio: {data_dir}")
        unlock_all_files(data_dir)


if __name__ == "__main__":
    main()
