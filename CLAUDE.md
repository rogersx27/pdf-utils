# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PDF Analyzer is a Python library for analyzing Colombian bank statement PDFs (extractos bancarios). It parses PDF filenames following a specific naming convention (`Extracto_{id}_{fecha}_{tipo}_{numero}.pdf`) and provides services for reading, analyzing, organizing, and extracting structured data from PDF documents.

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
```

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

## Testing

Test fixtures available in `conftest.py`:
- `temp_dir`: Temporary directory for test files
- `sample_pdf_path`: Single test PDF file
- `sample_pdf_files`: Multiple test PDF files
- `mock_pdfplumber`, `mock_pypdf_reader`: Mocked PDF readers
- `env_password`: PDF_PASSWORD environment fixture
