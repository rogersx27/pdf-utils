"""
PDF Analyzer Service - Controller for pdf_analyzer module.

This service acts as a thin controller layer that delegates all PDF operations
to the pdf_analyzer module's convenience functions and extractors.

Architecture:
    API Layer (FastAPI) -> PDFAnalyzerService -> pdf_analyzer module
    
The pdf_analyzer module provides:
    - Convenience functions: list_pdfs, extract_text, extract_tables, get_metadata, 
      search_in_pdf, analyze, get_page_count, is_encrypted
    - Extractors: SavingsAccountExtractor, CreditCardExtractor
    - Repository: LocalPDFRepository (for listing and getting PDFDocument objects)
"""
import sys
from pathlib import Path
from typing import Optional

# First import app modules (relative imports work within restApi/)
from app.core.config import settings
from app.core.exceptions import (
    PDFNotFoundError,
    PDFPasswordError,
    PDFParsingError,
    InvalidFilenameError,
)
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

# Add src to path for pdf_analyzer module
project_root = Path(__file__).parent.parent.parent.parent  # EXTRACTOS/
src_path = project_root / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import convenience functions and components from pdf_analyzer
from pdf_analyzer import (
    # Repository for document listing
    LocalPDFRepository,
    PDFDocument,
    PDFDocumentInfo,
    # Convenience functions
    list_pdfs,
    extract_text,
    extract_tables,
    get_metadata,
    get_page_count,
    is_encrypted,
    search_in_pdf,
    analyze,
    # Extractors for specialized data extraction
    SavingsAccountExtractor,
    CreditCardExtractor,
)


