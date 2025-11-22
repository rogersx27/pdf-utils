"""
Pydantic schemas for file operations and data processing.

These schemas provide request/response validation for file management
and data export operations.
"""
from pydantic import Field, field_validator
from typing import Optional, Literal
from datetime import datetime

from app.schemas.common import BaseSchema


# ============================================================================
# File Operation Request Schemas
# ============================================================================

class FileOperationRequest(BaseSchema):
    """Base schema for file operation requests"""
    
    source: str = Field(description="Source file path or filename")


class CopyFileRequest(FileOperationRequest):
    """Schema for copy file request"""
    
    destination: str = Field(description="Destination directory or file path")
    overwrite: bool = Field(default=False, description="Whether to overwrite if exists")


class MoveFileRequest(FileOperationRequest):
    """Schema for move file request"""
    
    destination: str = Field(description="Destination directory or file path")
    overwrite: bool = Field(default=False, description="Whether to overwrite if exists")


class RenameFileRequest(FileOperationRequest):
    """Schema for rename file request"""
    
    new_name: str = Field(description="New filename")
    
    @field_validator('new_name')
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Validate that new_name doesn't contain path separators"""
        if '/' in v or '\\' in v:
            raise ValueError("new_name should be a filename, not a path")
        return v


class DeleteFileRequest(FileOperationRequest):
    """Schema for delete file request"""
    
    permanent: bool = Field(
        default=False,
        description="Whether to permanently delete (not implemented - safety measure)"
    )


# ============================================================================
# File Operation Response Schemas
# ============================================================================

class FileOperationResponse(BaseSchema):
    """Schema for file operation response"""
    
    success: bool = Field(description="Whether operation succeeded")
    operation: str = Field(description="Operation performed (copy/move/rename/delete)")
    source: str = Field(description="Source file")
    destination: Optional[str] = Field(default=None, description="Destination file/directory")
    message: str = Field(description="Operation result message")


class FileInfoSchema(BaseSchema):
    """Schema for file information"""
    
    filename: str = Field(description="File name")
    path: str = Field(description="Absolute path")
    size_bytes: int = Field(description="File size in bytes")
    size_mb: float = Field(description="File size in MB")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    modified_at: Optional[str] = Field(default=None, description="Modification timestamp")
    is_encrypted: Optional[bool] = Field(default=None, description="Whether file is encrypted")
    is_valid: bool = Field(description="Whether file is a valid PDF")


class FolderInfoSchema(BaseSchema):
    """Schema for folder information"""
    
    path: str = Field(description="Folder path")
    file_count: int = Field(description="Number of PDF files")
    total_size_bytes: int = Field(description="Total size in bytes")
    total_size_mb: float = Field(description="Total size in MB")
    files: list[str] = Field(default_factory=list, description="List of filenames")


# ============================================================================
# PDF Organization Schemas
# ============================================================================

class OrganizeByTypeRequest(BaseSchema):
    """Schema for organize by type request"""
    
    source_dir: Optional[str] = Field(
        default=None,
        description="Source directory (defaults to data directory)"
    )
    target_dir: Optional[str] = Field(
        default=None,
        description="Target base directory (defaults to data directory)"
    )
    copy_files: bool = Field(
        default=False,
        description="Copy instead of move",
        alias="copy"
    )


class OrganizeByYearRequest(BaseSchema):
    """Schema for organize by year request"""
    
    source_dir: Optional[str] = Field(
        default=None,
        description="Source directory (defaults to data directory)"
    )
    target_dir: Optional[str] = Field(
        default=None,
        description="Target base directory (defaults to data directory)"
    )
    copy_files: bool = Field(
        default=False,
        description="Copy instead of move",
        alias="copy"
    )


class OrganizationResultSchema(BaseSchema):
    """Schema for organization operation result"""
    
    operation: str = Field(description="Organization type (by_type/by_year)")
    files_processed: int = Field(description="Number of files processed")
    files_moved: int = Field(description="Number of files moved/copied")
    folders_created: int = Field(description="Number of folders created")
    errors: list[str] = Field(default_factory=list, description="List of errors")
    summary: dict[str, int] = Field(
        default_factory=dict,
        description="Summary by category (type/year)"
    )


# ============================================================================
# Security Operation Schemas
# ============================================================================

