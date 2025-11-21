# GitHub Copilot Instructions - PDF Analyzer

## Project Overview

This is a Python library for analyzing Colombian bank statement PDFs (extractos bancarios) using a Repository pattern with layered architecture. The core domain revolves around parsing PDF filenames with the specific format: `Extracto_{id}_{fecha}_{tipo}_{numero}.pdf` where `fecha` is `YYYYMM`.

## Architecture & Key Patterns

### Repository Pattern Structure
- **models/**: Domain entities (`PDFDocument`, `PDFDocumentInfo`) - dataclasses with filename parsing logic
- **repositories/**: Data access (`LocalPDFRepository`) - filesystem management with built-in caching
- **services/**: Business logic (`ReaderService`, `AnalyzerService`, `SecurityService`) - PDF operations with optional password support
- **file_manager/**: File operations (`FileOperations`, `PDFOrganizer`, `PDFRegistry`) - organizing, copying, inventory management

### Dependency Injection Pattern
Services accept `password` parameter for encrypted PDFs. Environment variable `PDF_PASSWORD` provides default. All services follow this pattern:
```python
analyzer = AnalyzerService(password="optional_password")
result = analyzer.analyze(document_or_path)
```

### Filename Convention (Critical)
All functionality depends on this format: `Extracto_455000853_202309_CTA_AHORROS_4332.pdf`
- Document types: `CTA_AHORROS`, `TARJETA_MASTERCARD`, `COMISIONES_CONSOLIDADAS`
- Date format: `YYYYMM`
- Use `PDFDocumentInfo.from_filename()` for parsing

### Hierarchical Logging System
The `src/logger/` package provides specialized loggers by component type:
```python
from logger import setup_logger, setup_cli_logger, setup_coordinator_logger, setup_processor_logger

# For CLI tools
logger = setup_cli_logger(setup_logger, __name__)
# For analysis services (coordinators)
logger = setup_coordinator_logger(setup_logger, __name__)
# For repositories (processors)  
logger = setup_processor_logger(setup_logger, __name__)
```

Environment variables control log levels: `LOG_LEVEL_CLI`, `LOG_LEVEL_COORDINATORS`, `LOG_LEVEL_PROCESSORS`, `LOG_LEVEL_UTILS`.

## Development Workflows

### Environment Setup
```bash
# Windows (project uses .venv\Scripts\activate)
.venv\Scripts\activate
pip install -r requirements.txt
```

### Testing
```bash
pytest                                    # All tests
pytest tests/pdf_analyzer/test_models.py # Specific module
pytest --cov=src                         # With coverage
```

### Key Dependencies
- **pypdf**: Core PDF reading (`ReaderService`)
- **pdfplumber**: Table extraction 
- **colorlog**: Console logging with colors
- **python-dotenv**: Environment configuration

## Critical Implementation Notes

### Caching Strategy
Both `LocalPDFRepository` and `AnalyzerService` implement internal caching. Repository caches `PDFDocument` objects by path, services cache analysis results by document path.

### Path Resolution
Services accept `PDFDocument | Path | str` and use `_resolve_path()` internally. Always work with `Path` objects in implementations.

### Error Handling Pattern
Use the logging system extensively. Services log operations at appropriate levels (DEBUG for initialization, INFO for operations, ERROR for failures).

### Convenience Functions
The package exports high-level convenience functions alongside service classes:
```python
# Direct functions
from pdf_analyzer import list_pdfs, extract_text, analyze, search_in_pdf
# Or service classes
from pdf_analyzer import LocalPDFRepository, AnalyzerService
```

### Testing Patterns
Use `conftest.py` fixtures: `temp_dir`, `sample_pdf_path`, `sample_pdf_files`. Tests mock PDF content with minimal valid PDF structure. The project path is added to `sys.path` in conftest.

### Configuration System
`src/config.py` uses `python-dotenv` for environment variables and creates required directories (`DATA_DIR`, `LOGS_DIR`) on import.
