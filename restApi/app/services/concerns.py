"""
Service Concerns (Mixins) for REST API services.

Provides reusable behavior for common service patterns:
- Path validation and resolution
- Password handling
- Exception mapping
- Output directory management

Usage:
    class MyService(PathResolvableMixin, PasswordAwareMixin, ExceptionMapperMixin):
        def __init__(self, password: Optional[str] = None):
            self._init_password(password)

        def my_method(self, filename: str):
            pdf_path = self._resolve_and_validate_path(filename)
            with self._map_exceptions("operation description"):
                # ... do work
"""
from abc import ABC
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Generator, Callable, TypeVar, Any
from functools import wraps

from app.core.config import settings
from app.core.exceptions import (
    PDFNotFoundError,
    PDFPasswordError,
    PDFParsingError,
    InternalServerError,
)

T = TypeVar('T')


# =============================================================================
# Path Resolution Mixin
# =============================================================================

class PathResolvableMixin:
    """
    Mixin for path validation and resolution operations.

    Provides methods to validate PDF paths and resolve relative paths
    to absolute paths within the data directory.
    """

    def _resolve_path(self, filename: str, base_dir: Optional[Path] = None) -> Path:
        """
        Resolve filename to absolute path.

        Args:
            filename: PDF filename or relative path
            base_dir: Base directory (defaults to settings.data_dir)

        Returns:
            Absolute Path object
        """
        base = base_dir or settings.data_dir
        path = Path(filename)

        if path.is_absolute():
            return path
        return base / filename

    def _validate_path_exists(self, path: Path, filename: str) -> None:
        """
        Validate that path exists.

        Args:
            path: Path to validate
            filename: Original filename (for error message)

        Raises:
            PDFNotFoundError: If path doesn't exist
        """
        if not path.exists():
            raise PDFNotFoundError(filename)

    def _resolve_and_validate_path(
        self,
        filename: str,
        base_dir: Optional[Path] = None
    ) -> Path:
        """
        Resolve and validate path in one step.

        Args:
            filename: PDF filename
            base_dir: Base directory (optional)

        Returns:
            Validated absolute Path

        Raises:
            PDFNotFoundError: If file doesn't exist
        """
        path = self._resolve_path(filename, base_dir)
        self._validate_path_exists(path, filename)
        return path

    def _resolve_destination_path(
        self,
        destination: str,
        base_dir: Optional[Path] = None
    ) -> Path:
        """
        Resolve destination path (for copy/move operations).

        Args:
            destination: Destination path (relative or absolute)
            base_dir: Base directory for relative paths

        Returns:
            Absolute destination Path
        """
        dest_path = Path(destination)
        if dest_path.is_absolute():
            return dest_path
        return (base_dir or settings.data_dir) / destination


# =============================================================================
# Password Handling Mixin
# =============================================================================

class PasswordAwareMixin:
    """
    Mixin for password handling in services.

    Provides initialization and retrieval of PDF passwords
    with fallback to settings.
    """

    password: Optional[str]

    def _init_password(self, password: Optional[str] = None) -> None:
        """
        Initialize password from argument or settings.

        Args:
            password: Explicit password (optional)
        """
        self.password = password or settings.pdf_password or None

    def _get_password(self, override: Optional[str] = None) -> Optional[str]:
        """
        Get password with optional override.

        Args:
            override: Password override (optional)

        Returns:
            Password to use (override > instance > None)
        """
        return override or self.password


# =============================================================================
# Exception Mapping Mixin
# =============================================================================