class AddPasswordRequest(BaseSchema):
    """Schema for add password request"""
    
    filename: str = Field(description="PDF filename")
    password: str = Field(description="Password to set", min_length=1)
    owner_password: Optional[str] = Field(
        default=None,
        description="Owner password (optional, defaults to same as user password)"
    )


class RemovePasswordRequest(BaseSchema):
    """Schema for remove password request"""
    
    filename: str = Field(description="PDF filename")
    current_password: str = Field(description="Current password", min_length=1)


class BatchPasswordRequest(BaseSchema):
    """Schema for batch password operation"""
    
    filenames: list[str] = Field(description="List of PDF filenames", min_length=1)
    password: str = Field(description="Password to add/remove", min_length=1)


class PasswordOperationResponse(BaseSchema):
    """Schema for password operation response"""
    
    filename: str = Field(description="File processed")
    success: bool = Field(description="Whether operation succeeded")
    message: str = Field(description="Operation result message")


class BatchPasswordResponse(BaseSchema):
    """Schema for batch password operation response"""
    
    total: int = Field(description="Total files processed")
    successful: int = Field(description="Successful operations")
    failed: int = Field(description="Failed operations")
    results: list[PasswordOperationResponse] = Field(description="Individual results")


# ============================================================================
# Data Export Schemas
# ============================================================================

class ExportFormat(str):
    """Valid export formats"""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    MARKDOWN = "markdown"


class DataExportRequest(BaseSchema):
    """Schema for data export request"""
    
    filename: str = Field(description="Source PDF filename")
    format: Literal["csv", "excel", "json", "markdown"] = Field(
        default="excel",
        description="Export format"
    )
    output_filename: Optional[str] = Field(
        default=None,
        description="Custom output filename (auto-generated if not provided)"
    )
    password: Optional[str] = Field(default=None, description="PDF password if encrypted")


class DataExportResponse(BaseSchema):
    """Schema for data export response"""
    
    source_file: str = Field(description="Source PDF file")
    output_file: str = Field(description="Generated output file")
    format: str = Field(description="Export format used")
    record_count: int = Field(description="Number of records exported")
    sheets: Optional[list[str]] = Field(
        default=None,
        description="Sheet names (for Excel exports)"
    )
    message: str = Field(description="Export result message")


class ValidationResultSchema(BaseSchema):
    """Schema for data validation result"""
    
    is_valid: bool = Field(description="Whether data is valid")
    errors: list[str] = Field(default_factory=list, description="Validation errors")
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")
    record_count: int = Field(description="Number of records validated")


# ============================================================================
# Batch Operation Schemas
# ============================================================================

class BatchAnalysisRequest(BaseSchema):
    """Schema for batch analysis request"""
    
    filenames: list[str] = Field(
        description="List of PDF filenames to analyze",
        min_length=1
    )
    password: Optional[str] = Field(default=None, description="Password for encrypted files")
    extract_data: bool = Field(
        default=True,
        description="Whether to extract structured data"
    )


class BatchAnalysisResultSchema(BaseSchema):
    """Schema for batch analysis result"""
    
    total: int = Field(description="Total files processed")
    successful: int = Field(description="Successfully analyzed")
    failed: int = Field(description="Failed analyses")
    results: list[dict] = Field(
        default_factory=list,
        description="Individual analysis results"
    )


# ============================================================================
# Registry/Inventory Schemas
# ============================================================================

class PDFRegistryEntrySchema(BaseSchema):
    """Schema for PDF registry entry"""
    
    filename: str = Field(description="PDF filename")
    document_id: str = Field(description="Document ID")
    date: str = Field(description="Document date (YYYYMM)")
    type: str = Field(description="Document type")
    account_number: str = Field(description="Account/card number")
    file_size_mb: float = Field(description="File size in MB")
    is_encrypted: bool = Field(description="Encryption status")
    page_count: Optional[int] = Field(default=None, description="Number of pages")


class PDFRegistrySchema(BaseSchema):
    """Schema for complete PDF registry/inventory"""
    
    total_files: int = Field(description="Total number of files")
    total_size_mb: float = Field(description="Total size in MB")
    encrypted_count: int = Field(description="Number of encrypted files")
    document_types: dict[str, int] = Field(
        description="Count by document type"
    )
    entries: list[PDFRegistryEntrySchema] = Field(
        default_factory=list,
        description="Registry entries"
    )
    generated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Registry generation timestamp"
    )
