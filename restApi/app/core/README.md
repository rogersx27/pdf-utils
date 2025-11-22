# Core Package - Guía de Uso

Este paquete contiene los componentes fundamentales de la API REST del PDF Analyzer. Está diseñado para proporcionar una base sólida y consistente para todos los endpoints.

## 📁 Estructura

```
app/core/
├── __init__.py          # Exportaciones del paquete
├── config.py            # Configuración y settings
├── exceptions.py        # Excepciones personalizadas
├── responses.py         # Utilidades de respuesta HTTP
├── middleware.py        # Middleware personalizado
├── decorators.py        # Decoradores para endpoints
└── dependencies.py      # Dependencias FastAPI reutilizables
```

## 🎯 Componentes Principales

### 1. Excepciones (`exceptions.py`)

Define excepciones personalizadas con códigos HTTP apropiados.

#### Uso básico:

```python
from app.core import PDFNotFoundError, PDFPasswordError, InvalidFilenameError

@router.get("/pdf/{filename}")
async def get_pdf(filename: str):
    if not pdf_exists(filename):
        raise PDFNotFoundError(filename)
    
    if needs_password and not password:
        raise PDFPasswordError("Password required")
    
    return {"status": "ok"}
```

#### Excepciones disponibles:

**Errores de Cliente (4xx):**
- `BadRequestError` - Petición mal formada
- `UnauthorizedError` - Autenticación requerida
- `ForbiddenError` - Sin permisos
- `NotFoundError` - Recurso no encontrado
- `ConflictError` - Conflicto con estado actual
- `UnprocessableEntityError` - Entidad no procesable

**Errores específicos de PDF:**
- `PDFNotFoundError` - PDF no encontrado
- `PDFPasswordError` - Error de contraseña
- `PDFParsingError` - Error al parsear PDF
- `InvalidPDFFormatError` - Formato inválido
- `InvalidFilenameError` - Nombre de archivo inválido

**Errores de Servidor (5xx):**
- `InternalServerError` - Error interno
- `ServiceUnavailableError` - Servicio no disponible
- `ExtractionError` - Error en extracción
- `ValidationError` - Error de validación

### 2. Respuestas (`responses.py`)

Proporciona respuestas HTTP estandarizadas.

#### Uso básico:

```python
from app.core import APIResponse, success_response, paginated_response

@router.get("/pdfs")
async def list_pdfs():
    pdfs = get_all_pdfs()
    
    # Respuesta simple de éxito
    return success_response(
        data=pdfs,
        message="PDFs retrieved successfully"
    )

@router.get("/pdfs/paginated")
async def list_pdfs_paginated(page: int = 1, page_size: int = 20):
    pdfs, total = get_pdfs_page(page, page_size)
    
    # Respuesta paginada
    return paginated_response(
        data=pdfs,
        page=page,
        page_size=page_size,
        total=total
    )

@router.post("/pdf")
async def create_pdf(data: dict):
    result = create_new_pdf(data)
    
    # Respuesta 201 Created
    return APIResponse.created(
        data=result,
        message="PDF created successfully"
    )
```

#### Métodos disponibles:

- `APIResponse.success()` - Respuesta exitosa (200)
- `APIResponse.created()` - Recurso creado (201)
- `APIResponse.accepted()` - Aceptado para procesamiento (202)
- `APIResponse.no_content()` - Sin contenido (204)
- `APIResponse.error()` - Error genérico
- `APIResponse.bad_request()` - Bad request (400)
- `APIResponse.unauthorized()` - No autorizado (401)
- `APIResponse.forbidden()` - Prohibido (403)
- `APIResponse.not_found()` - No encontrado (404)
- `APIResponse.internal_server_error()` - Error interno (500)

### 3. Middleware (`middleware.py`)

Middleware personalizado para procesamiento de peticiones/respuestas.

Los middlewares están **pre-configurados** en `main.py` en el orden correcto:

1. **ErrorHandlerMiddleware** - Captura todas las excepciones
2. **RequestLoggingMiddleware** - Registra todas las peticiones/respuestas
3. **CORSHeadersMiddleware** - Añade headers CORS personalizados
4. **RequestIDMiddleware** - Genera ID único por petición

No necesitas configurarlos, funcionan automáticamente.

### 4. Decoradores (`decorators.py`)

Decoradores útiles para endpoints.

#### `@log_endpoint` - Registra ejecución:

```python
from app.core import log_endpoint

@router.get("/expensive")
@log_endpoint
async def expensive_operation():
    # Se registrará inicio, fin y tiempo de ejecución
    return process_data()
```

#### `@require_password()` - Requiere contraseña:

```python
from app.core import require_password

@router.post("/analyze")
@require_password(from_query=True, from_header=True)
async def analyze_pdf(request: Request, password: str = None):
    # password se extraerá automáticamente del header o query
    return analyze_with_password(password)
```

#### `@validate_filename_format()` - Valida formato de nombre:

```python
from app.core import validate_filename_format

@router.get("/pdf/{filename}")
@validate_filename_format(param_name="filename")
async def get_pdf(filename: str):
    # El nombre ya está validado
    return get_pdf_data(filename)
```

#### `@cache_response()` - Cachea respuestas:

```python
from app.core import cache_response

@router.get("/stats")
@cache_response(ttl_seconds=300)  # 5 minutos
async def get_stats():
    # Resultado se cachea por 5 minutos
    return calculate_expensive_stats()
```

