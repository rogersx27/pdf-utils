# Controllers Package - Guía de Uso

Este paquete contiene los controladores HTTP para la API REST del PDF Analyzer. Los controladores son responsables de manejar las respuestas HTTP y delegar la lógica de negocio a los servicios.

## 📁 Estructura

```
app/controllers/
├── __init__.py              # Exportaciones del paquete
├── pdf_controller.py        # Controlador para operaciones de PDF
├── file_controller.py       # Controlador para operaciones de archivos
├── export_controller.py     # Controlador para exportación de datos
└── README.md               # Esta guía
```

## 🎯 Arquitectura

```
API Endpoints -> Controllers -> Services -> Core Logic
                      ↓
                Core Utilities
         (responses, exceptions, decorators)
```

**Responsabilidades:**

- **Controllers**: Manejo de HTTP requests/responses
- **Services**: Lógica de negocio
- **Core**: Utilidades compartidas (excepciones, respuestas, decoradores)

## 📚 Controladores Disponibles

### 1. PDFController

Maneja operaciones de análisis de PDFs.

#### Inicialización:

```python
from app.controllers import PDFController

# Con password por defecto
controller = PDFController(password="secret")

# Sin password
controller = PDFController()
```

#### Métodos disponibles:

##### Listar PDFs

```python
# Sin filtros
response = await controller.list_pdfs()

# Con filtros
response = await controller.list_pdfs(
    tipo="CTA_AHORROS",
    fecha="202501"
)
```

**Response:**
```json
{
    "success": true,
    "message": "Found 5 PDF(s)",
    "data": [
        {
            "filename": "Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
            "path": "/data/Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
            "document_info": {
                "document_id": "455000853",
                "fecha": "202309",
                "tipo": "CTA_AHORROS",
                "numero": "4332"
            }
        }
    ],
    "meta": {
        "total": 5,
        "filters": {"tipo": "CTA_AHORROS"}
    }
}
```

##### Obtener información de PDF

```python
response = await controller.get_pdf("Extracto_455000853_202309_CTA_AHORROS_4332.pdf")
```

##### Extraer texto

```python
response = await controller.extract_text(
    filename="Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
    password="optional_password"
)
```

**Response:**
```json
{
    "success": true,
    "message": "Text extracted successfully",
    "data": {
        "text": "Extracted text content...",
        "metadata": {
            "page_count": 3,
            "is_encrypted": false
        }
    },
    "meta": {
        "pages": 3,
        "is_encrypted": false
    }
}
```

##### Extraer tablas

```python
response = await controller.extract_tables(
    filename="Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
    password="optional_password"
)
```

##### Buscar en PDF

```python
response = await controller.search_in_pdf(
    filename="Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
    query="COMPRA",
    case_sensitive=False,
    password="optional_password"
)
```

**Response:**
```json
{
    "success": true,
    "message": "Found 15 match(es) in 2 page(s)",
    "data": {
        "query": "COMPRA",
        "total_matches": 15,
        "pages_with_matches": [1, 2],
        "matches": [...]
    },
    "meta": {
        "query": "COMPRA",
        "case_sensitive": false,
        "total_matches": 15,
        "pages_with_matches": 2
    }
}
```

##### Extraer cuenta de ahorros

```python
response = await controller.extract_savings_account(
    filename="Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
    password="optional_password"
)
```

**Response:**
```json
{
    "success": true,
    "message": "Savings account statement extracted successfully",
    "data": {
        "account_info": {
            "account_number": "4332",
            "account_type": "AHORROS",
            "holder": "Juan Pérez",
            "period": "2023-09"
        },
        "financial_summary": {
            "previous_balance": 1000000.0,
            "current_balance": 1500000.0,
            "total_deposits": 700000.0,
            "total_withdrawals": 200000.0
        },
        "transactions": [...]
    },
    "meta": {
        "account_number": "4332",
        "period": "2023-09",
        "transactions": 25
    }
}
```

##### Extraer tarjeta de crédito

```python
response = await controller.extract_credit_card(
    filename="Extracto_841756036_202505_TARJETA_MASTERCARD_1325.pdf",
    password="optional_password"
)
```

