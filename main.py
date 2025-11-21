"""
Script principal para análisis de extractos bancarios en PDF.

Uso:
    # Configurar contraseña via variable de entorno (en .env o directamente)
    # Luego ejecutar:
    python main.py
"""

import sys
from pathlib import Path

# Agregar src al path para importaciones
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv

from logger import setup_logger, setup_cli_logger, log_header, log_success, log_info, log_error
from pdf_analyzer import PDFAnalyzer, list_pdfs, get_data_path
from pdf_analyzer.utils import parse_filename

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar logger como CLI (con consola y archivo)
logger = setup_cli_logger(setup_logger, __name__)


def main():
    """Función principal de demostración."""
    log_header(logger, "PDF Analyzer - Extractos Bancarios")

    data_path = get_data_path()
    log_info(logger, f"Directorio de datos: {data_path}")

    # Listar todos los PDFs disponibles
    pdfs = list_pdfs(data_path)
    log_info(logger, f"PDFs encontrados: {len(pdfs)}")

    if not pdfs:
        log_error(logger, "No se encontraron archivos PDF en la carpeta data/")
        return

    # Mostrar información de cada PDF
    logger.info("")
    logger.info("Archivos disponibles:")
    for pdf_path in pdfs:
        info = parse_filename(pdf_path.name)
        tipo = info.get("tipo", "N/A")
        fecha = info.get("fecha", "N/A")
        logger.info(f"  - {pdf_path.name}")
        logger.info(f"    Tipo: {tipo} | Fecha: {fecha}")

    # Ejemplo de análisis del primer PDF
    logger.info("")
    logger.info("-" * 50)
    logger.info("Analizando primer PDF como ejemplo...")
    logger.info("")

    try:
        analyzer = PDFAnalyzer(pdfs[0])
        summary = analyzer.get_summary()

        log_success(logger, f"Análisis completado: {summary['filename']}")
        logger.info(f"  Páginas: {summary['num_pages']}")
        logger.info(f"  Tablas encontradas: {summary['num_tables']}")
        logger.info(f"  Caracteres de texto: {summary['text_length']}")

    except Exception as e:
        log_error(logger, f"Error al analizar PDF: {e}")
        logger.error("Verifica que la contraseña PDF_PASSWORD esté configurada en .env")


if __name__ == "__main__":
    main()
