# GitHub Copilot Instructions - PDF Analyzer

## Project Overview

This is a Python library for analyzing Colombian bank statement PDFs (extractos bancarios) using a Repository pattern with layered architecture. The core domain revolves around parsing PDF filenames with the specific format: `Extracto_{id}_{fecha}_{tipo}_{numero}.pdf` where `fecha` is `YYYYMM`.

## Architecture & Key Patterns

### Repository Pattern Structure
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
- **data_processor/**: Pandas-based processors for converting extracted data to DataFrames with validation and multi-format export
  - `SavingsAccountProcessor`: Process savings account statements
  - `CreditCardProcessor`: Process credit card statements (multi-currency support)

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

### Number Parsing Convention
The project supports dual number formats with auto-detection:
- US format: `1,234.56` (comma as thousands separator, dot as decimal)
- Colombian format: `1.234,56` (dot as thousands separator, comma as decimal)
- Use `NumberParser` class for automatic format detection and conversion
- `parse_currency()` function handles currency string to float conversion

### Hierarchical Logging System
The `src/logger/` package provides date-based file handlers, colored console output, and pretty formatting functions:
```python
from logger import setup_logger, setup_cli_logger, setup_coordinator_logger, setup_processor_logger

# For CLI tools
logger = setup_cli_logger(setup_logger, __name__)
# For analysis services (coordinators)
logger = setup_coordinator_logger(setup_logger, __name__)
# For repositories (processors)  
logger = setup_processor_logger(setup_logger, __name__)
```

Environment variables control log levels: `LOG_LEVEL`, `LOG_LEVEL_CLI`, `LOG_LEVEL_COORDINATORS`, `LOG_LEVEL_PROCESSORS`, `LOG_LEVEL_UTILS`.

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

### Utility Scripts
```bash
python scripts/extract_with_pandas.py  # Extract data to CSV/Excel/Markdown
python scripts/lock_pdfs.py            # Add password protection
python scripts/unlock_pdfs.py          # Remove password protection
```

### Key Dependencies
- **pypdf**: Core PDF reading (`ReaderService`)
- **pdfplumber**: Table extraction 
- **colorlog**: Console logging with colors
- **python-dotenv**: Environment configuration
- **pandas**: Data processing and export

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

### Testing Patterns
Use `conftest.py` fixtures: `temp_dir`, `sample_pdf_path`, `sample_pdf_files`. Tests mock PDF content with minimal valid PDF structure. The project path is added to `sys.path` in conftest.

Test fixtures available in `conftest.py`:
- `temp_dir`: Temporary directory for test files
- `sample_pdf_path`: Single test PDF file
- `sample_pdf_files`: Multiple test PDF files
- `mock_pdfplumber`, `mock_pypdf_reader`: Mocked PDF readers
- `env_password`: PDF_PASSWORD environment fixture

### Configuration System
`src/config.py` uses `python-dotenv` for environment variables and creates required directories (`DATA_DIR`, `LOGS_DIR`) on import.