**Response:**
```json
{
    "success": true,
    "message": "Credit card statement extracted successfully",
    "data": {
        "card_info": {
            "card_number": "1325",
            "card_type": "MASTERCARD",
            "cardholder_name": "Juan Pérez"
        },
        "currencies": {
            "COP": {
                "transactions": [...],
                "balance_summary": {...}
            },
            "USD": {
                "transactions": [...],
                "balance_summary": {...}
            }
        }
    },
    "meta": {
        "card_number": "1325",
        "currencies": ["COP", "USD"],
        "total_transactions": 42
    }
}
```

##### Obtener metadata

```python
response = await controller.get_metadata(
    filename="Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
    password="optional_password"
)
```

---

### 2. FileController

Maneja operaciones de gestión de archivos.

#### Inicialización:

```python
from app.controllers import FileController

controller = FileController()
```

#### Métodos disponibles:

##### Copiar archivo

```python
response = await controller.copy_file(
    source="Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
    destination="backups/",
    overwrite=False
)
```

**Response:**
```json
{
    "success": true,
    "message": "File 'Extracto_455000853_202309_CTA_AHORROS_4332.pdf' copied successfully",
    "data": {
        "success": true,
        "operation": "copy",
        "source": "/data/Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
        "destination": "/backups/Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
        "message": "File copied successfully"
    },
    "meta": {
        "operation": "copy",
        "overwrite": false
    }
}
```

##### Mover archivo

```python
response = await controller.move_file(
    source="Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
    destination="archive/",
    overwrite=False
)
```

##### Renombrar archivo

```python
response = await controller.rename_file(
    source="Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
    new_name="Extracto_OLD_202309_CTA_AHORROS_4332.pdf",
    overwrite=False
)
```

##### Eliminar archivo

```python
response = await controller.delete_file(
    filename="Extracto_455000853_202309_CTA_AHORROS_4332.pdf"
)
```

##### Información de archivo

```python
response = await controller.get_file_info(
    filename="Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
    password="optional_password"
)
```

**Response:**
```json
{
    "success": true,
    "message": "File info retrieved for 'Extracto_455000853_202309_CTA_AHORROS_4332.pdf'",
    "data": {
        "filename": "Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
        "size_bytes": 245678,
        "size_mb": 0.23,
        "created_at": "2024-01-15T10:30:00",
        "modified_at": "2024-01-15T10:30:00",
        "is_encrypted": false,
        "page_count": 3
    },
    "meta": {
        "size_mb": 0.23,
        "is_encrypted": false
    }
}
```

##### Información de carpeta

```python
response = await controller.get_folder_info(password="optional_password")
```

**Response:**
```json
{
    "success": true,
    "message": "Folder contains 15 file(s)",
    "data": {
        "total_files": 15,
        "total_size_mb": 12.5,
        "encrypted_count": 0,
        "document_types": {
            "CTA_AHORROS": 8,
            "TARJETA_MASTERCARD": 6,
            "COMISIONES_CONSOLIDADAS": 1
        }
    },
    "meta": {
        "total_files": 15,
        "total_size_mb": 12.5,
        "encrypted_count": 0
    }
}
```

##### Organizar por tipo

```python
response = await controller.organize_by_type(
    base_folder="organized_by_type",
    dry_run=False
)
```

**Response:**
```json
{
    "success": true,
    "message": "PDFs organized by type",
    "data": {
        "summary": {
            "files_processed": 15,
            "files_moved": 15,
            "folders_created": 3,
            "errors": []
        }
    },
    "meta": {
        "files_processed": 15,
        "files_moved": 15,
        "folders_created": 3,
        "dry_run": false
    }
}
```

##### Organizar por año

```python
response = await controller.organize_by_year(
    base_folder="organized_by_year",
    dry_run=True  # Simular sin mover archivos
)
```

##### Obtener registro (inventario)

```python
response = await controller.get_registry(password="optional_password")
```

**Response:**
```json
{
    "success": true,
    "message": "Registry contains 15 file(s)",
    "data": {
        "total_files": 15,
        "total_size_mb": 12.5,
        "document_types": {
            "CTA_AHORROS": 8,
            "TARJETA_MASTERCARD": 6
        },
        "entries": [...]
    },
    "meta": {
        "total_files": 15,
        "total_size_mb": 12.5,
        "document_types": ["CTA_AHORROS", "TARJETA_MASTERCARD"]
    }
}
```

##### Exportar registro

```python
response = await controller.export_registry(
    output_path="registry.csv",
    format="csv",
    password="optional_password"
)
```

---

### 3. ExportController

Maneja operaciones de exportación de datos.

