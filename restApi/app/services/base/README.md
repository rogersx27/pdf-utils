# Service Constants Documentation

Este archivo documenta las constantes utilizadas en la capa de servicios de la API REST.

## Propósito

Las constantes centralizan todos los "magic strings" (cadenas mágicas) utilizadas en los servicios, mejorando:

- **Mantenibilidad**: Cambios en un solo lugar
- **Consistencia**: Uso uniforme en todo el código
- **Detección de errores**: Errores de tipeo detectados en tiempo de compilación
- **Refactorización segura**: IDE puede rastrear referencias
- **Documentación implícita**: Nombres descriptivos de constantes

## Categorías de Constantes

### 1. Operaciones de Archivos (`OPERATION_*`)

Tipos de operaciones en archivos PDF:

```python
OPERATION_COPY = "copy"
OPERATION_MOVE = "move"
OPERATION_RENAME = "rename"
OPERATION_DELETE = "delete"
```

**Uso**: `FileManagerService` para identificar tipos de operación en respuestas.

### 2. Tipos de Organización (`ORGANIZATION_*`)

Métodos de organización de archivos:

```python
ORGANIZATION_BY_TYPE = "by_type"
ORGANIZATION_BY_YEAR = "by_year"
```

**Uso**: `PDFOrganizer` para clasificar PDFs.

### 3. Formatos de Exportación (`EXPORT_FORMAT_*`, `EXT_*`)

Formatos soportados para exportación de datos:

```python
EXPORT_FORMAT_CSV = "csv"
EXPORT_FORMAT_EXCEL = "excel"
EXPORT_FORMAT_MARKDOWN = "markdown"

EXT_CSV = ".csv"
EXT_EXCEL = ".xlsx"
EXT_MARKDOWN = ".md"
EXT_PDF = ".pdf"
```

**Mapeo**: `EXPORT_EXTENSIONS` relaciona formatos con extensiones.

### 4. Nombres de Hojas Excel (`SHEET_*`)

Nombres estándar para hojas en archivos Excel exportados:

```python
# Cuentas de ahorro
SHEET_CUENTA = "Cuenta"
SHEET_RESUMEN = "Resumen"
SHEET_TRANSACCIONES = "Transacciones"

# Tarjetas de crédito
SHEET_TARJETA = "Tarjeta"
SHEET_CUPO = "Cupo"
SHEET_MOVIMIENTOS_PESOS = "Movimientos_Pesos"
SHEET_MOVIMIENTOS_DOLARES = "Movimientos_Dolares"
```

**Uso**: `DataProcessorService` al exportar datos estructurados.

### 5. Códigos de Moneda (`CURRENCY_*`)

```python
CURRENCY_COP = "COP"  # Pesos colombianos
CURRENCY_USD = "USD"  # Dólares estadounidenses
```

**Uso**: `CreditCardExtractor` para procesar transacciones multi-moneda.

### 6. Directorios de Salida (`DIR_*`)

```python
DIR_DATA_EXTRACTED = "data-extracted"
```

**Uso**: `OutputDirectoryMixin` para determinar ubicación de archivos exportados.

### 7. Mensajes de Error (`ERROR_*`)

#### Palabras clave para detección de errores

```python
ERROR_KEYWORD_PASSWORD = "password"
ERROR_KEYWORD_ENCRYPTED = "encrypted"
```

**Uso**: `ExceptionMapperMixin` para clasificar excepciones relacionadas con contraseñas.

#### Plantillas de mensajes de error

```python
ERROR_MSG_FAILED_TO = "Failed to {operation}: {error}"
ERROR_MSG_NO_TRANSACTIONS = "No transactions found in PDF"
ERROR_MSG_INVALID_FILENAME = "Invalid filename format: {filename}"
```

**Uso**: Formateo consistente de mensajes de error en todos los servicios.

### 8. Mensajes de Éxito (`MSG_*`)

```python
# Operaciones de archivo
MSG_FILE_COPIED = "File copied successfully to {filename}"
MSG_FILE_MOVED = "File moved successfully to {filename}"
MSG_FILE_RENAMED = "File renamed successfully to {filename}"
MSG_FILE_DELETED = "File deleted successfully"

# Exportación de datos
MSG_DATA_EXPORTED = "Data exported successfully to {filename}"
MSG_DATA_VALIDATED = "Data validated successfully"
```

**Uso**: Mensajes de respuesta uniformes en API.

### 9. Claves de Datos (`KEY_*`)

Claves estándar para diccionarios de datos:

#### Claves generales
```python
KEY_FILENAME = "filename"
KEY_PATH = "path"
KEY_SIZE_BYTES = "size_bytes"
KEY_SIZE_MB = "size_mb"
KEY_CREATED_AT = "created_at"
KEY_MODIFIED_AT = "modified_at"
KEY_IS_ENCRYPTED = "is_encrypted"
KEY_PAGE_COUNT = "page_count"
KEY_IS_VALID = "is_valid"
```

#### Claves de inventario/registro
```python
KEY_TOTAL_FILES = "total_files"
KEY_TOTAL_SIZE_MB = "total_size_mb"
KEY_ENCRYPTED_COUNT = "encrypted_count"
KEY_DOCUMENT_TYPES = "document_types"
KEY_ENTRIES = "entries"
KEY_DOCUMENT_ID = "document_id"
KEY_DATE = "date"
KEY_TYPE = "type"
KEY_ACCOUNT_NUMBER = "account_number"
```

