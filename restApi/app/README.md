# App Structure - FastAPI Application

Estructura modular de la aplicación FastAPI siguiendo mejores prácticas y patrón de controladores delgados.

## 📁 Estructura de Carpetas

```
app/
├── __init__.py              # Package initialization
├── main.py                  # FastAPI application entry point
├── core/                    # Configuración central
│   ├── __init__.py
│   ├── config.py           # Settings y configuración (BaseSettings)
│   └── exceptions.py       # Excepciones personalizadas de API
├── api/                     # Endpoints de la API
│   ├── __init__.py
│   └── v1/                 # API versión 1
│       ├── __init__.py
│       ├── router.py       # Router principal v1
│       └── endpoints/      # Endpoints organizados por dominio
│           ├── __init__.py
│           ├── health.py   # Health check endpoints
│           ├── system.py   # System info endpoints
│           ├── pdfs.py     # PDF operations endpoints
│           ├── analysis.py # PDF analysis endpoints
│           ├── extraction.py   # Data extraction endpoints
│           └── files.py    # File management endpoints
├── schemas/                 # Pydantic schemas (request/response)
│   ├── __init__.py
│   ├── common.py           # Schemas comunes (HealthResponse, SystemInfo)
│   ├── pdf_analyzer.py     # Schemas para PDF analysis
│   └── file_operations.py  # Schemas para file operations
├── services/               # Controladores de servicios (thin controllers)
│   ├── __init__.py
│   ├── pdf_analyzer_service.py    # Controller for pdf_analyzer module
│   ├── data_processor_service.py  # Controller for data_processor module
│   └── file_manager_service.py    # Controller for file_manager module
└── models/                  # Database models
    └── __init__.py
```

## 🎯 Responsabilidades por Carpeta

### `core/`
- **Propósito**: Configuración central, constantes y excepciones
- **Contenido**: 
  - `config.py` - Settings con Pydantic BaseSettings
  - `exceptions.py` - Excepciones personalizadas (PDFNotFoundError, PDFPasswordError, etc.)
- **Uso**: Configuración compartida por toda la aplicación

### `api/`
- **Propósito**: Definición de endpoints REST
- **Contenido**: Routers y endpoints organizados por versión
- **Patrón**: Versionado de API (`v1/`, `v2/`, etc.)
- **Arquitectura**: Thin controllers que delegan a services

### `api/v1/endpoints/`
- **Propósito**: Endpoints específicos agrupados por dominio
- **Contenido**: Archivos por funcionalidad
- **Endpoints Implementados**: 
  - `health.py` - Health checks y liveness probes
  - `system.py` - Información del sistema
  - `pdfs.py` - Listado y consulta de PDFs (usa PDFAnalyzerService)
  - `analysis.py` - Análisis de PDFs (texto, tablas, metadata, búsqueda)
  - `extraction.py` - Extracción de datos estructurados (savings/credit card)
  - `files.py` - Operaciones de archivos (copy, move, rename, delete, organize)

### `schemas/`
- **Propósito**: Modelos Pydantic para validación y serialización
- **Contenido**: Request/Response schemas
- **Ventaja**: Separación entre modelos de API y modelos de dominio
- **Archivos**:
  - `common.py` - Schemas comunes (HealthResponse, SystemInfo)
  - `pdf_analyzer.py` - Schemas para PDF analysis (PDFDocumentSchema, TextExtractionResultSchema, etc.)
  - `file_operations.py` - Schemas para file operations (FileOperationResponse, OrganizationResultSchema, etc.)

### `services/`
- **Propósito**: Controladores delgados (thin controllers)
- **Arquitectura**: Patrón de delegación a módulos de negocio
- **Responsabilidades**:
  1. Validación de rutas y paths
  2. Mapeo de excepciones a errores HTTP
  3. Conversión de modelos de dominio a schemas de API
  4. Delegación completa de lógica de negocio
- **Servicios Implementados**:
  - `pdf_analyzer_service.py` - Delega a `pdf_analyzer` (extract_text, get_metadata, search_in_pdf, etc.)
  - `data_processor_service.py` - Delega a `data_processor` (SavingsAccountProcessor, CreditCardProcessor)
  - `file_manager_service.py` - Delega a `pdf_analyzer.file_manager` (copy_pdf, move_pdf, PDFOrganizer, etc.)