#### Inicialización:

```python
from app.controllers import ExportController

# Con password por defecto
controller = ExportController(password="secret")

# Sin password
controller = ExportController()
```

#### Métodos disponibles:

##### Exportar cuenta de ahorros

```python
# Exportar a Excel (por defecto)
response = await controller.export_savings_account(
    filename="Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
    export_format="excel",
    output_filename="cuenta_ahorros_sep2023.xlsx",
    password="optional_password",
    return_file=False  # True para devolver el archivo para descarga
)
```

**Response (JSON):**
```json
{
    "success": true,
    "message": "Data exported to 'cuenta_ahorros_sep2023.xlsx'",
    "data": {
        "source_file": "Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
        "output_file": "/data-extracted/cuenta_ahorros_sep2023.xlsx",
        "format": "excel",
        "record_count": 25,
        "sheets": ["Transacciones", "Resumen", "Cuenta"]
    },
    "meta": {
        "format": "excel",
        "record_count": 25,
        "sheets": ["Transacciones", "Resumen", "Cuenta"]
    }
}
```

**Con `return_file=True`**: Devuelve `FileResponse` para descarga directa.

##### Exportar tarjeta de crédito

```python
response = await controller.export_credit_card(
    filename="Extracto_841756036_202505_TARJETA_MASTERCARD_1325.pdf",
    export_format="excel",
    output_filename="tarjeta_may2025.xlsx",
    password="optional_password",
    return_file=False
)
```

##### Validar datos de cuenta de ahorros

```python
response = await controller.validate_savings_data(
    filename="Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
    password="optional_password"
)
```

**Response:**
```json
{
    "success": true,
    "message": "Data validation completed: valid",
    "data": {
        "is_valid": true,
        "record_count": 25,
        "errors": [],
        "warnings": []
    },
    "meta": {
        "is_valid": true,
        "record_count": 25,
        "errors": 0
    }
}
```

##### Validar datos de tarjeta de crédito

```python
response = await controller.validate_credit_card_data(
    filename="Extracto_841756036_202505_TARJETA_MASTERCARD_1325.pdf",
    password="optional_password"
)
```

##### Exportación en lote - Cuentas de ahorro

```python
response = await controller.batch_export_savings(
    filenames=[
        "Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
        "Extracto_508915065_202312_CTA_AHORROS_4332.pdf",
        "Extracto_560653133_202403_CTA_AHORROS_4332.pdf"
    ],
    export_format="excel",
    password="optional_password"
)
```

**Response:**
```json
{
    "success": true,
    "message": "Batch export completed: 3 successful, 0 failed",
    "data": {
        "successful": [
            {
                "source_file": "Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
                "output_file": "/data-extracted/Extracto_455000853_202309_CTA_AHORROS_4332.xlsx",
                "record_count": 25
            },
            ...
        ],
        "failed": []
    },
    "meta": {
        "total": 3,
        "successful_count": 3,
        "failed_count": 0,
        "format": "excel"
    }
}
```

##### Exportación en lote - Tarjetas de crédito

```python
response = await controller.batch_export_credit_cards(
    filenames=[
        "Extracto_841756036_202505_TARJETA_MASTERCARD_1325.pdf",
        "Extracto_844503341_202505_TARJETA_MASTERCARD_8324.pdf"
    ],
    export_format="excel",
    password="optional_password"
)
```

---

## 🔧 Uso con FastAPI Endpoints

### Ejemplo de integración en endpoints:

```python
from fastapi import APIRouter, Depends, Query
from typing import Optional

from app.controllers import PDFController
from app.core.dependencies import get_pdf_password

router = APIRouter(prefix="/api/v1/pdfs", tags=["PDFs"])

@router.get("/")
async def list_pdfs(
    tipo: Optional[str] = Query(None, description="Filter by document type"),
    fecha: Optional[str] = Query(None, description="Filter by date (YYYYMM)"),
    password: Optional[str] = Depends(get_pdf_password)
):
    """List all PDFs with optional filters."""
    controller = PDFController(password=password)
    return await controller.list_pdfs(tipo=tipo, fecha=fecha)

@router.get("/{filename}")
async def get_pdf(
    filename: str,
    password: Optional[str] = Depends(get_pdf_password)
):
    """Get PDF information."""
    controller = PDFController(password=password)
    return await controller.get_pdf(filename)

@router.post("/{filename}/extract-text")
async def extract_text(
    filename: str,
    password: Optional[str] = Depends(get_pdf_password)
):
    """Extract text from PDF."""
    controller = PDFController(password=password)
    return await controller.extract_text(filename, password)

@router.post("/{filename}/extract-savings")
async def extract_savings(
    filename: str,
    password: Optional[str] = Depends(get_pdf_password)
):
    """Extract savings account data."""
    controller = PDFController(password=password)
    return await controller.extract_savings_account(filename, password)
```