#### `@handle_not_found()` - Convierte None a 404:

```python
from app.core import handle_not_found

@router.get("/pdf/{id}")
@handle_not_found(resource_name="PDF")
async def get_pdf_by_id(id: str):
    # Si retorna None, se lanzará NotFoundError automáticamente
    return find_pdf_by_id(id)
```

#### `@timing_decorator` - Mide tiempo de ejecución:

```python
from app.core import timing_decorator

@router.get("/process")
@timing_decorator
async def process_data():
    # Se registrará el tiempo de ejecución
    return heavy_processing()
```

### 5. Dependencias (`dependencies.py`)

Dependencias reutilizables de FastAPI (patrón Dependency Injection).

#### Password handling:

```python
from app.core import OptionalPasswordDep, RequiredPasswordDep

@router.post("/analyze")
async def analyze(password: RequiredPasswordDep):
    # password es obligatorio y ya viene validado
    return analyze_pdf(password)

@router.get("/read")
async def read(password: OptionalPasswordDep):
    # password es opcional
    return read_pdf(password)
```

#### Paginación:

```python
from app.core import PaginationDep

@router.get("/pdfs")
async def list_pdfs(pagination: PaginationDep):
    # pagination.page, pagination.page_size, pagination.offset
    return get_paginated_pdfs(pagination.offset, pagination.page_size)
```

#### Ordenamiento:

```python
from app.core import SortingDep

@router.get("/pdfs")
async def list_pdfs(sort: SortingDep):
    # sort.sort_by, sort.sort_order
    return get_sorted_pdfs(sort.sort_by, sort.sort_order)
```

#### Validación de archivos:

```python
from app.core import PDFPathDep

@router.get("/pdf/{filename}")
async def get_pdf(pdf_path: PDFPathDep):
    # pdf_path ya está validado y existe
    return read_pdf_from_path(pdf_path)
```

#### Request ID y Client Info:

```python
from app.core import RequestIDDep, ClientInfoDep

@router.post("/process")
async def process(request_id: RequestIDDep, client: ClientInfoDep):
    # request_id: ID único de la petición
    # client: {"host": "...", "user_agent": "...", ...}
    log_request(request_id, client)
    return {"processed": True}
```

## 📝 Schemas (`app/schemas/common.py`)

### Schemas base:

```python
from app.schemas import BaseSchema

class MyCustomSchema(BaseSchema):
    name: str
    value: int
    # Hereda configuración consistente
```

### Respuestas envueltas:

```python
from app.schemas import SuccessResponse

@router.get("/data", response_model=SuccessResponse[MyDataSchema])
async def get_data():
    return success_response(
        data=my_data,
        message="Data retrieved"
    )
```

### Paginación en schemas:

```python
from app.schemas import PaginatedResponse, PaginationParams

@router.get("/items", response_model=PaginatedResponse[ItemSchema])
async def get_items(pagination: PaginationParams):
    items, total = get_items_page(pagination.page, pagination.page_size)
    return paginated_response(
        data=items,
        page=pagination.page,
        page_size=pagination.page_size,
        total=total
    )
```

## 🎨 Ejemplo Completo: Endpoint con Todas las Características

```python
from fastapi import APIRouter
from app.core import (
    log_endpoint,
    validate_filename_format,
    PDFPathDep,
    RequiredPasswordDep,
    success_response,
    PDFParsingError
)
from app.schemas import BaseSchema

router = APIRouter()

class AnalysisResult(BaseSchema):
    filename: str
    pages: int
    transactions: list[dict]

@router.post("/analyze/{filename}")
@log_endpoint  # Registra ejecución
@validate_filename_format(param_name="filename")  # Valida nombre
async def analyze_pdf(
    pdf_path: PDFPathDep,  # Path validado y existe
    password: RequiredPasswordDep  # Password obligatorio
):
    """
    Analiza un PDF bancario.
    
    - Valida nombre de archivo automáticamente
    - Requiere password
    - Registra tiempo de ejecución
    - Maneja errores automáticamente
    """
    try:
        result = perform_analysis(pdf_path, password)
        
        return success_response(
            data=result,
            message="PDF analyzed successfully"
        )
        
    except Exception as e:
        raise PDFParsingError(f"Failed to analyze PDF: {str(e)}")
```

## 🚀 Mejores Prácticas

1. **Usa las excepciones personalizadas** en lugar de HTTPException genérica
2. **Usa APIResponse** para respuestas consistentes
3. **Usa dependencias** en lugar de duplicar validaciones
4. **Usa decoradores** para funcionalidades transversales
5. **Hereda de BaseSchema** para todos tus schemas
6. **Registra operaciones** con los decoradores de logging

## 📊 Estructura de Respuestas

### Respuesta Exitosa:
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { /* your data */ },
  "meta": { /* optional metadata */ }
}
```

### Respuesta de Error:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": [ /* optional error details */ ]
  }
}
```

### Respuesta Paginada:
```json
{
  "success": true,
  "message": "Success",
  "data": [ /* items */ ],
  "meta": {
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 100,
      "total_pages": 5,
      "has_next": true,
      "has_previous": false
    }
  }
}
```

---

Con esta base, puedes crear endpoints robustos sin preocuparte por:
✅ Manejo de errores
✅ Formato de respuestas
✅ Validaciones comunes
✅ Logging
✅ CORS y headers
✅ Request IDs
✅ Excepciones HTTP correctas
