"""
File Manager Service - Controller for pdf_analyzer.file_manager module.

This service acts as a thin controller layer that delegates all file operations
to the pdf_analyzer.file_manager module.

Architecture:
    API Layer (FastAPI) -> FileManagerService -> pdf_analyzer.file_manager
    
The pdf_analyzer.file_manager module provides:
    - Convenience functions: copy_pdf, move_pdf, rename_pdf, delete_pdf, get_file_info
    - PDFOrganizer: Organize PDFs by type/year
    - PDFRegistry: Generate inventories
"""
import sys
from pathlib import Path
from typing import Optional

# First import app modules (relative imports work within restApi/)
from app.core.config import settings
from app.core.exceptions import PDFNotFoundError, InternalServerError
from app.schemas.file_operations import (
    FileOperationResponse,
    FileInfoSchema,
    FolderInfoSchema,
    OrganizationResultSchema,
    PDFRegistrySchema,
    PDFRegistryEntrySchema,
)

# Add src to path for pdf_analyzer module
project_root = Path(__file__).parent.parent.parent.parent  # EXTRACTOS/
src_path = project_root / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import convenience functions and classes from pdf_analyzer.file_manager
from pdf_analyzer.file_manager import (
    copy_pdf,
    move_pdf,
    rename_pdf,
    delete_pdf,
    get_file_info,
    PDFOrganizer,
    PDFRegistry,
)


