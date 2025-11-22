"""
Script completo de procesamiento de extractos bancarios.

Este script realiza el flujo completo:
1. Quita la contraseña de los PDFs en data/
2. Guarda los PDFs desbloqueados en password-less/
3. Identifica el tipo de extracto (Ahorros o Crédito)
4. Extrae la información y la guarda en Excel en data-extracted/
"""

import sys
import os
from pathlib import Path

# Agregar src al path para importaciones
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

from logger import setup_logger, setup_cli_logger, log_header, log_success, log_info, log_error, log_warning
from pdf_analyzer import (
    SecurityService,
    list_pdfs,
    get_data_path,
    parse_filename,
    ensure_directory
)
from data_processor import SavingsAccountProcessor, CreditCardProcessor

# Cargar variables de entorno
load_dotenv()

# Configurar logger
logger = setup_cli_logger(setup_logger, __name__)

def main():
    log_header(logger, "Pipeline Completo de Procesamiento")

    # 1. Configuración de directorios
    root_path = Path(__file__).parent.parent
    data_path = get_data_path()
    unlocked_path = root_path / "password-less"
    extracted_path = root_path / "data-extracted"

    ensure_directory(unlocked_path)
    ensure_directory(extracted_path)

    log_info(logger, f"Directorio de entrada: {data_path}")
    log_info(logger, f"Directorio sin contraseña: {unlocked_path}")
    log_info(logger, f"Directorio de extracción: {extracted_path}")

    # 2. Obtener PDFs
    pdfs = list_pdfs(data_path)
    log_info(logger, f"PDFs encontrados: {len(pdfs)}")

    if not pdfs:
        log_error(logger, "No se encontraron archivos PDF en data/")
        return

    # Inicializar servicios
    security_service = SecurityService()
    savings_processor = SavingsAccountProcessor()
    credit_processor = CreditCardProcessor()

    # 3. Procesar cada PDF
    for pdf_path in pdfs:
        logger.info("")
        logger.info("-" * 50)
        log_info(logger, f"Procesando: {pdf_path.name}")

        try:
            # Paso 1: Quitar contraseña
            unlocked_file = unlocked_path / pdf_path.name
            
            # Si ya existe, lo usamos, si no, intentamos desbloquearlo
            if unlocked_file.exists():
                log_info(logger, "  Archivo desbloqueado ya existe, usando copia existente.")
            else:
                if security_service.is_encrypted(pdf_path):
                    log_info(logger, "  Archivo encriptado, quitando contraseña...")
                    try:
                        security_service.remove_password(pdf_path, output_path=unlocked_file)
                        log_success(logger, "  Contraseña eliminada exitosamente.")
                    except ValueError as e:
                        log_error(logger, f"  Error al quitar contraseña: {e}")
                        continue
                else:
                    # Si no está encriptado, simplemente lo copiamos
                    import shutil
                    shutil.copy2(pdf_path, unlocked_file)
                    log_info(logger, "  Archivo no estaba encriptado, copiado a password-less/.")

            # Paso 2: Identificar y Extraer
            info = parse_filename(unlocked_file.name)
            tipo = info.get("tipo", "DESCONOCIDO")
            
            log_info(logger, f"  Tipo detectado: {tipo}")

            output_filename = unlocked_file.stem + ".xlsx"
            output_file = extracted_path / output_filename

            if "CTA_AHORROS" in tipo:
                log_info(logger, "  Ejecutando extractor de Cuenta de Ahorros...")
                result = savings_processor.process(unlocked_file)
                savings_processor.export_to_excel(result, output_file)
                log_success(logger, f"  Datos extraídos a: {output_file.name}")
                
            elif "TARJETA" in tipo or "MASTERCARD" in tipo or "VISA" in tipo:
                log_info(logger, "  Ejecutando extractor de Tarjeta de Crédito...")
                result = credit_processor.process(unlocked_file)
                credit_processor.export_to_excel(result, output_file)
                log_success(logger, f"  Datos extraídos a: {output_file.name}")
                
            else:
                log_warning(logger, f"  Tipo de extracto no soportado para extracción automática: {tipo}")

        except Exception as e:
            log_error(logger, f"  Error inesperado procesando {pdf_path.name}: {e}")
            import traceback
            logger.debug(traceback.format_exc())

    logger.info("")
    log_header(logger, "Procesamiento Finalizado")

if __name__ == "__main__":
    main()