## 🔄 Flujo de una Request

```
main.py (FastAPI app)
    ↓
api/v1/router.py (incluye routers de endpoints)
    ↓
api/v1/endpoints/analysis.py (endpoint específico)
    ↓
schemas/pdf_analyzer.py (validación request/response con Pydantic)
    ↓
services/pdf_analyzer_service.py (thin controller - validación y mapeo)
    ↓
../../src/pdf_analyzer (módulo de negocio - lógica real)
    ↓
    ├─► extract_text() - Funciones de conveniencia
    ├─► get_metadata()
    ├─► search_in_pdf()
    └─► SavingsAccountExtractor - Extractores especializados
```

## 🏗️ Arquitectura de Servicios (Patrón de Delegación)

Los servicios en `app/services/` son **controladores delgados** que NO implementan lógica de negocio. Su única responsabilidad es:

```
┌─────────────────────────────────────────────────┐
│         FastAPI Endpoints (API Layer)           │
│  - Routing                                      │
│  - HTTP handling                                │
│  - Request validation (Pydantic)                │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│      Service Controllers (Thin Layer)           │
│  - Path validation                              │
│  - Exception mapping (Domain → HTTP)            │
│  - Schema conversion (Domain → API)             │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│    Business Logic Modules (../../src/)          │
│  - pdf_analyzer (core PDF operations)           │
│  - data_processor (data extraction & export)    │
│  - file_manager (file operations)               │
└─────────────────────────────────────────────────┘
```

### Ejemplo de Delegación:

```python
# ❌ ANTES (duplicación de lógica)
class PDFService:
    def extract_text(self, path):
        # Implementación directa con pypdf
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

# ✅ AHORA (delegación completa)
class PDFAnalyzerService:
    def extract_text(self, filename):
        # Step 1: Validate path
        pdf_path = settings.data_dir / filename
        if not pdf_path.exists():
            raise PDFNotFoundError(filename)
        
        # Step 2: Delegate to pdf_analyzer
        text = extract_text(pdf_path, password=self.password)
        
        # Step 3: Convert to API schema
        return TextExtractionResultSchema(text=text, ...)
```

## 📝 Convenciones

1. **Naming**:
   - Endpoints files: `plural_noun.py` (e.g., `pdfs.py`, `files.py`)
   - Schemas: `{Entity}{Type}Schema` (e.g., `PDFDocumentSchema`, `TextExtractionResultSchema`)
   - Services: `{Module}Service` (e.g., `PDFAnalyzerService`, `FileManagerService`)
   - Exceptions: `{Error}Error` (e.g., `PDFNotFoundError`, `PDFPasswordError`)

2. **Imports**:
   - API imports: Usar imports absolutos desde `app.*`
   - Ejemplo: `from app.core.config import settings`
   - Módulos de negocio: Agregar `src/` a sys.path en services
   - Ejemplo: `from pdf_analyzer import extract_text`

3. **Tags** (para Swagger/OpenAPI):
   - Agrupar endpoints con tags descriptivos
   - Tags implementados: `["Health"]`, `["System"]`, `["PDFs"]`, `["Analysis"]`, `["Extraction"]`, `["File Operations"]`

4. **Error Handling**:
   - Excepciones personalizadas en `core/exceptions.py`
   - Mapeo consistente en services:
     - Domain exceptions → API HTTP exceptions
     - Logging de errores antes de lanzar excepciones

5. **Documentation**:
   - Docstrings detallados en servicios explicando delegación
   - Workflow en pasos numerados (Step 1, Step 2, etc.)
   - Especificar qué función/módulo se usa para cada operación

## 🚀 Endpoints Implementados

### Health & System
- `GET /health` - Health check básico
- `GET /health/detailed` - Health check detallado con métricas
- `GET /system/info` - Información del sistema

### PDF Operations
- `GET /api/v1/pdfs` - Listar todos los PDFs
- `GET /api/v1/pdfs/{filename}` - Obtener información de un PDF específico

### PDF Analysis
- `POST /api/v1/analysis/text` - Extraer texto de PDF
- `POST /api/v1/analysis/tables` - Extraer tablas de PDF
- `POST /api/v1/analysis/metadata` - Obtener metadatos de PDF
- `POST /api/v1/analysis/search` - Buscar texto en PDF

