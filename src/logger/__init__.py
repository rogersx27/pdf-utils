"""Paquete de logging comprehensivo con archivos por fecha.

Este paquete proporciona un sistema de logging fácil de usar con:
- Archivos organizados por fecha (YYYY-MM-DD.log)
- Salida en consola con colores
- Configuración flexible por módulo
- Configuración dinámica basada en variables de entorno
- Pretty logging para outputs estéticos

Uso básico:
    from logger import setup_logger
    logger = setup_logger(__name__)
    logger.info("Mensaje")

Uso con categorías (recomendado):
    from logger import setup_logger, setup_cli_logger
    logger = setup_cli_logger(setup_logger, __name__)

Uso con pretty logging:
    from logger import setup_cli_logger, log_header, log_success
    logger = setup_cli_logger(setup_logger, __name__)
    log_header(logger, "Mi Aplicación")
    log_success(logger, "Todo listo!")
"""

from .logging_config import (
    setup_logger,
    get_logger,
    configure_root_logger,
    log_function_call,
    create_module_logger,
    DateBasedFileHandler,
)

from .config_helper import (
    setup_cli_logger,
    setup_coordinator_logger,
    setup_processor_logger,
    setup_utils_logger,
    LoggerCategory,
    get_logger_config,
)

# Pretty logging functions
from .pretty import (
    # Context managers
    indent,
    # Basic formatting
    log_header,
    log_section,
    log_subsection,
    log_info,
    log_success,
    log_error,
    log_warning,
    log_item,
    log_separator,
    log_blank,
    # Structured data
    log_dict,
    log_list,
    log_table,
    log_stats,
    # Progress
    log_progress,
    # Context helpers
    log_file_info,
    log_sheet_info,
    log_process_start,
    log_process_end,
    # Formatters
    format_number,
    format_bytes,
    format_duration,
)

__all__ = [
    # Core logging functions
    "setup_logger",
    "get_logger",
    "configure_root_logger",
    "log_function_call",
    "create_module_logger",
    "DateBasedFileHandler",
    # Category-based helpers
    "setup_cli_logger",
    "setup_coordinator_logger",
    "setup_processor_logger",
    "setup_utils_logger",
    "LoggerCategory",
    "get_logger_config",
    # Pretty logging
    "indent",
    "log_header",
    "log_section",
    "log_subsection",
    "log_info",
    "log_success",
    "log_error",
    "log_warning",
    "log_item",
    "log_separator",
    "log_blank",
    "log_dict",
    "log_list",
    "log_table",
    "log_stats",
    "log_progress",
    "log_file_info",
    "log_sheet_info",
    "log_process_start",
    "log_process_end",
    "format_number",
    "format_bytes",
    "format_duration",
]

__version__ = "1.2.0"
