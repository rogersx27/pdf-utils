"""
Base Controller - Common functionality for all controllers.

Provides a base class with shared utilities for HTTP response handling,
logging, and error management across all controller implementations.
"""
import logging
from typing import Any, Optional
from pathlib import Path
from fastapi.responses import JSONResponse, FileResponse

from app.core.responses import APIResponse


class BaseController:
    """
    Base controller providing common functionality for all controllers.

    Features:
    - Automatic logger configuration
    - Helper methods for response formatting
    - File response utilities
    """

    def __init__(self):
        """Initialize controller with configured logger."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def _success(
        self,
        data: Any,
        message: str = "Success",
        meta: Optional[dict[str, Any]] = None
    ) -> JSONResponse:
        """
        Create a standardized success response.

        Args:
            data: Response data (will call model_dump() if available)
            message: Success message
            meta: Optional metadata

        Returns:
            JSONResponse with standardized structure
        """
        # Auto-convert Pydantic models
        if hasattr(data, 'model_dump'):
            data = data.model_dump()

        return APIResponse.success(data=data, message=message, meta=meta)

    def _file_response(
        self,
        file_path: str | Path,
        filename: Optional[str] = None,
        media_type: str = 'application/octet-stream'
    ) -> FileResponse:
        """
        Create a file download response.

        Args:
            file_path: Path to the file
            filename: Download filename (defaults to actual filename)
            media_type: MIME type

        Returns:
            FileResponse for file download
        """
        path = Path(file_path)
        return FileResponse(
            path=str(path),
            filename=filename or path.name,
            media_type=media_type
        )

    def _log_operation(
        self,
        operation: str,
        **context: Any
    ) -> None:
        """
        Log an operation with context.

        Args:
            operation: Operation description
            **context: Additional context to log
        """
        self.logger.debug(f"{operation}", extra=context)
