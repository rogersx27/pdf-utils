"""
File Controller - HTTP response handler for file operations.

This controller is responsible for handling HTTP requests/responses
for file management operations. It delegates business logic to FileManagerService
and uses core utilities for consistent responses.
"""
from typing import Optional
from fastapi.responses import JSONResponse

from app.controllers.base import BaseController
from app.core.decorators import handle_controller_errors
from app.services.files import FileManagerService


class FileController(BaseController):
    """
    Controller for file management endpoints.

    Handles HTTP responses for file operations using APIResponse utilities
    and delegates business logic to FileManagerService.
    """

    def __init__(self):
        """Initialize controller with service."""
        super().__init__()
        self.service = FileManagerService()

    @handle_controller_errors
    async def copy_file(
        self,
        source: str,
        destination: str,
        overwrite: bool = False
    ) -> JSONResponse:
        """
        Copy a PDF file.

        Args:
            source: Source filename
            destination: Destination path
            overwrite: Whether to overwrite if exists

        Returns:
            JSONResponse with operation result
        """
        result = self.service.copy_file(source, destination, overwrite)

        return self._success(
            data=result,
            message=result.message,
            meta={"operation": result.operation}
        )

    @handle_controller_errors
    async def move_file(
        self,
        source: str,
        destination: str,
        overwrite: bool = False
    ) -> JSONResponse:
        """
        Move a PDF file.

        Args:
            source: Source filename
            destination: Destination path
            overwrite: Whether to overwrite if exists

        Returns:
            JSONResponse with operation result
        """
        result = self.service.move_file(source, destination, overwrite)

        return self._success(
            data=result,
            message=result.message,
            meta={"operation": result.operation}
        )

    @handle_controller_errors
    async def rename_file(
        self,
        source: str,
        new_name: str
    ) -> JSONResponse:
        """
        Rename a PDF file.

        Args:
            source: Source filename
            new_name: New filename

        Returns:
            JSONResponse with operation result
        """
        result = self.service.rename_file(source, new_name)

        return self._success(
            data=result,
            message=result.message,
            meta={"operation": result.operation}
        )

    @handle_controller_errors
    async def delete_file(self, filename: str) -> JSONResponse:
        """
        Delete a PDF file.

        Args:
            filename: Filename to delete

        Returns:
            JSONResponse with operation result
        """
        result = self.service.delete_file(filename)

        return self._success(
            data=result,
            message=result.message,
            meta={"operation": result.operation}
        )

    @handle_controller_errors
    async def get_file_info(self, filename: str) -> JSONResponse:
        """
        Get file information.

        Args:
            filename: Filename

        Returns:
            JSONResponse with file information
        """
        info = self.service.get_file_info(filename)

        return self._success(
            data=info,
            message=f"File info retrieved for '{filename}'",
            meta={
                "size_mb": info.size_mb,
                "is_encrypted": info.is_encrypted
            }
        )

    @handle_controller_errors
    async def get_folder_info(
        self,
        folder_path: Optional[str] = None
    ) -> JSONResponse:
        """
        Get folder statistics.

        Args:
            folder_path: Folder path (defaults to data directory)

        Returns:
            JSONResponse with folder statistics
        """
        info = self.service.get_folder_info(folder_path)

        return self._success(
            data=info,
            message=f"Folder contains {info.file_count} file(s)",
            meta={
                "file_count": info.file_count,
                "total_size_mb": info.total_size_mb
            }
        )

    @handle_controller_errors
    async def organize_by_type(
        self,
        source_dir: Optional[str] = None,
        target_dir: Optional[str] = None,
        copy: bool = False
    ) -> JSONResponse:
        """
        Organize PDFs by document type.

        Args:
            source_dir: Source directory (optional)
            target_dir: Target directory (optional)
            copy: If True, copy files instead of moving

        Returns:
            JSONResponse with organization results
        """
        result = self.service.organize_by_type(source_dir, target_dir, copy)
        action = "copied" if copy else "moved"

        return self._success(
            data=result,
            message=f"PDFs organized by type ({result.files_moved} files {action})",
            meta={
                "files_processed": result.files_processed,
                "files_moved": result.files_moved,
                "folders_created": result.folders_created,
                "copy_mode": copy
            }
        )

    @handle_controller_errors
    async def organize_by_year(
        self,
        source_dir: Optional[str] = None,
        target_dir: Optional[str] = None,
        copy: bool = False
    ) -> JSONResponse:
        """
        Organize PDFs by year.

        Args:
            source_dir: Source directory (optional)
            target_dir: Target directory (optional)
            copy: If True, copy files instead of moving

        Returns:
            JSONResponse with organization results
        """
        result = self.service.organize_by_year(source_dir, target_dir, copy)
        action = "copied" if copy else "moved"

        return self._success(
            data=result,
            message=f"PDFs organized by year ({result.files_moved} files {action})",
            meta={
                "files_processed": result.files_processed,
                "files_moved": result.files_moved,
                "folders_created": result.folders_created,
                "copy_mode": copy
            }
        )

    @handle_controller_errors
    async def get_registry(self) -> JSONResponse:
        """
        Get PDF registry (inventory).

        Returns:
            JSONResponse with PDF registry
        """
        registry = self.service.get_registry()

        return self._success(
            data=registry,
            message=f"Registry contains {registry.total_files} file(s)",
            meta={
                "total_files": registry.total_files,
                "total_size_mb": registry.total_size_mb,
                "encrypted_count": registry.encrypted_count,
                "document_types": list(registry.document_types.keys())
            }
        )