class ExceptionMapperMixin:
    """
    Mixin for consistent exception mapping.

    Maps generic exceptions to API-specific exceptions with
    proper error messages and HTTP status codes.
    """

    @contextmanager
    def _map_exceptions(
        self,
        operation: str,
        error_class: type = InternalServerError
    ) -> Generator[None, None, None]:
        """
        Context manager for exception mapping.

        Maps password-related exceptions to PDFPasswordError,
        and other exceptions to the specified error class.

        Args:
            operation: Description of operation (for error message)
            error_class: Exception class for non-password errors

        Usage:
            with self._map_exceptions("extract text"):
                # ... do work that might raise exceptions
        """
        try:
            yield
        except (PDFNotFoundError, PDFPasswordError, PDFParsingError, InternalServerError):
            # Re-raise API exceptions as-is
            raise
        except Exception as e:
            error_msg = str(e).lower()
            if "password" in error_msg or "encrypted" in error_msg:
                raise PDFPasswordError(str(e)) from e
            raise error_class(f"Failed to {operation}: {str(e)}") from e

    def _handle_exception(
        self,
        exception: Exception,
        operation: str,
        error_class: type = InternalServerError
    ) -> None:
        """
        Handle exception with consistent mapping.

        Args:
            exception: The caught exception
            operation: Description of operation
            error_class: Exception class for non-password errors

        Raises:
            PDFPasswordError: If exception is password-related
            error_class: For other exceptions
        """
        error_msg = str(exception).lower()
        if "password" in error_msg or "encrypted" in error_msg:
            raise PDFPasswordError(str(exception)) from exception
        raise error_class(f"Failed to {operation}: {str(exception)}") from exception


# =============================================================================
# Output Directory Mixin
# =============================================================================

class OutputDirectoryMixin:
    """
    Mixin for output directory management.

    Provides methods for preparing output directories and
    generating output paths for export operations.
    """

    def _get_output_dir(self, subdir: str = "data-extracted") -> Path:
        """
        Get or create output directory.

        Args:
            subdir: Subdirectory name within project root

        Returns:
            Path to output directory (created if needed)
        """
        output_dir = settings.data_dir.parent / subdir
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _generate_output_path(
        self,
        source_path: Path,
        output_filename: Optional[str] = None,
        extension: str = ".xlsx",
        output_dir: Optional[Path] = None
    ) -> Path:
        """
        Generate output file path.

        Args:
            source_path: Source PDF path
            output_filename: Custom output filename (optional)
            extension: File extension (default: .xlsx)
            output_dir: Output directory (optional)

        Returns:
            Path for output file
        """
        out_dir = output_dir or self._get_output_dir()

        if output_filename:
            return out_dir / output_filename

        return out_dir / f"{source_path.stem}{extension}"


# =============================================================================
# Base Service Class
# =============================================================================

class BaseService(PathResolvableMixin, PasswordAwareMixin, ExceptionMapperMixin):
    """
    Base service class combining common mixins.

    Provides a foundation for all API services with:
    - Path validation and resolution
    - Password handling
    - Exception mapping

    Usage:
        class MyService(BaseService):
            def __init__(self, password: Optional[str] = None):
                self._init_password(password)

            def my_method(self, filename: str):
                pdf_path = self._resolve_and_validate_path(filename)
                with self._map_exceptions("do something"):
                    # ... implementation
    """
    pass


class ExportableService(BaseService, OutputDirectoryMixin):
    """
    Base service class for services that export data.

    Extends BaseService with output directory management.

    Usage:
        class DataExportService(ExportableService):
            def export_data(self, filename: str, format: str):
                pdf_path = self._resolve_and_validate_path(filename)
                output_dir = self._get_output_dir()
                output_path = self._generate_output_path(pdf_path, extension=".csv")
                # ... export logic
    """
    pass


# =============================================================================
# Decorator Utilities
# =============================================================================

def with_path_validation(param_name: str = "filename"):
    """
    Decorator to validate PDF path before method execution.

    Args:
        param_name: Name of the filename parameter

    Usage:
        @with_path_validation("filename")
        def extract_text(self, filename: str) -> str:
            # filename is already validated
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> T:
            # Get filename from args or kwargs
            filename = kwargs.get(param_name)
            if filename is None and args:
                filename = args[0]

            if filename and hasattr(self, '_resolve_and_validate_path'):
                self._resolve_and_validate_path(filename)

            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def with_exception_mapping(operation: str, error_class: type = InternalServerError):
    """
    Decorator to map exceptions in method.

    Args:
        operation: Description of operation
        error_class: Exception class for non-password errors

    Usage:
        @with_exception_mapping("extract text", PDFParsingError)
        def extract_text(self, filename: str) -> str:
            # Exceptions will be mapped automatically
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> T:
            if hasattr(self, '_map_exceptions'):
                with self._map_exceptions(operation, error_class):
                    return func(self, *args, **kwargs)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
