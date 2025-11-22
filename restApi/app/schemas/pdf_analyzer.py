"""
Pydantic schemas for PDF Analyzer models.

These schemas provide request/response validation for PDF-related operations
including document info, transactions, and account statements.
"""
from pydantic import Field, ConfigDict
from typing import Optional
from datetime import datetime, date

from app.schemas.common import BaseSchema


# ============================================================================
# PDF Document Schemas
# ============================================================================

class PDFDocumentInfoSchema(BaseSchema):
    """Schema for PDF document information parsed from filename"""
    
    id: str = Field(description="Document ID from filename")
    fecha: str = Field(description="Date in YYYYMM format")
    tipo: str = Field(description="Document type (e.g., CTA_AHORROS, TARJETA_MASTERCARD)")
    numero: str = Field(description="Account/card number")
    filename: str = Field(description="Complete filename")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "455000853",
                "fecha": "202309",
                "tipo": "CTA_AHORROS",
                "numero": "4332",
                "filename": "Extracto_455000853_202309_CTA_AHORROS_4332.pdf"
            }
        }
    )


class PDFDocumentSchema(BaseSchema):
    """Schema for PDF document with metadata"""
    
    path: str = Field(description="Absolute path to PDF file")
    info: PDFDocumentInfoSchema = Field(description="Parsed document information")
    exists: bool = Field(description="Whether the file exists")
    size_bytes: Optional[int] = Field(default=None, description="File size in bytes")
    is_encrypted: Optional[bool] = Field(default=None, description="Whether PDF is encrypted")
    page_count: Optional[int] = Field(default=None, description="Number of pages")


class PDFMetadataSchema(BaseSchema):
    """Schema for PDF metadata"""
    
    title: Optional[str] = Field(default=None, description="PDF title")
    author: Optional[str] = Field(default=None, description="PDF author")
    subject: Optional[str] = Field(default=None, description="PDF subject")
    creator: Optional[str] = Field(default=None, description="PDF creator")
    producer: Optional[str] = Field(default=None, description="PDF producer")
    creation_date: Optional[str] = Field(default=None, description="Creation date")
    modification_date: Optional[str] = Field(default=None, description="Modification date")


# ============================================================================
# Transaction Schemas
# ============================================================================

class TransactionSchema(BaseSchema):
    """Base schema for financial transaction"""
    
    fecha: str = Field(description="Transaction date")
    descripcion: str = Field(description="Transaction description")
    valor: float = Field(description="Transaction amount")
    oficina: Optional[str] = Field(default=None, description="Office/branch code")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "fecha": "2023-09-15",
                "descripcion": "Compra en tienda",
                "valor": -50000.0,
                "oficina": "0123"
            }
        }
    )


class SavingsTransactionSchema(TransactionSchema):
    """Schema for savings account transaction"""
    
    pass


class CreditCardTransactionSchema(BaseSchema):
    """Schema for credit card transaction"""
    
    fecha: str = Field(description="Transaction date")
    descripcion: str = Field(description="Transaction description")
    referencia: Optional[str] = Field(default=None, description="Reference number")
    valor_pesos: Optional[float] = Field(default=None, description="Amount in COP")
    valor_dolares: Optional[float] = Field(default=None, description="Amount in USD")


# ============================================================================
# Account Info Schemas
# ============================================================================

class AccountInfoSchema(BaseSchema):
    """Schema for savings account information"""
    
    numero_cuenta: str = Field(description="Account number")
    tipo_cuenta: str = Field(description="Account type")
    titular: Optional[str] = Field(default=None, description="Account holder name")
    periodo: Optional[str] = Field(default=None, description="Statement period")


class CardInfoSchema(BaseSchema):
    """Schema for credit card information"""
    
    numero_tarjeta: str = Field(description="Masked card number")
    tipo_tarjeta: str = Field(description="Card type (e.g., MASTERCARD)")
    nombre_tarjetahabiente: Optional[str] = Field(default=None, description="Cardholder name")
    periodo: Optional[str] = Field(default=None, description="Statement period")