---

## 🎨 Formato de Respuestas

Todas las respuestas siguen el formato estándar definido en `app.core.responses.APIResponse`:

### Respuesta exitosa:
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": { ... },
    "meta": { ... }  // Opcional
}
```

### Respuesta de error:
```json
{
    "success": false,
    "error_code": "PDF_NOT_FOUND",
    "detail": "PDF 'filename.pdf' not found",
    "errors": [ ... ]  // Opcional
}
```

---

## 🚨 Manejo de Excepciones

Los controladores utilizan las excepciones definidas en `app.core.exceptions`:

- **PDFNotFoundError**: Cuando el PDF no existe
- **PDFPasswordError**: Cuando la contraseña es incorrecta
- **PDFParsingError**: Cuando falla la extracción/análisis
- **InvalidFilenameError**: Cuando el nombre del archivo es inválido
- **ConflictError**: Cuando hay un conflicto (ej: archivo ya existe)

### Ejemplo de manejo:

```python
from app.core.exceptions import PDFNotFoundError

@router.get("/{filename}")
async def get_pdf(filename: str):
    controller = PDFController()
    try:
        return await controller.get_pdf(filename)
    except PDFNotFoundError as e:
        # FastAPI manejará automáticamente la excepción
        # y devolverá el código HTTP 404 apropiado
        raise
```

---

## 📋 Utilidades Core Disponibles

Los controladores tienen acceso a todas las utilidades del paquete `core`:

### 1. Responses (`app.core.responses`)
- `APIResponse.success()` - Respuesta exitosa (200)
- `APIResponse.created()` - Recurso creado (201)
- `APIResponse.accepted()` - Aceptado para procesamiento (202)
- `APIResponse.no_content()` - Sin contenido (204)
- `APIResponse.error()` - Error genérico

### 2. Decorators (`app.core.decorators`)
- `@log_endpoint` - Logging automático de endpoints
- `@validate_filename` - Validación de nombres de archivo
- `@require_password` - Requiere contraseña
- `@cache_response` - Cache de respuestas

### 3. Dependencies (`app.core.dependencies`)
- `get_pdf_password()` - Obtener contraseña de PDF
- `require_pdf_password()` - Requerir contraseña
- `get_pagination_params()` - Parámetros de paginación
- `get_sort_params()` - Parámetros de ordenamiento

---

## 💡 Mejores Prácticas

1. **Siempre usar APIResponse**: Mantiene consistencia en todas las respuestas
2. **Delegar lógica a servicios**: Controladores solo manejan HTTP
3. **Usar excepciones del core**: Mapeo automático a códigos HTTP
4. **Incluir metadata relevante**: Ayuda a los clientes de la API
5. **Logging apropiado**: Los servicios ya tienen logging, no duplicar
6. **Password handling**: Usar dependencias de FastAPI para passwords

---

## 🔄 Flujo de Datos

```
1. Request HTTP
   ↓
2. FastAPI Endpoint
   ↓
3. Dependency Injection (password, pagination, etc.)
   ↓
4. Controller Method
   ↓
5. Service Method (lógica de negocio)
   ↓
6. Core Logic (pdf_analyzer, data_processor)
   ↓
7. Response (APIResponse wrapper)
   ↓
8. JSON Response HTTP
```

---

## 📖 Próximos Pasos

1. Crear endpoints FastAPI que usen estos controladores
2. Implementar tests para los controladores
3. Agregar documentación OpenAPI/Swagger
4. Implementar rate limiting y caching
5. Agregar autenticación si es necesaria

---

## 🤝 Contribución

Al agregar nuevos controladores:

1. Heredar patrones de controladores existentes
2. Usar `APIResponse` para todas las respuestas
3. Delegar lógica a servicios
4. Incluir metadata relevante en respuestas
5. Documentar con docstrings completos
6. Manejar excepciones apropiadamente
