# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PDF Analyzer is a Python library for analyzing Colombian bank statement PDFs (extractos bancarios). It parses PDF filenames following a specific naming convention (`Extracto_{id}_{fecha}_{tipo}_{numero}.pdf`) and provides services for reading, analyzing, organizing, and extracting structured data from PDF documents.

## Architecture

The project follows a Repository pattern with layered architecture:

### src/pdf_analyzer/
- **models/**: Domain entities and dataclasses
  - `PDFDocument`, `PDFDocumentInfo`: PDF document representation with parsed filename info
  - `Transaction`, `AccountSummary`: Base transaction models
  - `TableInfo`, `Section`: Extraction structure models
  - `AccountInfo`, `FinancialSummary`, `SavingsTransaction`, `SavingsAccountStatement`: Savings account models
  - `CardInfo`, `CreditLimit`, `InterestRates`, `BalanceSummary`, `MinimumPayment`, `CreditCardTransaction`, `CurrencyStatement`, `CreditCardStatement`: Credit card models
- **concerns/**: Reusable mixins for shared behavior
  - `PathResolvableMixin`: Document path resolution (`_resolve_path()`)
  - `PasswordAwareMixin`: Password handling (`_init_password()`, `get_default_password()`)
  - `CacheableMixin`: Caching operations (`_get_cached()`, `_set_cached()`, `clear_cache()`)
  - `Serializable`: Protocol for `to_dict()` method
- **repositories/**: Data access layer (`LocalPDFRepository`) - manages PDF files in the filesystem with caching
- **services/**: Business logic
  - `ReaderService`: Text/table extraction using pypdf and pdfplumber
  - `AnalyzerService`: Analysis operations with caching (search, compare)
  - `SecurityService`: Password operations (add/remove encryption)
  - **extractors/**: Specialized data extractors
    - `ExtractorService`: Base explorer for PDF structure analysis
    - `BancolombiaExtractor`: Core engine for Bancolombia-specific PDF parsing
    - `SavingsAccountExtractor`: Extracts savings account data
    - `CreditCardExtractor`: Extracts credit card data (multi-currency support)
  - **parsers/**: Parsing utilities
    - `NumberParser`: Dual format number parsing (US/Colombian)
    - `parse_currency()`: Currency string to float conversion
- **file_manager/**: File operations (`FileOperations`, `PDFOrganizer`, `PDFRegistry`) - copy/move/rename, organize by type/year, export inventories

### src/data_processor/
Pandas-based processors for converting extracted data to DataFrames with validation and multi-format export:
- `SavingsAccountProcessor`: Process savings account statements
- `CreditCardProcessor`: Process credit card statements (multi-currency support)

### src/logger/
Logging system with date-based file handlers, colored console output, and pretty formatting functions.

### restApi/
REST API built with FastAPI exposing pdf_analyzer functionality via HTTP endpoints.

- **app/core/**: Central configuration and utilities
  - `config.py`: Settings with Pydantic BaseSettings
  - `exceptions.py`: Custom HTTP exceptions (PDFNotFoundError, PDFPasswordError, etc.)
  - `responses.py`: Standardized API responses (APIResponse.success(), paginated_response())
  - `middleware.py`: Error handling, request logging, CORS, request ID
  - `decorators.py`: Endpoint utilities (@log_endpoint, @validate_filename_format, @cache_response)
  - `dependencies.py`: FastAPI dependencies (OptionalPasswordDep, PaginationDep, PDFPathDep)
- **app/api/v1/**: API version 1 endpoints (direct endpoint logic)
- **app/api/v2/**: API version 2 endpoints (controller-based architecture)
  - `endpoints/pdfs.py`: PDF operations (list, get, extract text/tables, search)
  - `endpoints/files.py`: File management (copy, move, rename, delete, organize)
  - `endpoints/exports.py`: Data export (savings/credit card to CSV/Excel)
- **app/controllers/**: Business logic handlers
  - `PDFController`: PDF analysis and extraction operations
  - `FileController`: File management operations
  - `ExportController`: Data export and validation operations
- **app/services/**: Thin controllers delegating to pdf_analyzer modules
  - `pdf/analyzer_service.py`: Delegates to pdf_analyzer (extract_text, search_in_pdf, etc.)
  - `data/processor_service.py`: Delegates to data_processor (SavingsAccountProcessor, etc.)
  - `file/manager_service.py`: Delegates to file_manager (copy_pdf, PDFOrganizer, etc.)
  - `base/constants.py`: Centralized magic strings and configuration keys
  - `base/concerns.py`: Reusable mixins (PasswordAwareMixin, ExceptionMapperMixin, OutputDirectoryMixin)
- **app/schemas/**: Pydantic models for request/response validation
  - `common.py`: Base schemas (HealthResponse, SystemInfo, PaginationParams)
  - `pdf_analyzer.py`: PDF schemas (PDFDocumentSchema, TextExtractionResultSchema)
  - `file_operations.py`: File operation schemas (FileOperationResponse, OrganizationResultSchema)

## Key Conventions

- PDF filename format: `Extracto_{id}_{fecha}_{tipo}_{numero}.pdf` where fecha is `YYYYMM`
- Document types include: `CTA_AHORROS`, `TARJETA_MASTERCARD`, `COMISIONES_CONSOLIDADAS`
- All services accept optional `password` parameter for encrypted PDFs
- Environment variable `PDF_PASSWORD` sets default password for services
- Logging levels configurable via env vars: `LOG_LEVEL`, `LOG_LEVEL_CLI`, `LOG_LEVEL_PROCESSORS`, etc.
- Number parsing supports dual formats: US (`1,234.56`) and Colombian (`1.234,56`) - auto-detected by `NumberParser`

## Imports

```python
# Main API
from pdf_analyzer import (
    PDFDocument, LocalPDFRepository,
    ReaderService, AnalyzerService, SecurityService,
    FileOperations, PDFOrganizer, PDFRegistry,
)

# Data extractors
from pdf_analyzer.services import (
    SavingsAccountExtractor, CreditCardExtractor, BancolombiaExtractor,
    ExtractorService,
)

# Models (dataclasses)
from pdf_analyzer.models import (
    # Savings account
    AccountInfo, FinancialSummary, SavingsTransaction, SavingsAccountStatement,
    # Credit card
    CardInfo, CreditLimit, CreditCardTransaction, CreditCardStatement,
    # Base
    Transaction, TableInfo, Section,
)

# Concerns (mixins for extending classes)
from pdf_analyzer.concerns import (
    PathResolvableMixin, PasswordAwareMixin, CacheableMixin, Serializable,
)

# Parsers
from pdf_analyzer.services.parsers import NumberParser, parse_currency

# Convenience functions
from pdf_analyzer import list_pdfs, extract_text, analyze, search_in_pdf

# Data processors
from data_processor import SavingsAccountProcessor, CreditCardProcessor

# Logging
from logger import setup_logger, setup_cli_logger
```

## Commands

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix

# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run specific test file
pytest tests/pdf_analyzer/test_models.py

# Run tests with coverage
pytest --cov=src

# Utility scripts
python scripts/extract_with_pandas.py  # Extract data to CSV/Excel/Markdown
python scripts/lock_pdfs.py            # Add password protection
python scripts/unlock_pdfs.py          # Remove password protection

# REST API
cd restApi && python main.py           # Start API server (development)
cd restApi && uvicorn app.main:app --reload  # Alternative with uvicorn
```

## REST API

### Running the API

```bash
cd restApi
python main.py
# Server runs at http://localhost:8000
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### API Endpoints (v2)

| Category | Method | Endpoint | Description |
|----------|--------|----------|-------------|
| PDFs | GET | `/api/v2/pdfs` | List all PDFs with filters |
| PDFs | GET | `/api/v2/pdfs/{filename}` | Get PDF information |
| PDFs | GET | `/api/v2/pdfs/{filename}/text` | Extract text content |
| PDFs | GET | `/api/v2/pdfs/{filename}/tables` | Extract tables |
| PDFs | GET | `/api/v2/pdfs/{filename}/search` | Search text in PDF |
| PDFs | GET | `/api/v2/pdfs/{filename}/extract/savings` | Extract savings statement |
| PDFs | GET | `/api/v2/pdfs/{filename}/extract/credit-card` | Extract credit card statement |
| Files | POST | `/api/v2/files/copy` | Copy PDF file |
| Files | POST | `/api/v2/files/move` | Move PDF file |
| Files | POST | `/api/v2/files/rename` | Rename PDF file |
| Files | DELETE | `/api/v2/files/{filename}` | Delete PDF file |
| Files | POST | `/api/v2/files/organize` | Organize PDFs by type/year |
| Export | POST | `/api/v2/export/savings/{filename}` | Export savings data |
| Export | POST | `/api/v2/export/credit-card/{filename}` | Export credit card data |
| Export | POST | `/api/v2/export/batch/savings` | Batch export savings |

### API Configuration

Environment variables (in `restApi/.env`):
- `API_TITLE`: API title (default: "PDF Analyzer API")
- `API_VERSION`: API version (default: "1.0.0")
- `HOST`: Server host (default: "0.0.0.0")
- `PORT`: Server port (default: 8000)
- `RELOAD`: Auto-reload in development (default: true)
- `PDF_PASSWORD`: Default password for encrypted PDFs
- `CORS_ORIGINS`: Allowed CORS origins (default: "*")

### API Imports

```python
# Controllers
from app.controllers import PDFController, FileController, ExportController

# Core utilities
from app.core import (
    APIResponse, success_response, paginated_response,
    PDFNotFoundError, PDFPasswordError, PDFParsingError,
    log_endpoint, validate_filename_format, cache_response,
    OptionalPasswordDep, RequiredPasswordDep, PaginationDep,
)

# Schemas
from app.schemas import (
    PDFDocumentSchema, TextExtractionResultSchema,
    FileOperationResponse, OrganizationResultSchema,
)
```

## Testing

Test fixtures available in `conftest.py`:
- `temp_dir`: Temporary directory for test files
- `sample_pdf_path`: Single test PDF file
- `sample_pdf_files`: Multiple test PDF files
- `mock_pdfplumber`, `mock_pypdf_reader`: Mocked PDF readers
- `env_password`: PDF_PASSWORD environment fixture
