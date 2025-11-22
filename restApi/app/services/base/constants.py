"""
Service Layer Constants.

Centralizes all magic strings and constant values used across services
for better maintainability and consistency.
"""
from typing import Final

# =============================================================================
# File Operations
# =============================================================================

# Operation types
OPERATION_COPY: Final[str] = "copy"
OPERATION_MOVE: Final[str] = "move"
OPERATION_RENAME: Final[str] = "rename"
OPERATION_DELETE: Final[str] = "delete"

# Organization types
ORGANIZATION_BY_TYPE: Final[str] = "by_type"
ORGANIZATION_BY_YEAR: Final[str] = "by_year"

# =============================================================================
# Data Export
# =============================================================================

# Export formats
EXPORT_FORMAT_CSV: Final[str] = "csv"
EXPORT_FORMAT_EXCEL: Final[str] = "excel"
EXPORT_FORMAT_MARKDOWN: Final[str] = "markdown"

# File extensions
EXT_CSV: Final[str] = ".csv"
EXT_EXCEL: Final[str] = ".xlsx"
EXT_MARKDOWN: Final[str] = ".md"
EXT_PDF: Final[str] = ".pdf"

# Sheet names for Excel exports
SHEET_CUENTA: Final[str] = "Cuenta"
SHEET_RESUMEN: Final[str] = "Resumen"
SHEET_TRANSACCIONES: Final[str] = "Transacciones"
SHEET_TARJETA: Final[str] = "Tarjeta"
SHEET_CUPO: Final[str] = "Cupo"
SHEET_MOVIMIENTOS_PESOS: Final[str] = "Movimientos_Pesos"
SHEET_MOVIMIENTOS_DOLARES: Final[str] = "Movimientos_Dolares"

# =============================================================================
# Currency Codes
# =============================================================================

CURRENCY_COP: Final[str] = "COP"
CURRENCY_USD: Final[str] = "USD"

# =============================================================================
# Output Directories
# =============================================================================

DIR_DATA_EXTRACTED: Final[str] = "data-extracted"

# =============================================================================
# Error Messages
# =============================================================================

# Password-related keywords for exception detection
ERROR_KEYWORD_PASSWORD: Final[str] = "password"
ERROR_KEYWORD_ENCRYPTED: Final[str] = "encrypted"

# Operation error messages (templates)
ERROR_MSG_FAILED_TO: Final[str] = "Failed to {operation}: {error}"
ERROR_MSG_NO_TRANSACTIONS: Final[str] = "No transactions found in PDF"
ERROR_MSG_INVALID_FILENAME: Final[str] = "Invalid filename format: {filename}"

# =============================================================================
# Success Messages
# =============================================================================

# File operations
MSG_FILE_COPIED: Final[str] = "File copied successfully to {filename}"
MSG_FILE_MOVED: Final[str] = "File moved successfully to {filename}"
MSG_FILE_RENAMED: Final[str] = "File renamed successfully to {filename}"
MSG_FILE_DELETED: Final[str] = "File deleted successfully"

# Export operations
MSG_DATA_EXPORTED: Final[str] = "Data exported successfully to {filename}"
MSG_DATA_VALIDATED: Final[str] = "Data validated successfully"

# =============================================================================
# Data Keys (dict keys used in data structures)
# =============================================================================

# Common keys
KEY_FILENAME: Final[str] = "filename"
KEY_PATH: Final[str] = "path"
KEY_SIZE_BYTES: Final[str] = "size_bytes"
KEY_SIZE_MB: Final[str] = "size_mb"
KEY_CREATED_AT: Final[str] = "created_at"
KEY_MODIFIED_AT: Final[str] = "modified_at"
KEY_IS_ENCRYPTED: Final[str] = "is_encrypted"
KEY_PAGE_COUNT: Final[str] = "page_count"
KEY_IS_VALID: Final[str] = "is_valid"

