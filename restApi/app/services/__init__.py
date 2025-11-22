"""
Services package - Business logic layer.

This package contains service classes that bridge the API endpoints
with the core pdf_analyzer and data_processor modules from src/.

Architecture:
    API Layer (FastAPI) -> Services -> pdf_analyzer / data_processor

Structure:
    services/
    ├── base/           # Infrastructure (concerns, constants, imports)
    ├── pdf/            # PDF analysis service
    ├── files/          # File management service
    └── export/         # Data export service

Services use a concerns-based architecture for code reuse:
    - BaseService: Path validation + Password handling + Exception mapping
    - ExportableService: BaseService + Output directory management
"""

# Services (main exports)
from .pdf import PDFAnalyzerService
from .files import FileManagerService
from .export import DataProcessorService

# Base infrastructure (for extending services)
from .base import (
    # Mixins
    PathResolvableMixin,
    PasswordAwareMixin,
    ExceptionMapperMixin,
    OutputDirectoryMixin,
    # Base classes
    BaseService,
    ExportableService,
    # Decorators
    with_path_validation,
    with_exception_mapping,
    # Constants module
    constants,
)

__all__ = [
    # Services
    "PDFAnalyzerService",
    "FileManagerService",
    "DataProcessorService",
    # Base infrastructure
    "PathResolvableMixin",
    "PasswordAwareMixin",
    "ExceptionMapperMixin",
    "OutputDirectoryMixin",
    "BaseService",
    "ExportableService",
    "with_path_validation",
    "with_exception_mapping",
    "constants",
]
