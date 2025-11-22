"""
PDF Analyzer Service - Controller for pdf_analyzer module.

This service acts as a thin controller layer that delegates all PDF operations
to the pdf_analyzer module's convenience functions and extractors.

Architecture:
    API Layer (FastAPI) -> PDFAnalyzerService -> pdf_analyzer module
"""
from typing import Optional

from app.core.config import settings
from app.core.exceptions import PDFParsingError, InvalidFilenameError
from app.schemas.pdf_analyzer import (
    PDFDocumentSchema,
    PDFDocumentInfoSchema,
    PDFMetadataSchema,
    TextExtractionResultSchema,
    TableExtractionResultSchema,
    SearchResultSchema,
    SavingsAccountStatementSchema,
    CreditCardStatementSchema,
)

from app.services.concerns import BaseService
from app.services.setup_imports import (
    LocalPDFRepository,
    PDFDocument,
    extract_text,
    extract_tables,
    get_metadata,
    get_page_count,
    is_encrypted,
    search_in_pdf,
    SavingsAccountExtractor,
    CreditCardExtractor,
)


class PDFAnalyzerService(BaseService):
    """
    Service controller for PDF analysis operations.

    Inherits from BaseService which provides:
    - _resolve_and_validate_path(): Path validation
    - _init_password() / _get_password(): Password handling
    - _map_exceptions(): Exception mapping
    """

    def __init__(self, password: Optional[str] = None):
        """
        Initialize service with repository.

        Args:
            password: Default password for encrypted PDFs
        """
        self._init_password(password)
        self.repository = LocalPDFRepository(
            str(settings.data_dir),
            password=self.password
        )

    def list_pdfs(self, filters: Optional[dict] = None) -> list[PDFDocumentSchema]:
        """
        List all PDFs in the data directory.

        Args:
            filters: Optional filters (tipo, fecha)

        Returns:
            List of PDFDocumentSchema with parsed filename information
        """
        with self._map_exceptions("list PDFs", PDFParsingError):
            documents = self.repository.get_all()

            if filters:
                documents = self._apply_filters(documents, filters)

            return [self._document_to_schema(doc) for doc in documents]

    def get_pdf(self, filename: str) -> PDFDocumentSchema:
        """
        Get a single PDF document with parsed metadata.

        Args:
            filename: PDF filename

        Returns:
            PDFDocumentSchema with parsed information
        """
        pdf_path = self._resolve_and_validate_path(filename)

        try:
            document = self.repository.get(str(pdf_path))
            return self._document_to_schema(document)
        except ValueError as e:
            raise InvalidFilenameError(filename) from e

    def extract_text(
        self,
        filename: str,
        password: Optional[str] = None
    ) -> TextExtractionResultSchema:
        """
        Extract text from PDF.

        Args:
            filename: PDF filename
            password: PDF password (optional)

        Returns:
            TextExtractionResultSchema with extracted text and metadata
        """
        pdf_path = self._resolve_and_validate_path(filename)
        pwd = self._get_password(password)

        with self._map_exceptions("extract text", PDFParsingError):
            text = extract_text(pdf_path, password=pwd)
            page_count = get_page_count(pdf_path, password=pwd)

            return TextExtractionResultSchema(
                text=text,
                page_count=page_count,
                char_count=len(text)
            )

    def extract_tables(
        self,
        filename: str,
        password: Optional[str] = None
    ) -> TableExtractionResultSchema:
        """
        Extract tables from PDF.

        Args:
            filename: PDF filename
            password: PDF password (optional)

        Returns:
            TableExtractionResultSchema with extracted tables
        """
        pdf_path = self._resolve_and_validate_path(filename)
        pwd = self._get_password(password)

        with self._map_exceptions("extract tables", PDFParsingError):
            tables = extract_tables(pdf_path, password=pwd)

            return TableExtractionResultSchema(
                tables=tables,
                table_count=sum(len(page_tables) for page_tables in tables)
            )

    def search_in_pdf(
        self,
        filename: str,
        query: str,
        password: Optional[str] = None
    ) -> SearchResultSchema:
        """
        Search for text in PDF.

        Args:
            filename: PDF filename
            query: Search query string
            password: PDF password (optional)

        Returns:
            SearchResultSchema with search results and context
        """
        pdf_path = self._resolve_and_validate_path(filename)
        pwd = self._get_password(password)

        with self._map_exceptions("search PDF", PDFParsingError):
            result = search_in_pdf(pdf_path, query, password=pwd)

            return SearchResultSchema(
                query=query,
                found=result.get('found', False),
                occurrences=result.get('matches', 0),
                context=result.get('context', [])
            )

    def get_metadata(
        self,
        filename: str,
        password: Optional[str] = None
    ) -> PDFMetadataSchema:
        """
        Get PDF metadata.

        Args:
            filename: PDF filename
            password: PDF password (optional)

        Returns:
            PDFMetadataSchema with PDF metadata
        """
        pdf_path = self._resolve_and_validate_path(filename)
        pwd = self._get_password(password)

        with self._map_exceptions("get metadata", PDFParsingError):
            metadata = get_metadata(pdf_path, password=pwd)

            return PDFMetadataSchema(
                title=metadata.get('/Title'),
                author=metadata.get('/Author'),
                subject=metadata.get('/Subject'),
                creator=metadata.get('/Creator'),
                producer=metadata.get('/Producer'),
                creation_date=str(metadata.get('/CreationDate', '')),
                modification_date=str(metadata.get('/ModDate', ''))
            )

    def extract_savings_statement(
        self,
        filename: str,
        password: Optional[str] = None
    ) -> SavingsAccountStatementSchema:
        """
        Extract savings account statement data.

        Args:
            filename: PDF filename
            password: PDF password (optional)

        Returns:
            SavingsAccountStatementSchema with account statement data
        """
        pdf_path = self._resolve_and_validate_path(filename)
        pwd = self._get_password(password)

        with self._map_exceptions("extract savings statement", PDFParsingError):
            extractor = SavingsAccountExtractor(password=pwd)
            statement = extractor.extract(pdf_path)

            return self._savings_to_schema(statement)

    def extract_credit_card_statement(
        self,
        filename: str,
        password: Optional[str] = None
    ) -> CreditCardStatementSchema:
        """
        Extract credit card statement data.

        Args:
            filename: PDF filename
            password: PDF password (optional)

        Returns:
            CreditCardStatementSchema with credit card statement data
        """
        pdf_path = self._resolve_and_validate_path(filename)
        pwd = self._get_password(password)

        with self._map_exceptions("extract credit card statement", PDFParsingError):
            extractor = CreditCardExtractor(password=pwd)
            statement = extractor.extract(pdf_path)

            return self._credit_card_to_schema(statement)

    # =========================================================================
    # Private Helper Methods
    # =========================================================================

    def _apply_filters(
        self,
        documents: list[PDFDocument],
        filters: dict
    ) -> list[PDFDocument]:
        """Apply filters to document list."""
        result = documents

        if 'tipo' in filters:
            result = [d for d in result if d.info.tipo == filters['tipo']]
        if 'fecha' in filters:
            result = [d for d in result if d.info.fecha == filters['fecha']]

        return result

    def _document_to_schema(self, document: PDFDocument) -> PDFDocumentSchema:
        """Convert PDFDocument domain model to API schema."""
        try:
            encrypted = is_encrypted(document.path) if document.path.exists() else None
            page_count = get_page_count(document.path, password=self.password) if document.path.exists() else None
        except Exception:
            encrypted = None
            page_count = None

        return PDFDocumentSchema(
            path=str(document.path),
            info=PDFDocumentInfoSchema(
                id=document.info.id,
                fecha=document.info.fecha,
                tipo=document.info.tipo,
                numero=document.info.numero,
                filename=document.info.filename
            ),
            exists=document.path.exists(),
            size_bytes=document.path.stat().st_size if document.path.exists() else None,
            is_encrypted=encrypted,
            page_count=page_count
        )

    def _savings_to_schema(self, statement) -> SavingsAccountStatementSchema:
        """Convert savings statement to API schema."""
        return SavingsAccountStatementSchema(
            cuenta={
                "numero_cuenta": statement.cuenta.numero_cuenta,
                "tipo_cuenta": statement.cuenta.tipo_cuenta,
                "titular": statement.cuenta.titular,
                "periodo": statement.cuenta.periodo,
            },
            resumen={
                "saldo_anterior": statement.resumen.saldo_anterior,
                "total_consignaciones": statement.resumen.total_consignaciones,
                "total_retiros": statement.resumen.total_retiros,
                "saldo_actual": statement.resumen.saldo_actual,
            },
            transacciones=[
                {
                    "fecha": t.fecha,
                    "descripcion": t.descripcion,
                    "valor": t.valor,
                    "oficina": t.oficina,
                }
                for t in statement.transacciones
            ]
        )

    def _credit_card_to_schema(self, statement) -> CreditCardStatementSchema:
        """Convert credit card statement to API schema."""
        return CreditCardStatementSchema(
            tarjeta={
                "numero_tarjeta": statement.tarjeta.numero_tarjeta,
                "tipo_tarjeta": statement.tarjeta.tipo_tarjeta,
                "nombre_tarjetahabiente": statement.tarjeta.nombre_tarjetahabiente,
                "periodo": statement.tarjeta.periodo,
            },
            cupo=self._credit_limit_to_dict(statement.cupo) if statement.cupo else None,
            resumen=self._balance_summary_to_dict(statement.resumen) if statement.resumen else None,
            movimientos_pesos=self._currency_statement_to_dict(
                statement.movimientos_pesos, "COP"
            ) if statement.movimientos_pesos else None,
            movimientos_dolares=self._currency_statement_to_dict(
                statement.movimientos_dolares, "USD"
            ) if statement.movimientos_dolares else None,
        )

    def _credit_limit_to_dict(self, cupo) -> dict:
        """Convert credit limit to dict."""
        return {
            "cupo_total": cupo.cupo_total,
            "cupo_disponible": cupo.cupo_disponible,
            "cupo_utilizado": cupo.cupo_utilizado,
        }

    def _balance_summary_to_dict(self, resumen) -> dict:
        """Convert balance summary to dict."""
        return {
            "saldo_anterior": resumen.saldo_anterior,
            "pagos": resumen.pagos,
            "compras": resumen.compras,
            "intereses": resumen.intereses,
            "saldo_actual": resumen.saldo_actual,
        }

    def _currency_statement_to_dict(self, movements, currency: str) -> dict:
        """Convert currency statement to dict."""
        is_usd = currency == "USD"

        return {
            "moneda": currency,
            "transacciones": [
                {
                    "fecha": t.fecha,
                    "descripcion": t.descripcion,
                    "referencia": t.referencia,
                    "valor_pesos": None if is_usd else t.valor_pesos,
                    "valor_dolares": t.valor_dolares if is_usd else None,
                }
                for t in movements.transacciones
            ],
            "total": movements.total,
        }
