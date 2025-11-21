"""Sistema de logging comprehensivo con archivos organizados por fecha.

Este módulo proporciona un sistema de logging fácil de usar que:
- Guarda logs en archivos separados por fecha (YYYY-MM-DD.log)
- Muestra logs en consola con colores
- Soporta múltiples niveles de log
- Permite configuración personalizada por módulo
- Rotación automática de archivos por día

Uso básico:
    from logger import setup_logger

    logger = setup_logger(__name__)
    logger.info("Mensaje informativo")
    logger.error("Mensaje de error")
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import colorlog


class DateBasedFileHandler(logging.Handler):
    """Handler que crea archivos de log basados en la fecha actual.

    Crea automáticamente un nuevo archivo cada día con formato:
    logs/YYYY-MM-DD.log
    """

    def __init__(self, log_dir: Path, level=logging.NOTSET):
        """
        Inicializa el handler.

        Args:
            log_dir: Directorio donde guardar los logs
            level: Nivel mínimo de logging
        """
        super().__init__(level)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._current_date = None
        self._file_handler = None

    def emit(self, record):
        """Emite un registro de log al archivo correspondiente."""
        today = datetime.now().date()

        # Si cambió el día, crear nuevo archivo
        if self._current_date != today:
            self._close_current_handler()
            self._create_new_handler(today)

        # Delegar al FileHandler interno
        if self._file_handler:
            self._file_handler.emit(record)

    def _create_new_handler(self, date):
        """Crea un nuevo FileHandler para la fecha especificada."""
        self._current_date = date
        log_file = self.log_dir / f"{date}.log"

        self._file_handler = logging.FileHandler(log_file, encoding='utf-8')
        self._file_handler.setFormatter(self.formatter)
        self._file_handler.setLevel(self.level)

    def _close_current_handler(self):
        """Cierra el FileHandler actual si existe."""
        if self._file_handler:
            self._file_handler.close()
            self._file_handler = None


def setup_logger(
    name: str,
    level: str = "INFO",
    log_dir: Optional[Path] = None,
    console_output: bool = True,
    file_output: bool = True,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Configura y retorna un logger con salida a archivo por fecha y consola con colores.

    Args:
        name: Nombre del logger (generalmente __name__)
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directorio para archivos de log (default: logs/)
        console_output: Si True, muestra logs en consola con colores
        file_output: Si True, guarda logs en archivo
        format_string: Formato personalizado para los logs

    Returns:
        Logger configurado

    Examples:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Inicio de la aplicación")
        >>> logger.warning("Advertencia")
        >>> logger.error("Error encontrado")

        >>> # Logger solo para archivo (sin consola)
        >>> logger = setup_logger(__name__, console_output=False)

        >>> # Logger con nivel DEBUG
        >>> logger = setup_logger(__name__, level="DEBUG")
    """
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Deshabilitar propagación para evitar duplicados con root logger
    logger.propagate = False

    # Limpiar handlers existentes para evitar duplicación
    logger.handlers.clear()

    # Formato por defecto
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Handler para consola con colores
    if console_output:
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))

        # Formato con colores
        color_format = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(color_format)
        logger.addHandler(console_handler)

    # Handler para archivo por fecha
    if file_output:
        if log_dir is None:
            # Usar directorio por defecto
            from config import LOGS_DIR
            log_dir = LOGS_DIR

        file_handler = DateBasedFileHandler(log_dir)
        file_handler.setLevel(getattr(logging, level.upper()))

        # Formato para archivo (sin colores)
        file_format = logging.Formatter(
            format_string,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger existente o crea uno nuevo con configuración por defecto.

    Args:
        name: Nombre del logger (generalmente __name__)

    Returns:
        Logger configurado

    Example:
        >>> from logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Mensaje")
    """
    logger = logging.getLogger(name)

    # Si no tiene handlers, configurarlo
    if not logger.handlers:
        return setup_logger(name)

    return logger


def configure_root_logger(level: str = "INFO", log_dir: Optional[Path] = None):
    """
    Configura el logger raíz para toda la aplicación.

    Útil para configurar logging de forma global al inicio de la aplicación.

    Args:
        level: Nivel de logging global
        log_dir: Directorio para archivos de log

    Example:
        >>> from logging_config import configure_root_logger
        >>> configure_root_logger(level="DEBUG")
        >>>
        >>> # Ahora cualquier logger funcionará
        >>> import logging
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Mensaje")
    """
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Limpiar handlers existentes
    root_logger.handlers.clear()

    # Usar setup_logger para configurar
    setup_logger("root", level=level, log_dir=log_dir)


def log_function_call(logger: logging.Logger):
    """
    Decorador para loguear llamadas a funciones automáticamente.

    Args:
        logger: Logger a usar

    Example:
        >>> logger = setup_logger(__name__)
        >>>
        >>> @log_function_call(logger)
        >>> def mi_funcion(x, y):
        >>>     return x + y
        >>>
        >>> resultado = mi_funcion(5, 3)  # Se loguea automáticamente
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Llamando a {func.__name__} con args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} completado exitosamente")
                return result
            except Exception as e:
                logger.error(f"Error en {func.__name__}: {e}", exc_info=True)
                raise
        return wrapper
    return decorator


def create_module_logger(module_name: str, level: str = "INFO") -> logging.Logger:
    """
    Crea un logger específico para un módulo con configuración personalizada.

    Args:
        module_name: Nombre del módulo
        level: Nivel de logging

    Returns:
        Logger configurado para el módulo

    Example:
        >>> # En un módulo de base de datos
        >>> db_logger = create_module_logger("database", level="DEBUG")
        >>> db_logger.debug("Ejecutando query...")
    """
    return setup_logger(module_name, level=level)


# Nota: No configuramos el root logger automáticamente para evitar
# conflictos y duplicación de logs. Si necesitas configuración global,
# llama explícitamente a configure_root_logger() al inicio de tu aplicación.
