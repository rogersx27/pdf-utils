"""Pretty logging helpers para mejorar la presentación visual de logs.

Sistema simple de helpers para crear logs más legibles y estéticos,
sin complicaciones innecesarias.

Uso:
    from logger.pretty import log_header, log_info, log_success

    log_header(logger, "Mi Aplicación")
    log_info(logger, "Procesando datos...")
    log_success(logger, "Completado!")
"""
import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional


# ============================================================================
# Estado de Indentación (simple)
# ============================================================================
_indent_level = 0
_indent_char = "   "  # 3 espacios


@contextmanager
def indent():
    """Context manager para indentación automática.

    Example:
        >>> log_section(logger, "Procesando archivos")
        >>> with indent():
        ...     log_info(logger, "Archivo 1")
        ...     log_info(logger, "Archivo 2")
    """
    global _indent_level
    _indent_level += 1
    try:
        yield
    finally:
        _indent_level -= 1


def _get_indent() -> str:
    """Retorna la indentación actual."""
    return _indent_char * _indent_level


# ============================================================================
# Funciones de Formato Simple
# ============================================================================

def log_header(logger: logging.Logger, text: str, icon: str = "🎯") -> None:
    """Log de encabezado principal con marco.

    Args:
        logger: Logger a usar
        text: Texto del encabezado
        icon: Emoji/icono a mostrar

    Example:
        >>> log_header(logger, "MODO ANÁLISIS", icon="📊")
    """
    width = 60
    border_top = "╔" + "═" * (width - 2) + "╗"
    border_bottom = "╚" + "═" * (width - 2) + "╝"

    # Centrar texto con icono
    content = f"{icon}  {text}"
    padding = (width - len(content) - 2) // 2
    line = "║" + " " * padding + content + " " * (width - len(content) - padding - 2) + "║"

    logger.info(border_top)
    logger.info(line)
    logger.info(border_bottom)
    logger.info("")


def log_section(logger: logging.Logger, text: str, icon: str = "📋") -> None:
    """Log de sección con separador simple.

    Args:
        logger: Logger a usar
        text: Texto de la sección
        icon: Emoji/icono a mostrar

    Example:
        >>> log_section(logger, "Análisis de Estructura")
    """
    indent = _get_indent()
    logger.info(f"{indent}{icon} {text}")


def log_subsection(logger: logging.Logger, text: str, icon: str = "▸") -> None:
    """Log de subsección.

    Args:
        logger: Logger a usar
        text: Texto de la subsección
        icon: Emoji/icono a mostrar
    """
    indent = _get_indent()
    logger.info(f"{indent}  {icon} {text}")


def log_info(logger: logging.Logger, text: str, prefix: str = "ℹ️") -> None:
    """Log de información con indentación.

    Args:
        logger: Logger a usar
        text: Texto informativo
        prefix: Prefijo/icono
    """
    indent = _get_indent()
    logger.info(f"{indent}{prefix}  {text}")


def log_success(logger: logging.Logger, text: str) -> None:
    """Log de éxito.

    Args:
        logger: Logger a usar
        text: Mensaje de éxito
    """
    indent = _get_indent()
    logger.info(f"{indent}✅ {text}")


def log_error(logger: logging.Logger, text: str) -> None:
    """Log de error.

    Args:
        logger: Logger a usar
        text: Mensaje de error
    """
    indent = _get_indent()
    logger.error(f"{indent}❌ {text}")


def log_warning(logger: logging.Logger, text: str) -> None:
    """Log de advertencia.

    Args:
        logger: Logger a usar
        text: Mensaje de advertencia
    """
    indent = _get_indent()
    logger.warning(f"{indent}⚠️  {text}")


def log_item(logger: logging.Logger, key: str, value: Any, bullet: str = "├─") -> None:
    """Log de item en lista/árbol.

    Args:
        logger: Logger a usar
        key: Clave/nombre del item
        value: Valor del item
        bullet: Carácter de bullet (├─ o └─)

    Example:
        >>> log_item(logger, "Archivos", 42)
        >>> log_item(logger, "Estado", "Completado", bullet="└─")
    """
    indent = _get_indent()
    logger.info(f"{indent}{bullet} {key}: {value}")


def log_separator(logger: logging.Logger, char: str = "─", width: int = 60) -> None:
    """Log de separador visual.

    Args:
        logger: Logger a usar
        char: Carácter para el separador
        width: Ancho del separador
    """
    indent = _get_indent()
    logger.info(f"{indent}{char * width}")


def log_blank(logger: logging.Logger, lines: int = 1) -> None:
    """Log de línea(s) en blanco.

    Args:
        logger: Logger a usar
        lines: Número de líneas en blanco
    """
    for _ in range(lines):
        logger.info("")


# ============================================================================
# Funciones para Datos Estructurados
# ============================================================================

def log_dict(logger: logging.Logger, data: Dict[str, Any], title: Optional[str] = None) -> None:
    """Log de diccionario con formato de árbol.

    Args:
        logger: Logger a usar
        data: Diccionario a mostrar
        title: Título opcional

    Example:
        >>> log_dict(logger, {"nombre": "Juan", "edad": 30}, title="Usuario")
    """
    if title:
        log_section(logger, title)

    items = list(data.items())
    for i, (key, value) in enumerate(items):
        is_last = i == len(items) - 1
        bullet = "└─" if is_last else "├─"
        log_item(logger, key, value, bullet=bullet)


def log_list(logger: logging.Logger, items: List[Any], title: Optional[str] = None,
             icon: str = "•") -> None:
    """Log de lista con bullets.

    Args:
        logger: Logger a usar
        items: Lista de items
        title: Título opcional
        icon: Icono/bullet para cada item

    Example:
        >>> log_list(logger, ["item1", "item2", "item3"], title="Archivos")
    """
    if title:
        log_section(logger, title)

    indent = _get_indent()
    for item in items:
        logger.info(f"{indent}  {icon} {item}")


