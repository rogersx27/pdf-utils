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

from app.services.base import BaseService
from app.services.base.constants import (
    OPERATION_COPY,
    OPERATION_MOVE,
    OPERATION_RENAME,
    OPERATION_DELETE,
    ORGANIZATION_BY_TYPE,
    ORGANIZATION_BY_YEAR,
    MSG_FILE_COPIED,
    MSG_FILE_MOVED,
    MSG_FILE_RENAMED,
    MSG_FILE_DELETED,
    KEY_SIZE_BYTES,
    KEY_SIZE_MB,
    KEY_CREATED_AT,
    KEY_MODIFIED_AT,
    KEY_IS_ENCRYPTED,
    KEY_PAGE_COUNT,
    KEY_TOTAL_FILES,
    KEY_TOTAL_SIZE_MB,
    KEY_ENCRYPTED_COUNT,
    KEY_DOCUMENT_TYPES,
    KEY_ENTRIES,
    KEY_FILENAME,
    KEY_DOCUMENT_ID,
    KEY_DATE,
    KEY_TYPE,
    KEY_ACCOUNT_NUMBER,
    KEY_FILE_SIZE_MB,
    KEY_FILES_PROCESSED,
    KEY_FILES_MOVED,
    KEY_FOLDERS_CREATED,
    KEY_ERRORS,
    KEY_SUMMARY,
    EXT_PDF,
)
from app.services.base.imports import (
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
                operation=OPERATION_COPY,
                source=str(source_path),
                destination=str(result_path),
                message=MSG_FILE_COPIED.format(filename=Path(result_path).name)
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
                operation=OPERATION_MOVE,
                source=str(source_path),
                destination=str(result_path),
                message=MSG_FILE_MOVED.format(filename=Path(result_path).name)
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
                operation=OPERATION_RENAME,
                source=str(source_path),
                destination=str(result_path),
                message=MSG_FILE_RENAMED.format(filename=new_name)
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
                operation=OPERATION_DELETE,
                source=str(source_path),
                destination=None,
                message=MSG_FILE_DELETED
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
                size_bytes=info[KEY_SIZE_BYTES],
                size_mb=info[KEY_SIZE_MB],
                created_at=info.get(KEY_CREATED_AT),
                modified_at=info.get(KEY_MODIFIED_AT),
                is_encrypted=info.get(KEY_IS_ENCRYPTED),
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
            pdf_files = list(path.glob(f"*{EXT_PDF}"))
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

            return self._organization_result_to_schema(result, ORGANIZATION_BY_TYPE)

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

            return self._organization_result_to_schema(result, ORGANIZATION_BY_YEAR)

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
                    filename=entry[KEY_FILENAME],
                    document_id=entry[KEY_DOCUMENT_ID],
                    date=entry[KEY_DATE],
                    type=entry[KEY_TYPE],
                    account_number=entry[KEY_ACCOUNT_NUMBER],
                    file_size_mb=entry[KEY_FILE_SIZE_MB],
                    is_encrypted=entry[KEY_IS_ENCRYPTED],
                    page_count=entry.get(KEY_PAGE_COUNT)
                )
                for entry in inventory.get(KEY_ENTRIES, [])
            ]

            return PDFRegistrySchema(
                total_files=inventory.get(KEY_TOTAL_FILES, 0),
                total_size_mb=inventory.get(KEY_TOTAL_SIZE_MB, 0.0),
                encrypted_count=inventory.get(KEY_ENCRYPTED_COUNT, 0),
                document_types=inventory.get(KEY_DOCUMENT_TYPES, {}),
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
            files_processed=result.get(KEY_FILES_PROCESSED, 0),
            files_moved=result.get(KEY_FILES_MOVED, 0),
            folders_created=result.get(KEY_FOLDERS_CREATED, 0),
            errors=result.get(KEY_ERRORS, []),
            summary=result.get(KEY_SUMMARY, {})
        )