class PDFAnalyzerService:
    """
    Service controller for PDF analysis operations.
    
    Delegates all PDF operations to pdf_analyzer module.
    This service only handles:
    - Path resolution and validation
    - Error handling and exception mapping
    - Format conversion to API response schemas
    """
    
    def __init__(self, password: Optional[str] = None):
        """
        Initialize service with repository.
        
        Args:
            password: Default password for encrypted PDFs
            
        Note: Most operations use convenience functions directly.
        Repository is only used for listing/getting PDFDocument objects.
        """
        self.password = password or settings.pdf_password
        self.repository = LocalPDFRepository(str(settings.data_dir), password=self.password)
    
    def list_pdfs(self, filters: Optional[dict] = None) -> list[PDFDocumentSchema]:
        """
        List all PDFs in the data directory.
        
        Uses LocalPDFRepository to get PDFDocument objects with parsed metadata.
        
        Args:
            filters: Optional filters (type, date range, etc.)
            
        Returns:
            List of PDFDocumentSchema with parsed filename information
            
        Raises:
            InternalServerError: If listing fails
        """
        try:
            # Get all documents from repository
            documents = self.repository.get_all()
            
            # Apply filters if provided
            if filters:
                if 'tipo' in filters:
                    documents = [d for d in documents if d.info.tipo == filters['tipo']]
                if 'fecha' in filters:
                    documents = [d for d in documents if d.info.fecha == filters['fecha']]
            
            # Convert to API schemas
            return [self._document_to_schema(doc) for doc in documents]
        except Exception as e:
            raise PDFParsingError(f"Failed to list PDFs: {str(e)}") from e
    
    def get_pdf(self, filename: str) -> PDFDocumentSchema:
        """
        Get a single PDF document with parsed metadata.
        
        Uses LocalPDFRepository to get PDFDocument with filename parsing.
        
        Args:
            filename: PDF filename (in settings.data_dir)
            
        Returns:
            PDFDocumentSchema with parsed information
            
        Raises:
            PDFNotFoundError: If PDF doesn't exist
            InvalidFilenameError: If filename doesn't match expected format
        """
        # Step 1: Validate path
        pdf_path = settings.data_dir / filename
        if not pdf_path.exists():
            raise PDFNotFoundError(filename)
        
        try:
            # Step 2: Get document from repository (handles filename parsing)
            document = self.repository.get(str(pdf_path))
            
            # Step 3: Convert to API schema
            return self._document_to_schema(document)
        except ValueError as e:
            raise InvalidFilenameError(filename) from e
    
    def extract_text(self, filename: str, password: Optional[str] = None) -> TextExtractionResultSchema:
        """
        Extract text from PDF.
        
        Delegates to pdf_analyzer.extract_text() and pdf_analyzer.get_page_count()
        convenience functions.
        
        Args:
            filename: PDF filename (in settings.data_dir)
            password: PDF password (optional, uses service default)
            
        Returns:
            TextExtractionResultSchema with extracted text and metadata
            
        Raises:
            PDFNotFoundError: If PDF doesn't exist
            PDFPasswordError: If password is incorrect
            PDFParsingError: If extraction fails
        """
        # Step 1: Validate path
        pdf_path = settings.data_dir / filename
        if not pdf_path.exists():
            raise PDFNotFoundError(filename)
        
        try:
            # Step 2: Use password if provided, otherwise use service default
            pwd = password or self.password
            
            # Step 3: Delegate to pdf_analyzer convenience functions
            text = extract_text(pdf_path, password=pwd)
            page_count = get_page_count(pdf_path, password=pwd)
            
            # Step 4: Return API schema
            return TextExtractionResultSchema(
                text=text,
                page_count=page_count,
                char_count=len(text)
            )
        except Exception as e:
            if "password" in str(e).lower():
                raise PDFPasswordError(str(e)) from e
            raise PDFParsingError(f"Failed to extract text: {str(e)}") from e
    
    def extract_tables(self, filename: str, password: Optional[str] = None) -> TableExtractionResultSchema:
        """
        Extract tables from PDF.
        
        Delegates to pdf_analyzer.extract_tables() convenience function.
        
        Args:
            filename: PDF filename (in settings.data_dir)
            password: PDF password (optional, uses service default)
            
        Returns:
            TableExtractionResultSchema with extracted tables
            
        Raises:
            PDFNotFoundError: If PDF doesn't exist
            PDFPasswordError: If password is incorrect
            PDFParsingError: If extraction fails
        """
        # Step 1: Validate path
        pdf_path = settings.data_dir / filename
        if not pdf_path.exists():
            raise PDFNotFoundError(filename)
        
        try:
            # Step 2: Use password if provided, otherwise use service default
            pwd = password or self.password
            
            # Step 3: Delegate to pdf_analyzer convenience function
            tables = extract_tables(pdf_path, password=pwd)
            
            # Step 4: Return API schema
            return TableExtractionResultSchema(
                tables=tables,
                table_count=sum(len(page_tables) for page_tables in tables)
            )
        except Exception as e:
            if "password" in str(e).lower():
                raise PDFPasswordError(str(e)) from e
            raise PDFParsingError(f"Failed to extract tables: {str(e)}") from e
    
    def search_in_pdf(
        self,
        filename: str,
        query: str,
        password: Optional[str] = None
    ) -> SearchResultSchema:
        """
        Search for text in PDF.
        
        Delegates to pdf_analyzer.search_in_pdf() convenience function.
        
        Args:
            filename: PDF filename (in settings.data_dir)
            query: Search query string
            password: PDF password (optional, uses service default)
            
        Returns:
            SearchResultSchema with search results and context
            
        Raises:
            PDFNotFoundError: If PDF doesn't exist
            PDFPasswordError: If password is incorrect
            PDFParsingError: If search fails
        """
        # Step 1: Validate path
        pdf_path = settings.data_dir / filename
        if not pdf_path.exists():
            raise PDFNotFoundError(filename)
        
        try:
            # Step 2: Use password if provided, otherwise use service default
            pwd = password or self.password
            
            # Step 3: Delegate to pdf_analyzer convenience function
            result = search_in_pdf(pdf_path, query, password=pwd)
            
            # Step 4: Return API schema
            # The search_in_pdf function returns a dict with matches and context
            return SearchResultSchema(
                query=query,
                found=result.get('found', False),
                occurrences=result.get('matches', 0),
                context=result.get('context', [])
            )
        except Exception as e:
            if "password" in str(e).lower():
                raise PDFPasswordError(str(e)) from e
            raise PDFParsingError(f"Failed to search PDF: {str(e)}") from e
    
    def get_metadata(self, filename: str, password: Optional[str] = None) -> PDFMetadataSchema:
        """
        Get PDF metadata.
        
        Delegates to pdf_analyzer.get_metadata() convenience function.
        
        Args:
            filename: PDF filename (in settings.data_dir)
            password: PDF password (optional, uses service default)
            
        Returns:
            PDFMetadataSchema with PDF metadata
            
        Raises:
            PDFNotFoundError: If PDF doesn't exist
            PDFPasswordError: If password is incorrect
            PDFParsingError: If metadata extraction fails
        """
        # Step 1: Validate path
        pdf_path = settings.data_dir / filename
        if not pdf_path.exists():
            raise PDFNotFoundError(filename)
        
        try:
            # Step 2: Use password if provided, otherwise use service default
            pwd = password or self.password
            
            # Step 3: Delegate to pdf_analyzer convenience function
            metadata = get_metadata(pdf_path, password=pwd)
            
            # Step 4: Return API schema
            return PDFMetadataSchema(
                title=metadata.get('/Title'),
                author=metadata.get('/Author'),
                subject=metadata.get('/Subject'),
                creator=metadata.get('/Creator'),
                producer=metadata.get('/Producer'),
                creation_date=str(metadata.get('/CreationDate', '')),
                modification_date=str(metadata.get('/ModDate', ''))
            )
        except Exception as e:
            if "password" in str(e).lower():
                raise PDFPasswordError(str(e)) from e
            raise PDFParsingError(f"Failed to get metadata: {str(e)}") from e
    
    def extract_savings_statement(
        self,
        filename: str,
        password: Optional[str] = None
    ) -> SavingsAccountStatementSchema:
        """
        Extract savings account statement data.
        
        Delegates to SavingsAccountExtractor from pdf_analyzer.
        
        Args:
            filename: PDF filename (in settings.data_dir)
            password: PDF password (optional, uses service default)
            
        Returns:
            SavingsAccountStatementSchema with account statement data
            
        Raises:
            PDFNotFoundError: If PDF doesn't exist
            PDFPasswordError: If password is incorrect
            PDFParsingError: If extraction fails
        """
        # Step 1: Validate path
        pdf_path = settings.data_dir / filename
        if not pdf_path.exists():
            raise PDFNotFoundError(filename)
        
        try:
            # Step 2: Use password if provided, otherwise use service default
            pwd = password or self.password
            
            # Step 3: Delegate to SavingsAccountExtractor
            extractor = SavingsAccountExtractor(password=pwd)
            statement = extractor.extract(pdf_path)
            
            # Step 4: Convert domain model to API schema
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
        except Exception as e:
            if "password" in str(e).lower():
                raise PDFPasswordError(str(e)) from e
            raise PDFParsingError(f"Failed to extract savings statement: {str(e)}") from e
    
    def extract_credit_card_statement(
        self,
        filename: str,
        password: Optional[str] = None
    ) -> CreditCardStatementSchema:
        """
        Extract credit card statement data.
        
        Delegates to CreditCardExtractor from pdf_analyzer.
        
        Args:
            filename: PDF filename (in settings.data_dir)
            password: PDF password (optional, uses service default)
            
        Returns:
            CreditCardStatementSchema with credit card statement data
            
        Raises:
            PDFNotFoundError: If PDF doesn't exist
            PDFPasswordError: If password is incorrect
            PDFParsingError: If extraction fails
        """
        # Step 1: Validate path
        pdf_path = settings.data_dir / filename
        if not pdf_path.exists():
            raise PDFNotFoundError(filename)
        
        try:
            # Step 2: Use password if provided, otherwise use service default
            pwd = password or self.password
            
            # Step 3: Delegate to CreditCardExtractor
            extractor = CreditCardExtractor(password=pwd)
            statement = extractor.extract(pdf_path)
            
            # Step 4: Convert domain model to API schema
            return CreditCardStatementSchema(
                tarjeta={
                    "numero_tarjeta": statement.tarjeta.numero_tarjeta,
                    "tipo_tarjeta": statement.tarjeta.tipo_tarjeta,
                    "nombre_tarjetahabiente": statement.tarjeta.nombre_tarjetahabiente,
                    "periodo": statement.tarjeta.periodo,
                },
                cupo={
                    "cupo_total": statement.cupo.cupo_total if statement.cupo else None,
                    "cupo_disponible": statement.cupo.cupo_disponible if statement.cupo else None,
                    "cupo_utilizado": statement.cupo.cupo_utilizado if statement.cupo else None,
                } if statement.cupo else None,
                resumen={
                    "saldo_anterior": statement.resumen.saldo_anterior if statement.resumen else None,
                    "pagos": statement.resumen.pagos if statement.resumen else None,
                    "compras": statement.resumen.compras if statement.resumen else None,
                    "intereses": statement.resumen.intereses if statement.resumen else None,
                    "saldo_actual": statement.resumen.saldo_actual if statement.resumen else None,
                } if statement.resumen else None,
                movimientos_pesos={
                    "moneda": "COP",
                    "transacciones": [
                        {
                            "fecha": t.fecha,
                            "descripcion": t.descripcion,
                            "referencia": t.referencia,
                            "valor_pesos": t.valor_pesos,
                            "valor_dolares": None,
                        }
                        for t in (statement.movimientos_pesos.transacciones if statement.movimientos_pesos else [])
                    ],
                    "total": statement.movimientos_pesos.total if statement.movimientos_pesos else None,
                } if statement.movimientos_pesos else None,
                movimientos_dolares={
                    "moneda": "USD",
                    "transacciones": [
                        {
                            "fecha": t.fecha,
                            "descripcion": t.descripcion,
                            "referencia": t.referencia,
                            "valor_pesos": None,
                            "valor_dolares": t.valor_dolares,
                        }
                        for t in (statement.movimientos_dolares.transacciones if statement.movimientos_dolares else [])
                    ],
                    "total": statement.movimientos_dolares.total if statement.movimientos_dolares else None,
                } if statement.movimientos_dolares else None,
            )
        except Exception as e:
            if "password" in str(e).lower():
                raise PDFPasswordError(str(e)) from e
            raise PDFParsingError(f"Failed to extract credit card statement: {str(e)}") from e
    
    def _document_to_schema(self, document: PDFDocument) -> PDFDocumentSchema:
        """
        Convert PDFDocument domain model to API schema.
        
        Uses pdf_analyzer convenience functions to enrich the schema with
        additional metadata (encryption status, page count).
        
        Args:
            document: PDFDocument from repository
            
        Returns:
            PDFDocumentSchema for API response
        """
        try:
            # Get additional metadata using convenience functions
            encrypted = is_encrypted(document.path) if document.path.exists() else None
            page_count = get_page_count(document.path, password=self.password) if document.path.exists() else None
        except Exception:
            # If metadata extraction fails, set to None
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
