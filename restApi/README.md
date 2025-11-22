# PDF Analyzer REST API

REST API built with FastAPI for analyzing Colombian bank statement PDFs.

## Features

- 🚀 Built with FastAPI (latest version)
- 📚 Automatic interactive API documentation (Swagger UI)
- 🔄 Auto-reload during development
- ✅ Request/response validation with Pydantic
- 🌐 CORS support
- 🏥 Health check endpoints

## Installation

### 1. Install dependencies

Desde la raíz del proyecto:

```bash
pip install -r requirements.txt
```

Las dependencias de FastAPI están incluidas en el `requirements.txt` principal del proyecto.

### 2. Configure environment (optional)

```bash
cd restApi
cp .env.example .env
# Edita .env con tu configuración
```

**Importante**: El archivo `.env` debe estar en la carpeta `restApi/`, no en la raíz del proyecto.

Variables de entorno disponibles:
- `API_TITLE`: Título de la API (default: "PDF Analyzer API")
- `API_VERSION`: Versión de la API (default: "1.0.0")
- `HOST`: Host del servidor (default: "0.0.0.0")
- `PORT`: Puerto del servidor (default: 8000)
- `RELOAD`: Auto-reload en desarrollo (default: true)
- `LOG_LEVEL`: Nivel de logs (default: "info")
- `ENVIRONMENT`: Entorno (default: "development")
- `CORS_ORIGINS`: Orígenes CORS permitidos (default: "*")
- `PDF_PASSWORD`: Contraseña para PDFs encriptados

## Running the API

### Development mode (with auto-reload)

Desde la carpeta `restApi/`:

```bash
cd restApi
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Available Endpoints

### Root & Health

- `GET /` - API information
- `GET /health` - Health check

### API v1

- `GET /api/v1/info` - API information and available endpoints

## Development

The API is structured to be extended with additional endpoints for:

- PDF document listing
- PDF text extraction
- Bank statement analysis
- Transaction data extraction
- File management operations

## Project Structure

```
restApi/
├── main.py                  # FastAPI entry point
├── app/                     # Application package
│   ├── core/               # Core configuration
│   │   ├── config.py       # Settings
│   │   └── __init__.py
│   ├── api/                # API endpoints
│   │   └── v1/            # API version 1
│   │       ├── router.py   # Main router
│   │       └── endpoints/  # Endpoint modules
│   │           ├── health.py
│   │           └── system.py
│   ├── schemas/            # Pydantic schemas
│   │   └── common.py
│   ├── services/           # Business logic
│   ├── models/             # Database models (future)
│   └── README.md           # App structure docs
├── scripts/
│   └── test_config.py      # Configuration test script
├── .env.example            # Environment configuration example
├── .env                    # Your local config (not in git)
├── .gitignore              # Git ignore file
└── README.md               # This file
```

**Architecture**:
- **Modular**: Separación clara de responsabilidades
- **Versionado**: API v1 con posibilidad de v2, v3, etc.
- **Escalable**: Fácil agregar nuevos endpoints y servicios
- **Clean**: Siguiendo principios SOLID y mejores prácticas de FastAPI

Ver `app/README.md` para detalles de la estructura interna.

**Note**: 
- Las dependencias de FastAPI están en el `requirements.txt` principal del proyecto.
- El archivo `.env` debe estar en la carpeta `restApi/` (será ignorado por git).

## Next Steps

1. Add routers for different API modules (documents, analysis, etc.)
2. Integrate with the PDF analyzer library
3. Add authentication/authorization
4. Implement database for storing results
5. Add background tasks for long-running operations
6. Configure production deployment settings

## Testing

```bash
# Test the configuration
cd restApi
python scripts/test_config.py

# Test the API is running
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

## License

Same as parent project.
