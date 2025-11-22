"""
File Manager Service - Controller for pdf_analyzer.file_manager module.

This service acts as a thin controller layer that delegates all file operations
to the pdf_analyzer.file_manager module.

Architecture:
    API Layer (FastAPI) -> FileManagerService -> pdf_analyzer.file_manager
"""
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.exceptions import InternalServerError
from app.schemas.file_operations import (
    FileOperationResponse,
    FileInfoSchema,
    FolderInfoSchema,
    OrganizationResultSchema,
    PDFRegistrySchema,
    PDFRegistryEntrySchema,
)

from app.services.concerns import BaseService
from app.services.setup_imports import (
    copy_pdf,
    move_pdf,
    rename_pdf,
    delete_pdf,
    get_file_info,
    PDFOrganizer,
    PDFRegistry,
)


class FileManagerService(BaseService):
    """
    Service controller for file management operations.

    Inherits from BaseService which provides:
    - _resolve_and_validate_path(): Path validation
    - _resolve_destination_path(): Destination resolution
    - _map_exceptions(): Exception mapping
    """

    def __init__(self):
        """Initialize service with organizer and registry."""
        self.organizer = PDFOrganizer(str(settings.data_dir))
        self.registry = PDFRegistry(str(settings.data_dir))

    def copy_file(
        self,
        source: str,
        destination: str,
        overwrite: bool = False
    ) -> FileOperationResponse:
        """
        Copy a PDF file.

        Args:
            source: Source filename
            destination: Destination path
            overwrite: Whether to overwrite if exists

        Returns:
            FileOperationResponse with operation details
        """
        source_path = self._resolve_and_validate_path(source)
        dest_path = self._resolve_destination_path(destination)

        with self._map_exceptions("copy file"):
            result_path = copy_pdf(
                source=str(source_path),
                destination=str(dest_path),
                overwrite=overwrite
            )

            return FileOperationResponse(
                success=True,
                operation="copy",
                source=str(source_path),
                destination=str(result_path),
                message=f"File copied successfully to {Path(result_path).name}"
            )

    def move_file(
        self,
        source: str,
        destination: str,
        overwrite: bool = False
    ) -> FileOperationResponse:
        """
        Move a PDF file.

        Args:
            source: Source filename
            destination: Destination path
            overwrite: Whether to overwrite if exists

        Returns:
            FileOperationResponse with operation details
        """
        source_path = self._resolve_and_validate_path(source)
        dest_path = self._resolve_destination_path(destination)

        with self._map_exceptions("move file"):
            result_path = move_pdf(
                source=str(source_path),
                destination=str(dest_path),
                overwrite=overwrite
            )

            return FileOperationResponse(
                success=True,
                operation="move",
                source=str(source_path),
                destination=str(result_path),
                message=f"File moved successfully to {Path(result_path).name}"
            )

    def rename_file(self, source: str, new_name: str) -> FileOperationResponse:
        """
        Rename a PDF file.

        Args:
            source: Source filename
            new_name: New filename (without path)

        Returns:
            FileOperationResponse with operation details
        """
        source_path = self._resolve_and_validate_path(source)

        with self._map_exceptions("rename file"):
            result_path = rename_pdf(
                path=str(source_path),
                new_name=new_name
            )

            return FileOperationResponse(
                success=True,
                operation="rename",
                source=str(source_path),
                destination=str(result_path),
                message=f"File renamed successfully to {new_name}"
            )

    def delete_file(self, source: str) -> FileOperationResponse:
        """
        Delete a PDF file.

        Args:
            source: Source filename

        Returns:
            FileOperationResponse with operation details
        """
        source_path = self._resolve_and_validate_path(source)

        with self._map_exceptions("delete file"):
            delete_pdf(path=str(source_path))

            return FileOperationResponse(
                success=True,
                operation="delete",
                source=str(source_path),
                destination=None,
                message="File deleted successfully"
            )

    def get_file_info(self, filename: str) -> FileInfoSchema:
        """
        Get file information.

        Args:
            filename: PDF filename

        Returns:
            FileInfoSchema with file metadata
        """
        file_path = self._resolve_and_validate_path(filename)

        with self._map_exceptions("get file info"):
            info = get_file_info(path=str(file_path))

            return FileInfoSchema(
                filename=filename,
                path=str(file_path),
                size_bytes=info['size_bytes'],
                size_mb=info['size_mb'],
                created_at=info.get('created_at'),
                modified_at=info.get('modified_at'),
                is_encrypted=info.get('is_encrypted'),
                is_valid=True
            )

    def get_folder_info(self, folder_path: Optional[str] = None) -> FolderInfoSchema:
        """
        Get folder information.

        Args:
            folder_path: Folder path (defaults to settings.data_dir)

        Returns:
            FolderInfoSchema with folder statistics
        """
        path = Path(folder_path) if folder_path else settings.data_dir

        with self._map_exceptions("get folder info"):
            pdf_files = list(path.glob("*.pdf"))
            total_size = sum(f.stat().st_size for f in pdf_files if f.exists())

            return FolderInfoSchema(
                path=str(path),
                file_count=len(pdf_files),
                total_size_bytes=total_size,
                total_size_mb=round(total_size / (1024 * 1024), 2),
                files=[f.name for f in pdf_files]
            )

    def organize_by_type(
        self,
        source_dir: Optional[str] = None,
        target_dir: Optional[str] = None,
        copy: bool = False
    ) -> OrganizationResultSchema:
        """
        Organize PDFs by document type.

        Args:
            source_dir: Source directory
            target_dir: Target directory
            copy: Copy files instead of moving

        Returns:
            OrganizationResultSchema with operation statistics
        """
        with self._map_exceptions("organize by type"):
            result = self.organizer.organize_by_type(
                source_dir=source_dir,
                target_dir=target_dir,
                copy=copy
            )

            return self._organization_result_to_schema(result, "by_type")

    def organize_by_year(
        self,
        source_dir: Optional[str] = None,
        target_dir: Optional[str] = None,
        copy: bool = False
    ) -> OrganizationResultSchema:
        """
        Organize PDFs by year.

        Args:
            source_dir: Source directory
            target_dir: Target directory
            copy: Copy files instead of moving

        Returns:
            OrganizationResultSchema with operation statistics
        """
        with self._map_exceptions("organize by year"):
            result = self.organizer.organize_by_year(
                source_dir=source_dir,
                target_dir=target_dir,
                copy=copy
            )

            return self._organization_result_to_schema(result, "by_year")

    def get_registry(self) -> PDFRegistrySchema:
        """
        Get PDF registry/inventory.

        Returns:
            PDFRegistrySchema with complete inventory
        """
        with self._map_exceptions("generate registry"):
            inventory = self.registry.generate_inventory()

            entries = [
                PDFRegistryEntrySchema(
                    filename=entry['filename'],
                    document_id=entry['document_id'],
                    date=entry['date'],
                    type=entry['type'],
                    account_number=entry['account_number'],
                    file_size_mb=entry['file_size_mb'],
                    is_encrypted=entry['is_encrypted'],
                    page_count=entry.get('page_count')
                )
                for entry in inventory.get('entries', [])
            ]

            return PDFRegistrySchema(
                total_files=inventory.get('total_files', 0),
                total_size_mb=inventory.get('total_size_mb', 0.0),
                encrypted_count=inventory.get('encrypted_count', 0),
                document_types=inventory.get('document_types', {}),
                entries=entries
            )

    # =========================================================================
    # Private Helper Methods
    # =========================================================================

    def _organization_result_to_schema(
        self,
        result: dict,
        operation: str
    ) -> OrganizationResultSchema:
        """Convert organization result to API schema."""
        return OrganizationResultSchema(
            operation=operation,
            files_processed=result.get('files_processed', 0),
            files_moved=result.get('files_moved', 0),
            folders_created=result.get('folders_created', 0),
            errors=result.get('errors', []),
            summary=result.get('summary', {})
        )
