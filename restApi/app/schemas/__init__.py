"""
Schemas package - Pydantic models for validation

This package contains all request/response schemas for the API.
All schemas inherit from BaseSchema for consistent configuration.
"""

from .common import (
    # Base
    BaseSchema,
    
    # Response wrappers
    SuccessResponse,
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
    
    # Pagination
    PaginationMeta,
    
    # Common responses
    HealthResponse,
    APIInfoResponse,
    MessageResponse,
    
    # Request parameters
    PaginationParams,
    SortParams,
    FilterParams,
)

from .pdf_analyzer import (
    # PDF Document
    PDFDocumentInfoSchema,
    PDFDocumentSchema,
    PDFMetadataSchema,
    
    # Transactions
    TransactionSchema,
    SavingsTransactionSchema,
    CreditCardTransactionSchema,
    
    # Account Info
    AccountInfoSchema,
    CardInfoSchema,
    FinancialSummarySchema,
    CreditLimitSchema,
    BalanceSummarySchema,
    
    # Statements
    SavingsAccountStatementSchema,
    CurrencyStatementSchema,
    CreditCardStatementSchema,
    
    # Analysis Results
    TextExtractionResultSchema,
    TableExtractionResultSchema,
    SearchResultSchema,
    ComparisonResultSchema,
)

from .file_operations import (
    # File Operation Requests
    FileOperationRequest,
    CopyFileRequest,
    MoveFileRequest,
    RenameFileRequest,
    DeleteFileRequest,
    
    # File Operation Responses
    FileOperationResponse,
    FileInfoSchema,
    FolderInfoSchema,
    
    # Organization
    OrganizeByTypeRequest,
    OrganizeByYearRequest,
    OrganizationResultSchema,
    
    # Security
    AddPasswordRequest,
    RemovePasswordRequest,
    BatchPasswordRequest,
    PasswordOperationResponse,
    BatchPasswordResponse,
    
    # Data Export
    DataExportRequest,
    DataExportResponse,
    ValidationResultSchema,
    
    # Batch Operations
    BatchAnalysisRequest,
    BatchAnalysisResultSchema,
    
    # Registry
    PDFRegistryEntrySchema,
    PDFRegistrySchema,
)

__all__ = [
    # Base
    "BaseSchema",
    
    # Response wrappers
    "SuccessResponse",
    "ErrorDetail",
    "ErrorResponse",
    "PaginatedResponse",
    
    # Pagination
    "PaginationMeta",
    
    # Common responses
    "HealthResponse",
    "APIInfoResponse",
    "MessageResponse",
    
    # Request parameters
    "PaginationParams",
    "SortParams",
    "FilterParams",
    
    # PDF Analyzer - Documents
    "PDFDocumentInfoSchema",
    "PDFDocumentSchema",
    "PDFMetadataSchema",
    
    # PDF Analyzer - Transactions
    "TransactionSchema",
    "SavingsTransactionSchema",
    "CreditCardTransactionSchema",
    
    # PDF Analyzer - Account Info
    "AccountInfoSchema",
    "CardInfoSchema",
    "FinancialSummarySchema",
    "CreditLimitSchema",
    "BalanceSummarySchema",
    
    # PDF Analyzer - Statements
    "SavingsAccountStatementSchema",
    "CurrencyStatementSchema",
    "CreditCardStatementSchema",
    
    # PDF Analyzer - Analysis
    "TextExtractionResultSchema",
    "TableExtractionResultSchema",
    "SearchResultSchema",
    "ComparisonResultSchema",
    
    # File Operations - Requests
    "FileOperationRequest",
    "CopyFileRequest",
    "MoveFileRequest",
    "RenameFileRequest",
    "DeleteFileRequest",
    
    # File Operations - Responses
    "FileOperationResponse",
    "FileInfoSchema",
    "FolderInfoSchema",
    
    # File Operations - Organization
    "OrganizeByTypeRequest",
    "OrganizeByYearRequest",
    "OrganizationResultSchema",
    
    # File Operations - Security
    "AddPasswordRequest",
    "RemovePasswordRequest",
    "BatchPasswordRequest",
    "PasswordOperationResponse",
    "BatchPasswordResponse",
    
    # File Operations - Export
    "DataExportRequest",
    "DataExportResponse",
    "ValidationResultSchema",
    
    # File Operations - Batch
    "BatchAnalysisRequest",
    "BatchAnalysisResultSchema",
    
    # File Operations - Registry
    "PDFRegistryEntrySchema",
    "PDFRegistrySchema",
]


