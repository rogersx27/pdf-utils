# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PDF Analyzer is a Python library for analyzing bank statement PDFs (extractos bancarios). It parses PDF filenames following a specific naming convention (`Extracto_{id}_{fecha}_{tipo}_{numero}.pdf`) and provides services for reading, analyzing, and organizing PDF documents.

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
```

## Architecture

The project follows a Repository pattern with layered architecture in `src/pdf_analyzer/`:

- **models/**: Domain entities (`PDFDocument`, `PDFDocumentInfo`) - dataclasses representing PDF documents with parsed filename info (tipo, fecha, numero)
- **repositories/**: Data access layer (`LocalPDFRepository`) - manages PDF files in the filesystem with caching
- **services/**: Business logic
  - `ReaderService`: Text/table extraction using pypdf and pdfplumber
  - `AnalyzerService`: Analysis operations with caching (search, compare)
  - `SecurityService`: Password operations (add/remove encryption)
- **file_manager/**: File operations (`FileOperations`, `PDFOrganizer`, `PDFRegistry`) - copy/move/rename, organize by type/year, export inventories

The `src/logger/` package provides a logging system with date-based file handlers, colored console output, and pretty formatting functions.

## Key Conventions

- PDF filename format: `Extracto_{id}_{fecha}_{tipo}_{numero}.pdf` where fecha is `YYYYMM`
- Document types include: `CTA_AHORROS`, `TARJETA_MASTERCARD`, `COMISIONES_CONSOLIDADAS`
- All services accept optional `password` parameter for encrypted PDFs
- Environment variable `PDF_PASSWORD` sets default password for services
- Logging levels configurable via env vars: `LOG_LEVEL`, `LOG_LEVEL_CLI`, `LOG_LEVEL_PROCESSORS`, etc.

## Imports

```python
# Main API
from pdf_analyzer import (
    PDFDocument, LocalPDFRepository,
    ReaderService, AnalyzerService, SecurityService,
    FileOperations, PDFOrganizer, PDFRegistry,
)

# Convenience functions
from pdf_analyzer import list_pdfs, extract_text, analyze, search_in_pdf

# Logging
from logger import setup_logger, setup_cli_logger
```