### Data Extraction
- `POST /api/v1/extraction/savings` - Extraer datos de cuenta de ahorros
- `POST /api/v1/extraction/credit-card` - Extraer datos de tarjeta de crédito
- `POST /api/v1/extraction/export-savings` - Exportar datos de ahorros (CSV/Excel)
- `POST /api/v1/extraction/export-credit-card` - Exportar datos de tarjeta (CSV/Excel)

### File Operations
- `POST /api/v1/files/copy` - Copiar archivo
- `POST /api/v1/files/move` - Mover archivo
- `POST /api/v1/files/rename` - Renombrar archivo
- `DELETE /api/v1/files/{filename}` - Eliminar archivo
- `GET /api/v1/files/{filename}/info` - Información de archivo
- `GET /api/v1/files/folder/info` - Información de carpeta
- `POST /api/v1/files/organize/by-type` - Organizar PDFs por tipo
- `POST /api/v1/files/organize/by-year` - Organizar PDFs por año
- `GET /api/v1/files/registry` - Obtener inventario de PDFs

## 🔗 Integración con Módulos de Negocio

La API integra tres módulos principales del proyecto:

### 1. `pdf_analyzer` (../../src/pdf_analyzer/)
- **Funciones de conveniencia**: `extract_text()`, `extract_tables()`, `get_metadata()`, `search_in_pdf()`
- **Repository**: `LocalPDFRepository` para gestión de documentos
- **Extractores**: `SavingsAccountExtractor`, `CreditCardExtractor`
- **File Manager**: `copy_pdf()`, `move_pdf()`, `PDFOrganizer`, `PDFRegistry`

### 2. `data_processor` (../../src/data_processor/)
- **Procesadores**: `SavingsAccountProcessor`, `CreditCardProcessor`
- **Funcionalidad**: Extracción y exportación de datos a CSV/Excel/Markdown
- **Validación**: Validación de consistencia de datos bancarios

### 3. `logger` (../../src/logger/)
- **Sistema de logs**: Logging jerárquico con niveles configurables
- **Handlers**: File handlers con rotación por fecha, console handlers con colores
- **Configuración**: Variables de entorno para control de niveles de log

## 🛠️ Desarrollo y Testing

### Ejecutar la API

```bash
# Activar entorno virtual
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
cd restApi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Acceder a la documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Testing

```bash
# Ejecutar tests (cuando se implementen)
pytest tests/

# Con cobertura
pytest --cov=app tests/
```

## 🔮 Próximos Pasos

### Funcionalidades Pendientes

1. **Autenticación y Autorización**:
   - JWT tokens para autenticación
   - Rate limiting
   - API keys para acceso programático

2. **Batch Operations**:
   - Procesamiento de múltiples PDFs en paralelo
   - Queue system para operaciones largas
   - Webhooks para notificaciones

3. **Storage**:
   - Integración con cloud storage (S3, Azure Blob)
   - Upload directo de PDFs vía API
   - Generación de URLs firmadas

4. **Reporting**:
   - Endpoints para reportes consolidados
   - Exportación de datos agregados
   - Dashboards y visualizaciones

5. **Monitoring**:
   - Prometheus metrics
   - Health checks avanzados
   - Performance monitoring

### Mejoras de Arquitectura

1. **Dependency Injection**:
   - FastAPI dependency injection para services
   - Mejor testabilidad y mantenimiento

2. **Caching**:
   - Redis para cacheo de resultados
   - Cache invalidation strategies

3. **Background Tasks**:
   - Celery para tareas asíncronas
   - Progress tracking para operaciones largas

4. **Database** (opcional):
   - Persistencia de resultados de análisis
   - Histórico de operaciones
   - SQLAlchemy ORM

## 📚 Recursos Adicionales

- **Documentación de pdf_analyzer**: `../../docs/pdf_analyzer_api.md`
- **Guía de Bancolombia Extractor**: `../../docs/BANCOLOMBIA_EXTRACTOR_GUIDE.md`
- **Guía de Data Processor**: `../../docs/DATA_PROCESSOR_GUIDE.md`
- **Configuración de Logging**: `../../docs/LOGGING_CONFIGURATION.md`