#### Claves de extractos bancarios
```python
# Cuenta de ahorros
KEY_CUENTA = "cuenta"
KEY_RESUMEN = "resumen"
KEY_TRANSACCIONES = "transacciones"
KEY_NUMERO_CUENTA = "numero_cuenta"
KEY_TIPO_CUENTA = "tipo_cuenta"
KEY_TITULAR = "titular"
KEY_PERIODO = "periodo"
KEY_SALDO_ANTERIOR = "saldo_anterior"
KEY_SALDO_ACTUAL = "saldo_actual"
KEY_TOTAL_CONSIGNACIONES = "total_consignaciones"
KEY_TOTAL_RETIROS = "total_retiros"

# Transacciones
KEY_FECHA = "fecha"
KEY_DESCRIPCION = "descripcion"
KEY_VALOR = "valor"
KEY_OFICINA = "oficina"
KEY_REFERENCIA = "referencia"

# Tarjeta de crédito
KEY_TARJETA = "tarjeta"
KEY_CUPO = "cupo"
KEY_MOVIMIENTOS_PESOS = "movimientos_pesos"
KEY_MOVIMIENTOS_DOLARES = "movimientos_dolares"
KEY_NUMERO_TARJETA = "numero_tarjeta"
KEY_TIPO_TARJETA = "tipo_tarjeta"
KEY_NOMBRE_TARJETAHABIENTE = "nombre_tarjetahabiente"
KEY_CUPO_TOTAL = "cupo_total"
KEY_CUPO_DISPONIBLE = "cupo_disponible"
KEY_CUPO_UTILIZADO = "cupo_utilizado"
KEY_PAGOS = "pagos"
KEY_COMPRAS = "compras"
KEY_INTERESES = "intereses"
```

#### Claves de resultados de organización
```python
KEY_FILES_PROCESSED = "files_processed"
KEY_FILES_MOVED = "files_moved"
KEY_FOLDERS_CREATED = "folders_created"
KEY_ERRORS = "errors"
KEY_SUMMARY = "summary"
```

### 10. Claves de Filtros (`FILTER_*`)

```python
FILTER_TIPO = "tipo"
FILTER_FECHA = "fecha"
```

**Uso**: `PDFAnalyzerService.list_pdfs()` para filtrar documentos.

### 11. Claves de Información de Documento PDF (`INFO_*`)

```python
INFO_ID = "id"
INFO_FILENAME = "filename"
```

**Uso**: Serialización de `PDFDocumentInfo`.

### 12. Constantes de Validación

```python
VALIDATION_MIN_TRANSACTIONS = 0
VALIDATION_MAX_FILE_SIZE_MB = 50
```

**Uso**: Validación de datos en procesadores.

### 13. Mapeos

```python
EXPORT_EXTENSIONS: dict[str, str] = {
    EXPORT_FORMAT_CSV: EXT_CSV,
    EXPORT_FORMAT_EXCEL: EXT_EXCEL,
    EXPORT_FORMAT_MARKDOWN: EXT_MARKDOWN,
}
```

**Uso**: Conversión de formato a extensión de archivo.

## Ejemplos de Uso

### Ejemplo 1: FileManagerService

**Antes:**
```python
return FileOperationResponse(
    success=True,
    operation="copy",
    message=f"File copied successfully to {filename}"
)
```

**Después:**
```python
return FileOperationResponse(
    success=True,
    operation=OPERATION_COPY,
    message=MSG_FILE_COPIED.format(filename=filename)
)
```

### Ejemplo 2: DataProcessorService

**Antes:**
```python
if export_format == "excel":
    processor.export_to_excel(data, output_path)
    return ["Transacciones", "Resumen", "Cuenta"]
```

**Después:**
```python
if export_format == EXPORT_FORMAT_EXCEL:
    processor.export_to_excel(data, output_path)
    return [SHEET_TRANSACCIONES, SHEET_RESUMEN, SHEET_CUENTA]
```

### Ejemplo 3: Manejo de Excepciones

**Antes:**
```python
error_msg = str(e).lower()
if "password" in error_msg or "encrypted" in error_msg:
    raise PDFPasswordError(str(e)) from e
raise InternalServerError(f"Failed to {operation}: {str(e)}") from e
```

**Después:**
```python
error_msg = str(e).lower()
if ERROR_KEYWORD_PASSWORD in error_msg or ERROR_KEYWORD_ENCRYPTED in error_msg:
    raise PDFPasswordError(str(e)) from e
raise InternalServerError(ERROR_MSG_FAILED_TO.format(operation=operation, error=str(e))) from e
```

## Mejores Prácticas

1. **Siempre importar constantes necesarias** al inicio de cada servicio
2. **No crear strings duplicados** - verificar si ya existe una constante
3. **Usar `Final` type hint** para todas las constantes
4. **Nombres descriptivos en UPPER_SNAKE_CASE**
5. **Agrupar constantes relacionadas** con comentarios de sección
6. **Documentar con docstrings** cuando el propósito no sea obvio
7. **Plantillas con `.format()`** para mensajes parametrizados

## Migración desde Magic Strings

Al encontrar un magic string en el código:

1. Verificar si ya existe una constante apropiada
2. Si no existe, agregarla a `constants.py` en la categoría correcta
3. Importar la constante en el archivo que la necesita
4. Reemplazar el string literal con la constante
5. Ejecutar tests para verificar que todo funciona

## Mantenimiento

Al agregar nuevas constantes:

- Mantener orden alfabético dentro de cada categoría
- Actualizar este README con ejemplos si es necesario
- Usar nombres que reflejen el dominio del negocio
- Considerar crear subcategorías si una sección crece demasiado

## Referencias

- Servicios que usan constantes:
  - `concerns.py`: Mixins base
  - `file_manager_service.py`: Operaciones de archivo
  - `data_processor_service.py`: Procesamiento y exportación
  - `pdf_analyzer_service.py`: Análisis de PDFs