class FileManagerService:
    """
    Service controller for file management operations.
    
    Delegates all file operations to pdf_analyzer.file_manager module.
    This service only handles:
    - Path resolution and validation
    - Error handling and exception mapping
    - Format conversion to API response schemas
    """
    
    def __init__(self):
        """
        Initialize service with organizer and registry.
        
        Note: File operations use convenience functions directly,
        no need to instantiate FileOperations class.
        """
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
        
        Delegates to pdf_analyzer.file_manager.copy_pdf() convenience function.
        
        Args:
            source: Source filename (in settings.data_dir)
            destination: Destination path (relative or absolute)
            overwrite: Whether to overwrite if exists
            
        Returns:
            FileOperationResponse with operation details
            
        Raises:
            PDFNotFoundError: If source file doesn't exist
            InternalServerError: If copy operation fails
        """
        # Step 1: Validate source path
        source_path = settings.data_dir / source
        if not source_path.exists():
            raise PDFNotFoundError(source)
        
        try:
            # Step 2: Resolve destination path
            dest_path = Path(destination)
            if not dest_path.is_absolute():
                dest_path = settings.data_dir / destination
            
            # Step 3: Delegate to pdf_analyzer convenience function
            result_path = copy_pdf(
                source=str(source_path),
                destination=str(dest_path),
                overwrite=overwrite
            )
            
            # Step 4: Return API response
            return FileOperationResponse(
                success=True,
                operation="copy",
                source=str(source_path),
                destination=str(result_path),
                message=f"File copied successfully to {Path(result_path).name}"
            )
        except Exception as e:
            raise InternalServerError(f"Failed to copy file: {str(e)}") from e
    
    def move_file(
        self,
        source: str,
        destination: str,
        overwrite: bool = False
    ) -> FileOperationResponse:
        """
        Move a PDF file.
        
        Delegates to pdf_analyzer.file_manager.move_pdf() convenience function.
        
        Args:
            source: Source filename (in settings.data_dir)
            destination: Destination path (relative or absolute)
            overwrite: Whether to overwrite if exists
            
        Returns:
            FileOperationResponse with operation details
            
        Raises:
            PDFNotFoundError: If source file doesn't exist
            InternalServerError: If move operation fails
        """
        # Step 1: Validate source path
        source_path = settings.data_dir / source
        if not source_path.exists():
            raise PDFNotFoundError(source)
        
        try:
            # Step 2: Resolve destination path
            dest_path = Path(destination)
            if not dest_path.is_absolute():
                dest_path = settings.data_dir / destination
            
            # Step 3: Delegate to pdf_analyzer convenience function
            result_path = move_pdf(
                source=str(source_path),
                destination=str(dest_path),
                overwrite=overwrite
            )
            
            # Step 4: Return API response
            return FileOperationResponse(
                success=True,
                operation="move",
                source=str(source_path),
                destination=str(result_path),
                message=f"File moved successfully to {Path(result_path).name}"
            )
        except Exception as e:
            raise InternalServerError(f"Failed to move file: {str(e)}") from e
    
    def rename_file(self, source: str, new_name: str) -> FileOperationResponse:
        """
        Rename a PDF file.
        
        Delegates to pdf_analyzer.file_manager.rename_pdf() convenience function.
        
        Args:
            source: Source filename (in settings.data_dir)
            new_name: New filename (without path)
            
        Returns:
            FileOperationResponse with operation details
            
        Raises:
            PDFNotFoundError: If source file doesn't exist
            InternalServerError: If rename operation fails
        """
        # Step 1: Validate source path
        source_path = settings.data_dir / source
        if not source_path.exists():
            raise PDFNotFoundError(source)
        
        try:
            # Step 2: Delegate to pdf_analyzer convenience function
            result_path = rename_pdf(
                path=str(source_path),
                new_name=new_name
            )
            
            # Step 3: Return API response
            return FileOperationResponse(
                success=True,
                operation="rename",
                source=str(source_path),
                destination=str(result_path),
                message=f"File renamed successfully to {new_name}"
            )
        except Exception as e:
            raise InternalServerError(f"Failed to rename file: {str(e)}") from e
    
    def delete_file(self, source: str) -> FileOperationResponse:
        """
        Delete a PDF file.
        
        Delegates to pdf_analyzer.file_manager.delete_pdf() convenience function.
        
        Args:
            source: Source filename (in settings.data_dir)
            
        Returns:
            FileOperationResponse with operation details
            
        Raises:
            PDFNotFoundError: If source file doesn't exist
            InternalServerError: If delete operation fails
        """
        # Step 1: Validate source path
        source_path = settings.data_dir / source
        if not source_path.exists():
            raise PDFNotFoundError(source)
        
        try:
            # Step 2: Delegate to pdf_analyzer convenience function
            delete_pdf(path=str(source_path))
            
            # Step 3: Return API response
            return FileOperationResponse(
                success=True,
                operation="delete",
                source=str(source_path),
                destination=None,
                message="File deleted successfully"
            )
        except Exception as e:
            raise InternalServerError(f"Failed to delete file: {str(e)}") from e
    
    def get_file_info(self, filename: str) -> FileInfoSchema:
        """
        Get file information.
        
        Delegates to pdf_analyzer.file_manager.get_file_info() convenience function.
        
        Args:
            filename: PDF filename (in settings.data_dir)
            
        Returns:
            FileInfoSchema with file metadata
            
        Raises:
            PDFNotFoundError: If file doesn't exist
            InternalServerError: If operation fails
        """
        # Step 1: Validate path
        file_path = settings.data_dir / filename
        if not file_path.exists():
            raise PDFNotFoundError(filename)
        
        try:
            # Step 2: Delegate to pdf_analyzer convenience function
            info = get_file_info(path=str(file_path))
            
            # Step 3: Convert to API schema
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
        except Exception as e:
            raise InternalServerError(f"Failed to get file info: {str(e)}") from e
    
    def get_folder_info(self, folder_path: Optional[str] = None) -> FolderInfoSchema:
        """
        Get folder information.
        
        Scans directory for PDF files and calculates statistics.
        
        Args:
            folder_path: Folder path (defaults to settings.data_dir)
            
        Returns:
            FolderInfoSchema with folder statistics
            
        Raises:
            InternalServerError: If operation fails
        """
        # Step 1: Resolve path
        path = Path(folder_path) if folder_path else settings.data_dir
        
        try:
            # Step 2: Scan for PDF files and calculate stats
            pdf_files = list(path.glob("*.pdf"))
            total_size = sum(f.stat().st_size for f in pdf_files if f.exists())
            
            # Step 3: Return API schema
            return FolderInfoSchema(
                path=str(path),
                file_count=len(pdf_files),
                total_size_bytes=total_size,
                total_size_mb=round(total_size / (1024 * 1024), 2),
                files=[f.name for f in pdf_files]
            )
        except Exception as e:
            raise InternalServerError(f"Failed to get folder info: {str(e)}") from e
    
    def organize_by_type(
        self,
        source_dir: Optional[str] = None,
        target_dir: Optional[str] = None,
        copy: bool = False
    ) -> OrganizationResultSchema:
        """
        Organize PDFs by document type.
        
        Delegates to PDFOrganizer from pdf_analyzer.file_manager.
        Creates folders based on document type (CTA_AHORROS, TARJETA_MASTERCARD, etc.).
        
        Args:
            source_dir: Source directory (defaults to settings.data_dir)
            target_dir: Target directory (defaults to source_dir/organized)
            copy: Copy files instead of moving
            
        Returns:
            OrganizationResultSchema with operation statistics
            
        Raises:
            InternalServerError: If organization fails
        """
        try:
            # Delegate to PDFOrganizer (already handles all logic internally)
            result = self.organizer.organize_by_type(
                source_dir=source_dir,
                target_dir=target_dir,
                copy=copy
            )
            
            # Convert to API schema
            return OrganizationResultSchema(
                operation="by_type",
                files_processed=result.get('files_processed', 0),
                files_moved=result.get('files_moved', 0),
                folders_created=result.get('folders_created', 0),
                errors=result.get('errors', []),
                summary=result.get('summary', {})
            )
        except Exception as e:
            raise InternalServerError(f"Failed to organize by type: {str(e)}") from e
    
    def organize_by_year(
        self,
        source_dir: Optional[str] = None,
        target_dir: Optional[str] = None,
        copy: bool = False
    ) -> OrganizationResultSchema:
        """
        Organize PDFs by year.
        
        Delegates to PDFOrganizer from pdf_analyzer.file_manager.
        Creates folders based on year extracted from filename (YYYYMM format).
        
        Args:
            source_dir: Source directory (defaults to settings.data_dir)
            target_dir: Target directory (defaults to source_dir/organized)
            copy: Copy files instead of moving
            
        Returns:
            OrganizationResultSchema with operation statistics
            
        Raises:
            InternalServerError: If organization fails
        """
        try:
            # Delegate to PDFOrganizer (already handles all logic internally)
            result = self.organizer.organize_by_year(
                source_dir=source_dir,
                target_dir=target_dir,
                copy=copy
            )
            
            # Convert to API schema
            return OrganizationResultSchema(
                operation="by_year",
                files_processed=result.get('files_processed', 0),
                files_moved=result.get('files_moved', 0),
                folders_created=result.get('folders_created', 0),
                errors=result.get('errors', []),
                summary=result.get('summary', {})
            )
        except Exception as e:
            raise InternalServerError(f"Failed to organize by year: {str(e)}") from e
    
    def get_registry(self) -> PDFRegistrySchema:
        """
        Get PDF registry/inventory.
        
        Delegates to PDFRegistry from pdf_analyzer.file_manager.
        Generates comprehensive inventory of all PDFs in the directory.
        
        Returns:
            PDFRegistrySchema with complete inventory
            
        Raises:
            InternalServerError: If registry generation fails
        """
        try:
            # Delegate to PDFRegistry (already handles all extraction and processing)
            inventory = self.registry.generate_inventory()
            
            # Convert entries to API schema
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
            
            # Return API schema
            return PDFRegistrySchema(
                total_files=inventory.get('total_files', 0),
                total_size_mb=inventory.get('total_size_mb', 0.0),
                encrypted_count=inventory.get('encrypted_count', 0),
                document_types=inventory.get('document_types', {}),
                entries=entries
            )
        except Exception as e:
            raise InternalServerError(f"Failed to generate registry: {str(e)}") from e
