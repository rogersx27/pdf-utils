"""
Data Processor Service - Controller for data_processor module.

This service acts as a thin controller layer that delegates all processing logic
to the data_processor module (SavingsAccountProcessor, CreditCardProcessor).

Architecture:
    API Layer (FastAPI) -> DataProcessorService -> data_processor -> pdf_analyzer
    
The data_processor module internally uses pdf_analyzer extractors:
    - SavingsAccountProcessor -> SavingsAccountExtractor
    - CreditCardProcessor -> CreditCardExtractor
"""
import sys
from pathlib import Path
from typing import Optional, Literal

# First import app modules (relative imports work within restApi/)
from app.core.config import settings
from app.core.exceptions import (
    PDFNotFoundError,
    PDFPasswordError,
    InternalServerError
)
from app.schemas.file_operations import (
    DataExportResponse,
    ValidationResultSchema,
)

# Add src to path for pdf_analyzer and data_processor modules
project_root = Path(__file__).parent.parent.parent.parent  # EXTRACTOS/
src_path = project_root / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import processors that handle all extraction and processing logic
from data_processor import SavingsAccountProcessor, CreditCardProcessor


class DataProcessorService:
    """
    Service controller for data processing operations.
    
    Delegates all processing logic to data_processor module, which internally
    uses pdf_analyzer extractors. This service only handles:
    - Path resolution and validation
    - Output directory management
    - Format conversion to API response schemas
    - Error handling and exception mapping
    
    Processing workflow:
        1. Validate PDF path
        2. Call processor.process() -> extracts data using pdf_analyzer
        3. Call processor.export_*() -> exports to desired format
        4. Return API response
    """
    
    def __init__(self, password: Optional[str] = None):
        """
        Initialize service with processors.
        
        Args:
            password: Default password for encrypted PDFs (from settings)
        """
        self.password = password or settings.pdf_password
        # Initialize processors - they handle all extraction logic internally
        self.savings_processor = SavingsAccountProcessor(password=self.password)
        self.credit_processor = CreditCardProcessor(password=self.password)
    
    def export_savings_account(
        self,
        filename: str,
        export_format: Literal["csv", "excel"] = "excel",
        output_filename: Optional[str] = None,
        password: Optional[str] = None
    ) -> DataExportResponse:
        """
        Export savings account statement data.
        
        Delegates to SavingsAccountProcessor which uses SavingsAccountExtractor
        internally to extract data from PDF.
        
        Workflow:
            1. Validate PDF path exists
            2. processor.process(pdf) -> internally calls SavingsAccountExtractor
            3. processor.export_to_*(data, output) -> pandas export
            4. Return response with metadata
        
        Args:
            filename: Source PDF filename (in settings.data_dir)
            export_format: Export format ('csv' or 'excel')
            output_filename: Custom output filename (optional)
            password: PDF password (unused, uses service default)
            
        Returns:
            DataExportResponse with export details
            
        Raises:
            PDFNotFoundError: If PDF doesn't exist
            PDFPasswordError: If password is incorrect
            InternalServerError: If processing fails
        """
        # Step 1: Validate path
        pdf_path = settings.data_dir / filename
        if not pdf_path.exists():
            raise PDFNotFoundError(filename)
        
        # Step 2: Prepare output directory
        output_dir = settings.data_dir.parent / "data-extracted"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Step 3: Process PDF (processor calls extractor internally)
            # validate=False for faster processing in API context
            data = self.savings_processor.process(str(pdf_path), validate=False)
            
            # Step 4: Validate we got transactions
            transactions_df = data.get('transacciones')
            if transactions_df is None or transactions_df.empty:
                raise InternalServerError("No transactions found in PDF")
            
            record_count = len(transactions_df)
            
            # Step 5: Determine output path
            if output_filename:
                output_path = output_dir / output_filename
            else:
                base_name = pdf_path.stem
                extension = ".xlsx" if export_format == "excel" else ".csv"
                output_path = output_dir / f"{base_name}{extension}"
            
            # Step 6: Export using processor's native methods
            if export_format == "excel":
                self.savings_processor.export_to_excel(data, output_path)
                sheets = ["Transacciones", "Resumen", "Información"]
            elif export_format == "csv":
                self.savings_processor.export_to_csv(data, output_path)
                sheets = None
            else:
                raise InternalServerError(
                    f"Format '{export_format}' not supported. Use 'csv' or 'excel'"
                )
            
            # Step 7: Return API response
            return DataExportResponse(
                source_file=filename,
                output_file=str(output_path),
                format=export_format,
                record_count=record_count,
                sheets=sheets,
                message=f"Data exported successfully to {output_path.name}"
            )
            
        except Exception as e:
            # Map exceptions to API exceptions
            if "password" in str(e).lower():
                raise PDFPasswordError(str(e)) from e
            raise InternalServerError(f"Failed to export data: {str(e)}") from e
    
    def export_credit_card(
        self,
        filename: str,
        export_format: Literal["csv", "excel"] = "excel",
        output_filename: Optional[str] = None,
        password: Optional[str] = None
    ) -> DataExportResponse:
        """
        Export credit card statement data.
        
        Delegates to CreditCardProcessor which uses CreditCardExtractor
        internally to extract multi-currency data from PDF.
        
        Workflow:
            1. Validate PDF path exists
            2. processor.process(pdf) -> internally calls CreditCardExtractor
            3. processor.export_to_*(data, output) -> pandas export
            4. Return response with metadata
        
        Args:
            filename: Source PDF filename (in settings.data_dir)
            export_format: Export format ('csv' or 'excel')
            output_filename: Custom output filename (optional)
            password: PDF password (unused, uses service default)
            
        Returns:
            DataExportResponse with export details
            
        Raises:
            PDFNotFoundError: If PDF doesn't exist
            PDFPasswordError: If password is incorrect
            InternalServerError: If processing fails
        """
        # Step 1: Validate path
        pdf_path = settings.data_dir / filename
        if not pdf_path.exists():
            raise PDFNotFoundError(filename)
        
        # Step 2: Prepare output directory
        output_dir = settings.data_dir.parent / "data-extracted"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Step 3: Process PDF (processor calls extractor internally)
            data = self.credit_processor.process(str(pdf_path))
            
            # Step 4: Count transactions from both currencies
            record_count = 0
            if data.get('pesos') and data['pesos'].get('transacciones') is not None:
                record_count += len(data['pesos']['transacciones'])
            if data.get('dolares') and data['dolares'].get('transacciones') is not None:
                record_count += len(data['dolares']['transacciones'])
            
            if record_count == 0:
                raise InternalServerError("No transactions found in PDF")
            
            # Step 5: Determine output path
            if output_filename:
                output_path = output_dir / output_filename
            else:
                base_name = pdf_path.stem
                if export_format == "csv":
                    # CSV exports to directory with multiple files
                    output_path = output_dir / base_name
                else:
                    output_path = output_dir / f"{base_name}.xlsx"
            
            # Step 6: Export using processor's native methods
            if export_format == "excel":
                self.credit_processor.export_to_excel(data, output_path)
                sheets = [
                    "Información", "Cupos", 
                    "Transacciones Pesos", "Resumen Pesos",
                    "Transacciones Dólares", "Resumen Dólares"
                ]
                output_file_display = str(output_path)
            elif export_format == "csv":
                self.credit_processor.export_to_csv(data, output_path)
                sheets = None
                output_file_display = f"{output_path}/ (multiple CSV files)"
            else:
                raise InternalServerError(
                    f"Format '{export_format}' not supported. Use 'csv' or 'excel'"
                )
            
            # Step 7: Return API response
            return DataExportResponse(
                source_file=filename,
                output_file=output_file_display,
                format=export_format,
                record_count=record_count,
                sheets=sheets,
                message="Data exported successfully"
            )
            
        except Exception as e:
            # Map exceptions to API exceptions
            if "password" in str(e).lower():
                raise PDFPasswordError(str(e)) from e
            raise InternalServerError(f"Failed to export data: {str(e)}") from e
    
    def validate_savings_data(
        self,
        filename: str,
        password: Optional[str] = None
    ) -> ValidationResultSchema:
        """
        Validate savings account data consistency.
        
        Delegates to SavingsAccountProcessor with validate=True flag.
        The processor internally:
            1. Extracts data using SavingsAccountExtractor
            2. Validates balance consistency, transaction sums, etc.
        
        Args:
            filename: Source PDF filename (in settings.data_dir)
            password: PDF password (unused, uses service default)
            
        Returns:
            ValidationResultSchema with validation results
            
        Raises:
            PDFNotFoundError: If PDF doesn't exist
            PDFPasswordError: If password is incorrect
            InternalServerError: If processing fails
        """
        # Step 1: Validate path
        pdf_path = settings.data_dir / filename
        if not pdf_path.exists():
            raise PDFNotFoundError(filename)
        
        try:
            # Step 2: Process with validation enabled
            # Processor calls extractor + validation logic internally
            data = self.savings_processor.process(str(pdf_path), validate=True)
            
            # Step 3: Extract validation results
            validation = data.get('validacion')
            record_count = len(data.get('transacciones', []))
            
            # Step 4: Convert to API schema
            if validation:
                return ValidationResultSchema(
                    is_valid=validation.is_valid,
                    errors=validation.errors,
                    warnings=validation.warnings,
                    record_count=record_count
                )
            else:
                # If no validation info, assume success
                return ValidationResultSchema(
                    is_valid=True,
                    errors=[],
                    warnings=[],
                    record_count=record_count
                )
            
        except Exception as e:
            # Map exceptions to API exceptions
            if "password" in str(e).lower():
                raise PDFPasswordError(str(e)) from e
            raise InternalServerError(f"Failed to validate data: {str(e)}") from e
    
    def validate_credit_card_data(
        self,
        filename: str,
        password: Optional[str] = None
    ) -> ValidationResultSchema:
        """
        Validate credit card data by attempting to process it.
        
        Args:
            filename: Source PDF filename
            password: PDF password (currently not used, uses service default)
            
        Returns:
            Validation result
        """
        pdf_path = settings.data_dir / filename
        
        if not pdf_path.exists():
            raise PDFNotFoundError(filename)
        
        try:
            # Process (no validation flag for credit cards)
            data = self.credit_processor.process(str(pdf_path))
            
            # Count records
            record_count = 0
            if data.get('pesos') and data['pesos'].get('transacciones') is not None:
                record_count += len(data['pesos']['transacciones'])
            if data.get('dolares') and data['dolares'].get('transacciones') is not None:
                record_count += len(data['dolares']['transacciones'])
            
            # If we got here without exception, data is valid
            return ValidationResultSchema(
                is_valid=True,
                errors=[],
                warnings=[],
                record_count=record_count
            )
            
        except Exception as e:
            if "password" in str(e).lower():
                raise PDFPasswordError(str(e)) from e
            raise InternalServerError(f"Failed to validate data: {str(e)}") from e
