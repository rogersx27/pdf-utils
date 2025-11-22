# App Structure - FastAPI Application

Estructura modular de la aplicación FastAPI siguiendo mejores prácticas.

## 📁 Estructura de Carpetas

```
app/
├── __init__.py              # Package initialization
├── core/                    # Configuración central
│   ├── __init__.py
│   └── config.py           # Settings y configuración
├── api/                     # Endpoints de la API
│   ├── __init__.py
│   └── v1/                 # API versión 1
│       ├── __init__.py
│       ├── router.py       # Router principal v1
│       └── endpoints/      # Endpoints organizados por dominio
│           ├── __init__.py
│           ├── health.py   # Endpoints de health check
│           └── system.py   # Endpoints de información del sistema
├── schemas/                 # Pydantic schemas (request/response)
│   ├── __init__.py
│   └── common.py           # Schemas comunes
├── models/                  # Database models (futuro)
│   └── __init__.py
└── services/               # Lógica de negocio
    └── __init__.py
```

## 🎯 Responsabilidades por Carpeta

### `core/`
- **Propósito**: Configuración central y utilidades compartidas
- **Contenido**: Settings, constantes, configuración de la app
- **Ejemplo**: `config.py` con clase `Settings`

### `api/`
- **Propósito**: Definición de endpoints REST
- **Contenido**: Routers y endpoints organizados por versión
- **Patrón**: Versionado de API (`v1/`, `v2/`, etc.)

### `api/v1/endpoints/`
- **Propósito**: Endpoints específicos agrupados por dominio
- **Contenido**: Archivos por funcionalidad (health, pdf, documents, etc.)
- **Ejemplo**: 
  - `health.py` - Health checks
  - `system.py` - Info del sistema
  - `pdfs.py` - Operaciones con PDFs (futuro)
  - `analysis.py` - Análisis de documentos (futuro)

### `schemas/`
- **Propósito**: Modelos Pydantic para validación
- **Contenido**: Request/Response schemas
- **Ventaja**: Separación entre modelos de API y modelos de BD

### `services/`
- **Propósito**: Lógica de negocio
- **Contenido**: Clases que implementan operaciones
- **Ejemplo futuro**: 
  - `pdf_service.py` - Interacción con pdf_analyzer
  - `extraction_service.py` - Extracción de datos

### `models/`
- **Propósito**: Modelos de base de datos (si se necesita)
- **Contenido**: SQLAlchemy/Tortoise models (futuro)
- **Uso**: Persistencia de datos si se agrega BD

## 🔄 Flujo de una Request

```
main.py (FastAPI app)
    ↓
api/v1/router.py (incluye routers)
    ↓
api/v1/endpoints/health.py (endpoint específico)
    ↓
schemas/common.py (validación request/response)
    ↓
services/pdf_service.py (lógica de negocio)
    ↓
../../src/pdf_analyzer (librería del proyecto)
```

## 📝 Convenciones

1. **Naming**:
   - Endpoints files: `plural_noun.py` (e.g., `pdfs.py`, `documents.py`)
   - Schemas: `{Entity}{Action}Schema` (e.g., `PDFUploadSchema`)
   - Services: `{Entity}Service` (e.g., `PDFService`)

2. **Imports**:
   - Usar imports absolutos desde `app.*`
   - Ejemplo: `from app.core.config import settings`

3. **Tags**:
   - Agrupar endpoints con tags en routers
   - Tags descriptivos: `["Health"]`, `["PDFs"]`, `["Analysis"]`

## 🚀 Próximos Pasos

1. **Agregar endpoints de PDFs**:
   - `GET /api/v1/pdfs` - Listar PDFs
   - `GET /api/v1/pdfs/{id}` - Obtener PDF info
   - `POST /api/v1/pdfs/analyze` - Analizar PDF

2. **Crear servicios**:
   - `services/pdf_service.py` - Integrar con `pdf_analyzer`
   - `services/extraction_service.py` - Extracción de datos

3. **Agregar schemas específicos**:
   - `schemas/pdf.py` - Schemas para operaciones PDF
   - `schemas/analysis.py` - Schemas para análisis

4. **Middleware** (opcional):
   - `core/middleware.py` - Custom middleware
   - Logging, autenticación, etc.