class FinancialSummarySchema(BaseSchema):
    """Schema for financial summary"""
    
    saldo_anterior: Optional[float] = Field(default=None, description="Previous balance")
    total_consignaciones: Optional[float] = Field(default=None, description="Total deposits")
    total_retiros: Optional[float] = Field(default=None, description="Total withdrawals")
    saldo_actual: Optional[float] = Field(default=None, description="Current balance")


class CreditLimitSchema(BaseSchema):
    """Schema for credit card limit information"""
    
    cupo_total: Optional[float] = Field(default=None, description="Total credit limit")
    cupo_disponible: Optional[float] = Field(default=None, description="Available credit")
    cupo_utilizado: Optional[float] = Field(default=None, description="Used credit")


class BalanceSummarySchema(BaseSchema):
    """Schema for credit card balance summary"""
    
    saldo_anterior: Optional[float] = Field(default=None, description="Previous balance")
    pagos: Optional[float] = Field(default=None, description="Payments made")
    compras: Optional[float] = Field(default=None, description="New purchases")
    intereses: Optional[float] = Field(default=None, description="Interest charges")
    saldo_actual: Optional[float] = Field(default=None, description="Current balance")


# ============================================================================
# Statement Schemas
# ============================================================================

class SavingsAccountStatementSchema(BaseSchema):
    """Schema for complete savings account statement"""
    
    cuenta: AccountInfoSchema = Field(description="Account information")
    resumen: FinancialSummarySchema = Field(description="Financial summary")
    transacciones: list[SavingsTransactionSchema] = Field(
        default_factory=list,
        description="List of transactions"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cuenta": {
                    "numero_cuenta": "****4332",
                    "tipo_cuenta": "Cuenta de Ahorros",
                    "periodo": "Septiembre 2023"
                },
                "resumen": {
                    "saldo_anterior": 1000000.0,
                    "total_consignaciones": 500000.0,
                    "total_retiros": 300000.0,
                    "saldo_actual": 1200000.0
                },
                "transacciones": [
                    {
                        "fecha": "2023-09-15",
                        "descripcion": "Consignación",
                        "valor": 500000.0
                    }
                ]
            }
        }
    )


class CurrencyStatementSchema(BaseSchema):
    """Schema for currency-specific credit card statement"""
    
    moneda: str = Field(description="Currency code (COP/USD)")
    transacciones: list[CreditCardTransactionSchema] = Field(
        default_factory=list,
        description="Transactions in this currency"
    )
    total: Optional[float] = Field(default=None, description="Total amount in currency")


class CreditCardStatementSchema(BaseSchema):
    """Schema for complete credit card statement"""
    
    tarjeta: CardInfoSchema = Field(description="Card information")
    cupo: Optional[CreditLimitSchema] = Field(default=None, description="Credit limit info")
    resumen: Optional[BalanceSummarySchema] = Field(default=None, description="Balance summary")
    movimientos_pesos: Optional[CurrencyStatementSchema] = Field(
        default=None,
        description="Transactions in COP"
    )
    movimientos_dolares: Optional[CurrencyStatementSchema] = Field(
        default=None,
        description="Transactions in USD"
    )


# ============================================================================
# Analysis Result Schemas
# ============================================================================

class TextExtractionResultSchema(BaseSchema):
    """Schema for text extraction result"""
    
    text: str = Field(description="Extracted text")
    page_count: int = Field(description="Number of pages")
    char_count: int = Field(description="Character count")


class TableExtractionResultSchema(BaseSchema):
    """Schema for table extraction result"""
    
    tables: list[list[list[str]]] = Field(
        description="Extracted tables (page -> table -> rows -> cells)"
    )
    table_count: int = Field(description="Total number of tables found")


class SearchResultSchema(BaseSchema):
    """Schema for search result in PDF"""
    
    query: str = Field(description="Search query")
    found: bool = Field(description="Whether query was found")
    occurrences: int = Field(description="Number of occurrences")
    context: list[str] = Field(
        default_factory=list,
        description="Context snippets where query was found"
    )


class ComparisonResultSchema(BaseSchema):
    """Schema for PDF comparison result"""
    
    file1: str = Field(description="First file name")
    file2: str = Field(description="Second file name")
    are_identical: bool = Field(description="Whether files are identical")
    differences: list[str] = Field(
        default_factory=list,
        description="List of differences found"
    )