def log_table(logger: logging.Logger, headers: List[str], rows: List[List[Any]],
              title: Optional[str] = None) -> None:
    """Log de tabla simple.

    Args:
        logger: Logger a usar
        headers: Encabezados de columnas
        rows: Filas de datos
        title: Título opcional

    Example:
        >>> headers = ["Nombre", "Edad", "Ciudad"]
        >>> rows = [["Juan", 30, "Madrid"], ["Ana", 25, "Barcelona"]]
        >>> log_table(logger, headers, rows, title="Usuarios")
    """
    if title:
        log_section(logger, title)

    # Calcular anchos de columna
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    indent = _get_indent()

    # Header
    header_line = " │ ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    logger.info(f"{indent}  {header_line}")

    # Separador
    sep = "─┼─".join("─" * w for w in col_widths)
    logger.info(f"{indent}  {sep}")

    # Rows
    for row in rows:
        row_line = " │ ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths))
        logger.info(f"{indent}  {row_line}")


# ============================================================================
# Funciones de Progreso
# ============================================================================

def log_progress(logger: logging.Logger, current: int, total: int,
                 text: str = "Progreso", width: int = 30) -> None:
    """Log de barra de progreso simple.

    Args:
        logger: Logger a usar
        current: Valor actual
        total: Valor total
        text: Texto descriptivo
        width: Ancho de la barra

    Example:
        >>> for i in range(1, 101):
        ...     log_progress(logger, i, 100, "Procesando")
    """
    percentage = int((current / total) * 100)
    filled = int((current / total) * width)
    bar = "█" * filled + "░" * (width - filled)

    indent = _get_indent()
    logger.info(f"{indent}{text}: [{bar}] {percentage}% ({current}/{total})")


def log_stats(logger: logging.Logger, stats: Dict[str, Any], title: str = "Estadísticas") -> None:
    """Log de estadísticas con formato bonito.

    Args:
        logger: Logger a usar
        stats: Diccionario con estadísticas
        title: Título de la sección

    Example:
        >>> stats = {
        ...     "Archivos procesados": 42,
        ...     "Errores": 0,
        ...     "Tiempo": "2.5s"
        ... }
        >>> log_stats(logger, stats)
    """
    log_section(logger, title, icon="📊")

    with indent():
        items = list(stats.items())
        for i, (key, value) in enumerate(items):
            is_last = i == len(items) - 1
            bullet = "└─" if is_last else "├─"
            log_item(logger, key, value, bullet=bullet)


# ============================================================================
# Helpers de Contexto (para archivos/procesos)
# ============================================================================

def log_file_info(logger: logging.Logger, filename: str, details: Optional[Dict[str, Any]] = None) -> None:
    """Log de información de archivo con formato consistente.

    Args:
        logger: Logger a usar
        filename: Nombre del archivo
        details: Detalles adicionales del archivo

    Example:
        >>> log_file_info(logger, "datos.xlsx", {"Tamaño": "2.5 MB", "Hojas": 3})
    """
    log_section(logger, f"Archivo: {filename}", icon="📄")

    if details:
        with indent():
            items = list(details.items())
            for i, (key, value) in enumerate(items):
                is_last = i == len(items) - 1
                bullet = "└─" if is_last else "├─"
                log_item(logger, key, value, bullet=bullet)


def log_sheet_info(logger: logging.Logger, sheet_name: str, info: Dict[str, Any]) -> None:
    """Log de información de hoja Excel.

    Args:
        logger: Logger a usar
        sheet_name: Nombre de la hoja
        info: Información de la hoja

    Example:
        >>> info = {"Tipo": "COMPLEX", "Filas": 567, "Encabezados": 14}
        >>> log_sheet_info(logger, "Pendientes", info)
    """
    log_subsection(logger, f"Hoja: {sheet_name}", icon="📋")

    with indent():
        items = list(info.items())
        for i, (key, value) in enumerate(items):
            is_last = i == len(items) - 1
            bullet = "└─" if is_last else "├─"
            log_item(logger, key, value, bullet=bullet)


def log_process_start(logger: logging.Logger, process: str, target: str = "") -> None:
    """Log de inicio de proceso.

    Args:
        logger: Logger a usar
        process: Nombre del proceso
        target: Objetivo/archivo del proceso
    """
    if target:
        log_info(logger, f"🚀 {process}: {target}")
    else:
        log_info(logger, f"🚀 {process}")


def log_process_end(logger: logging.Logger, process: str, duration: Optional[float] = None) -> None:
    """Log de fin de proceso.

    Args:
        logger: Logger a usar
        process: Nombre del proceso
        duration: Duración en segundos (opcional)
    """
    if duration:
        log_success(logger, f"{process} completado en {duration:.2f}s")
    else:
        log_success(logger, f"{process} completado")


# ============================================================================
# Funciones de Conveniencia
# ============================================================================

def format_number(num: int) -> str:
    """Formatea número con separadores de miles.

    Args:
        num: Número a formatear

    Returns:
        Número formateado (ej: "1,234,567")
    """
    return f"{num:,}"


def format_bytes(bytes_size: int) -> str:
    """Formatea tamaño en bytes a formato legible.

    Args:
        bytes_size: Tamaño en bytes

    Returns:
        Tamaño formateado (ej: "2.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def format_duration(seconds: float) -> str:
    """Formatea duración en segundos a formato legible.

    Args:
        seconds: Duración en segundos

    Returns:
        Duración formateada (ej: "2m 30s", "45.2s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
