"""
PDF Controller - HTTP response handler for PDF operations.

This controller is responsible for handling HTTP requests/responses
for PDF analysis operations. It delegates business logic to PDFAnalyzerService
and uses core utilities for consistent responses.
"""
from typing import Optional
from fastapi.responses import JSONResponse

from app.controllers.base import BaseController
from app.controllers.concerns import PasswordAwareMixin
from app.core.decorators import handle_controller_errors
from app.services.pdf import PDFAnalyzerService


class PDFController(BaseController, PasswordAwareMixin):
    """
    Controller for PDF analysis endpoints.

    Handles HTTP responses for PDF operations using APIResponse utilities
    and delegates business logic to PDFAnalyzerService.
    """

    def __init__(self, password: Optional[str] = None):
        """
        Initialize controller with service.

        Args:
            password: Default password for encrypted PDFs
        """
        super().__init__()
        self._init_password(password)
        self.service = PDFAnalyzerService(password=password)

    @handle_controller_errors
    async def list_pdfs(
        self,
        tipo: Optional[str] = None,
        fecha: Optional[str] = None
    ) -> JSONResponse:
        """
        List all PDFs with optional filters.

        Args:
            tipo: Filter by document type (CTA_AHORROS, TARJETA_MASTERCARD, etc.)
            fecha: Filter by date (YYYYMM format)

        Returns:
            JSONResponse with list of PDFs
        """
        filters = {}
        if tipo:
            filters["tipo"] = tipo
        if fecha:
            filters["fecha"] = fecha

        pdfs = self.service.list_pdfs(filters=filters if filters else None)

        return self._success(
            data=[pdf.model_dump() for pdf in pdfs],
            message=f"Found {len(pdfs)} PDF(s)",
            meta={"total": len(pdfs), "filters": filters}
        )

    @handle_controller_errors
    async def get_pdf(self, filename: str) -> JSONResponse:
        """
        Get PDF document information.

        Args:
            filename: PDF filename

        Returns:
            JSONResponse with PDF information
        """
        pdf = self.service.get_pdf(filename)

        return self._success(
            data=pdf,
            message=f"PDF '{filename}' retrieved successfully"
        )

    @handle_controller_errors
    async def extract_text(
        self,
        filename: str,
        password: Optional[str] = None
    ) -> JSONResponse:
        """
        Extract text from PDF.

        Args:
            filename: PDF filename
            password: PDF password if encrypted

        Returns:
            JSONResponse with extracted text
        """
        result = self.service.extract_text(filename, password)

        return self._success(
            data=result,
            message="Text extracted successfully",
            meta={
                "page_count": result.page_count,
                "char_count": result.char_count
            }
        )

    @handle_controller_errors
    async def extract_tables(
        self,
        filename: str,
        password: Optional[str] = None
    ) -> JSONResponse:
        """
        Extract tables from PDF.

        Args:
            filename: PDF filename
            password: PDF password if encrypted

        Returns:
            JSONResponse with extracted tables
        """
        result = self.service.extract_tables(filename, password)

        return self._success(
            data=result,
            message=f"Extracted {result.table_count} table(s)",
            meta={"table_count": result.table_count}
        )

    @handle_controller_errors
    async def search_in_pdf(
        self,
        filename: str,
        query: str,
        password: Optional[str] = None
    ) -> JSONResponse:
        """
        Search text in PDF.

        Args:
            filename: PDF filename
            query: Search query
            password: PDF password if encrypted

        Returns:
            JSONResponse with search results
        """
        result = self.service.search_in_pdf(filename, query, password)

        return self._success(
            data=result,
            message=f"Found {result.occurrences} occurrence(s)",
            meta={
                "query": result.query,
                "found": result.found,
                "occurrences": result.occurrences
            }
        )

    @handle_controller_errors
    async def extract_savings_statement(
        self,
        filename: str,
        password: Optional[str] = None
    ) -> JSONResponse:
        """
        Extract savings account statement data.

        Args:
            filename: PDF filename
            password: PDF password if encrypted

        Returns:
            JSONResponse with savings account data
        """
        result = self.service.extract_savings_statement(filename, password)

        return self._success(
            data=result,
            message="Savings account statement extracted successfully",
            meta={
                "cuenta": result.cuenta.numero_cuenta,
                "periodo": result.cuenta.periodo,
                "transacciones": len(result.transacciones)
            }
        )

    @handle_controller_errors
    async def extract_credit_card_statement(
        self,
        filename: str,
        password: Optional[str] = None
    ) -> JSONResponse:
        """
        Extract credit card statement data.

        Args:
            filename: PDF filename
            password: PDF password if encrypted

        Returns:
            JSONResponse with credit card data
        """
        result = self.service.extract_credit_card_statement(filename, password)

        # Count transactions from both currencies
        total_transactions = 0
        currencies = []

        if result.movimientos_pesos:
            total_transactions += len(result.movimientos_pesos.transacciones)
            currencies.append("COP")
        if result.movimientos_dolares:
            total_transactions += len(result.movimientos_dolares.transacciones)
            currencies.append("USD")

        return self._success(
            data=result,
            message="Credit card statement extracted successfully",
            meta={
                "tarjeta": result.tarjeta.numero_tarjeta,
                "currencies": currencies,
                "total_transactions": total_transactions
            }
        )

    @handle_controller_errors
    async def get_metadata(
        self,
        filename: str,
        password: Optional[str] = None
    ) -> JSONResponse:
        """
        Get PDF metadata.

        Args:
            filename: PDF filename
            password: PDF password if encrypted

        Returns:
            JSONResponse with PDF metadata
        """
        metadata = self.service.get_metadata(filename, password)

        return self._success(
            data=metadata,
            message="Metadata retrieved successfully"
        )