# Inventory/Registry keys
KEY_TOTAL_FILES: Final[str] = "total_files"
KEY_TOTAL_SIZE_MB: Final[str] = "total_size_mb"
KEY_ENCRYPTED_COUNT: Final[str] = "encrypted_count"
KEY_DOCUMENT_TYPES: Final[str] = "document_types"
KEY_ENTRIES: Final[str] = "entries"
KEY_DOCUMENT_ID: Final[str] = "document_id"
KEY_DATE: Final[str] = "date"
KEY_TYPE: Final[str] = "type"
KEY_ACCOUNT_NUMBER: Final[str] = "account_number"
KEY_FILE_SIZE_MB: Final[str] = "file_size_mb"

# Organization result keys
KEY_FILES_PROCESSED: Final[str] = "files_processed"
KEY_FILES_MOVED: Final[str] = "files_moved"
KEY_FOLDERS_CREATED: Final[str] = "folders_created"
KEY_ERRORS: Final[str] = "errors"
KEY_SUMMARY: Final[str] = "summary"

# Statement data keys
KEY_CUENTA: Final[str] = "cuenta"
KEY_RESUMEN: Final[str] = "resumen"
KEY_TRANSACCIONES: Final[str] = "transacciones"
KEY_TARJETA: Final[str] = "tarjeta"
KEY_CUPO: Final[str] = "cupo"
KEY_MOVIMIENTOS_PESOS: Final[str] = "movimientos_pesos"
KEY_MOVIMIENTOS_DOLARES: Final[str] = "movimientos_dolares"

# Account info keys
KEY_NUMERO_CUENTA: Final[str] = "numero_cuenta"
KEY_TIPO_CUENTA: Final[str] = "tipo_cuenta"
KEY_TITULAR: Final[str] = "titular"
KEY_PERIODO: Final[str] = "periodo"

# Financial summary keys
KEY_SALDO_ANTERIOR: Final[str] = "saldo_anterior"
KEY_SALDO_ACTUAL: Final[str] = "saldo_actual"
KEY_TOTAL_CONSIGNACIONES: Final[str] = "total_consignaciones"
KEY_TOTAL_RETIROS: Final[str] = "total_retiros"

# Transaction keys
KEY_FECHA: Final[str] = "fecha"
KEY_DESCRIPCION: Final[str] = "descripcion"
KEY_VALOR: Final[str] = "valor"
KEY_OFICINA: Final[str] = "oficina"
KEY_REFERENCIA: Final[str] = "referencia"

# Credit card keys
KEY_NUMERO_TARJETA: Final[str] = "numero_tarjeta"
KEY_TIPO_TARJETA: Final[str] = "tipo_tarjeta"
KEY_NOMBRE_TARJETAHABIENTE: Final[str] = "nombre_tarjetahabiente"
KEY_CUPO_TOTAL: Final[str] = "cupo_total"
KEY_CUPO_DISPONIBLE: Final[str] = "cupo_disponible"
KEY_CUPO_UTILIZADO: Final[str] = "cupo_utilizado"
KEY_PAGOS: Final[str] = "pagos"
KEY_COMPRAS: Final[str] = "compras"
KEY_INTERESES: Final[str] = "intereses"

# =============================================================================
# Filter Keys
# =============================================================================

FILTER_TIPO: Final[str] = "tipo"
FILTER_FECHA: Final[str] = "fecha"

# =============================================================================
# PDF Document Info Keys (from PDFDocumentInfo dataclass)
# =============================================================================

INFO_ID: Final[str] = "id"
INFO_FILENAME: Final[str] = "filename"

# =============================================================================
# Validation Constants
# =============================================================================

VALIDATION_MIN_TRANSACTIONS: Final[int] = 0
VALIDATION_MAX_FILE_SIZE_MB: Final[int] = 50

# =============================================================================
# Export mapping (format -> extension)
# =============================================================================

EXPORT_EXTENSIONS: Final[dict[str, str]] = {
    EXPORT_FORMAT_CSV: EXT_CSV,
    EXPORT_FORMAT_EXCEL: EXT_EXCEL,
    EXPORT_FORMAT_MARKDOWN: EXT_MARKDOWN,
}
