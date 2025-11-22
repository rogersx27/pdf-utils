"""
Services package - Business logic layer.

This package contains service classes that bridge the API endpoints
with the core pdf_analyzer and data_processor modules from src/.

Architecture:
    API Layer (FastAPI) -> Services -> pdf_analyzer / data_processor

Services use a concerns-based architecture for code reuse:
    - BaseService: Path validation + Password handling + Exception mapping
    - ExportableService: BaseService + Output directory management
"""

# Services
from .pdf_analyzer_service import PDFAnalyzerService
from .file_manager_service import FileManagerService
from .data_processor_service import DataProcessorService

# Concerns (Mixins) for extending services
from .concerns import (
    # Individual mixins
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
)

__all__ = [
    # Services
    "PDFAnalyzerService",
    "FileManagerService",
    "DataProcessorService",
    # Concerns
    "PathResolvableMixin",
    "PasswordAwareMixin",
    "ExceptionMapperMixin",
    "OutputDirectoryMixin",
    "BaseService",
    "ExportableService",
    # Decorators
    "with_path_validation",
    "with_exception_mapping",
]
