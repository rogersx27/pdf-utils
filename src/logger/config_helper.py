"""Helper para configuración dinámica de loggers basada en categorías.

Este módulo proporciona funciones para configurar loggers según su categoría,
usando variables de entorno definidas en config.py.
"""
from typing import Tuple

from config import (
    LOG_LEVEL_CLI,
    LOG_LEVEL_COORDINATORS,
    LOG_LEVEL_PROCESSORS,
    LOG_LEVEL_UTILS,
)


class LoggerCategory:
    """Categorías de loggers según su función en la arquitectura."""

    CLI = "cli"
    COORDINATOR = "coordinator"
    PROCESSOR = "processor"
    UTILS = "utils"


def get_logger_config(category: str) -> Tuple[str, bool, bool]:
    """Obtiene la configuración de logger apropiada según la categoría.

    Args:
        category: Categoría del logger (CLI, COORDINATOR, PROCESSOR, UTILS)

    Returns:
        Tupla con (level, console_output, file_output)

    Example:
        >>> level, console, file = get_logger_config(LoggerCategory.CLI)
        >>> logger = setup_logger(__name__, level=level, console_output=console, file_output=file)
    """
    configs = {
        LoggerCategory.CLI: (
            LOG_LEVEL_CLI,
            True,  # Consola activada para interacción con usuario
            True,  # Archivo activado
        ),
        LoggerCategory.COORDINATOR: (
            LOG_LEVEL_COORDINATORS,
            True,  # Consola activada para mostrar progreso
            True,  # Archivo activado
        ),
        LoggerCategory.PROCESSOR: (
            LOG_LEVEL_PROCESSORS,
            False,  # Sin consola para evitar saturación
            True,  # Archivo activado
        ),
        LoggerCategory.UTILS: (
            LOG_LEVEL_UTILS,
            False,  # Sin consola, solo problemas
            True,  # Archivo activado
        ),
    }

    return configs.get(category, (LOG_LEVEL_COORDINATORS, True, True))


def setup_cli_logger(logger_setup_func, module_name: str):
    """Configura logger para scripts CLI.

    Args:
        logger_setup_func: Función setup_logger del paquete logger
        module_name: Nombre del módulo (__name__)

    Returns:
        Logger configurado

    Example:
        >>> from logger import setup_logger
        >>> from logger.config_helper import setup_cli_logger
        >>> logger = setup_cli_logger(setup_logger, __name__)
    """
    level, console, file = get_logger_config(LoggerCategory.CLI)
    return logger_setup_func(
        module_name, level=level, console_output=console, file_output=file
    )


def setup_coordinator_logger(logger_setup_func, module_name: str):
    """Configura logger para módulos coordinadores.

    Args:
        logger_setup_func: Función setup_logger del paquete logger
        module_name: Nombre del módulo (__name__)

    Returns:
        Logger configurado

    Example:
        >>> from logger import setup_logger
        >>> from logger.config_helper import setup_coordinator_logger
        >>> logger = setup_coordinator_logger(setup_logger, __name__)
    """
    level, console, file = get_logger_config(LoggerCategory.COORDINATOR)
    return logger_setup_func(
        module_name, level=level, console_output=console, file_output=file
    )


def setup_processor_logger(logger_setup_func, module_name: str):
    """Configura logger para módulos procesadores.

    Args:
        logger_setup_func: Función setup_logger del paquete logger
        module_name: Nombre del módulo (__name__)

    Returns:
        Logger configurado

    Example:
        >>> from logger import setup_logger
        >>> from logger.config_helper import setup_processor_logger
        >>> logger = setup_processor_logger(setup_logger, __name__)
    """
    level, console, file = get_logger_config(LoggerCategory.PROCESSOR)
    return logger_setup_func(
        module_name, level=level, console_output=console, file_output=file
    )


def setup_utils_logger(logger_setup_func, module_name: str):
    """Configura logger para módulos de utilidades.

    Args:
        logger_setup_func: Función setup_logger del paquete logger
        module_name: Nombre del módulo (__name__)

    Returns:
        Logger configurado

    Example:
        >>> from logger import setup_logger
        >>> from logger.config_helper import setup_utils_logger
        >>> logger = setup_utils_logger(setup_logger, __name__)
    """
    level, console, file = get_logger_config(LoggerCategory.UTILS)
    return logger_setup_func(
        module_name, level=level, console_output=console, file_output=file
    )
