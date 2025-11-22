"""
Data Processor Service - Controller for data_processor module.

This service acts as a thin controller layer that delegates all processing logic
to the data_processor module (SavingsAccountProcessor, CreditCardProcessor).

Architecture:
    API Layer (FastAPI) -> DataProcessorService -> data_processor -> pdf_analyzer
"""
from pathlib import Path
from typing import Optional, Literal

from app.core.config import settings
from app.core.exceptions import InternalServerError
from app.schemas.file_operations import (
    DataExportResponse,
    ValidationResultSchema,
)

from app.services.concerns import ExportableService
from app.services.setup_imports import (
    SavingsAccountProcessor,
    CreditCardProcessor,
)


class DataProcessorService(ExportableService):
    """
    Service controller for data processing operations.

    Inherits from ExportableService which provides:
    - _resolve_and_validate_path(): Path validation
    - _init_password() / _get_password(): Password handling
    - _map_exceptions(): Exception mapping
    - _get_output_dir(): Output directory management
    - _generate_output_path(): Output path generation
    """

    def __init__(self, password: Optional[str] = None):
        """
        Initialize service with processors.

        Args:
            password: Default password for encrypted PDFs
        """
        self._init_password(password)
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

        Args:
            filename: Source PDF filename
            export_format: Export format ('csv' or 'excel')
            output_filename: Custom output filename (optional)
            password: PDF password (optional)

        Returns:
            DataExportResponse with export details
        """
        pdf_path = self._resolve_and_validate_path(filename)
        output_dir = self._get_output_dir()

        with self._map_exceptions("export savings data"):
            # Process PDF
            data = self.savings_processor.process(str(pdf_path), validate=False)

            # Validate transactions exist
            transactions_df = data.get('transacciones')
            if transactions_df is None or transactions_df.empty:
                raise InternalServerError("No transactions found in PDF")

            record_count = len(transactions_df)

            # Generate output path
            extension = ".xlsx" if export_format == "excel" else ".csv"
            output_path = self._generate_output_path(
                pdf_path,
                output_filename,
                extension,
                output_dir
            )

            # Export
            sheets = self._export_savings(data, output_path, export_format)

            return DataExportResponse(
                source_file=filename,
                output_file=str(output_path),
                format=export_format,
                record_count=record_count,
                sheets=sheets,
                message=f"Data exported successfully to {output_path.name}"
            )

    def export_credit_card(
        self,
        filename: str,
        export_format: Literal["csv", "excel"] = "excel",
        output_filename: Optional[str] = None,
        password: Optional[str] = None
    ) -> DataExportResponse:
        """
        Export credit card statement data.

        Args:
            filename: Source PDF filename
            export_format: Export format ('csv' or 'excel')
            output_filename: Custom output filename (optional)
            password: PDF password (optional)

        Returns:
            DataExportResponse with export details
        """
        pdf_path = self._resolve_and_validate_path(filename)
        output_dir = self._get_output_dir()

        with self._map_exceptions("export credit card data"):
            # Process PDF
            data = self.credit_processor.process(str(pdf_path))

            # Count transactions
            record_count = self._count_credit_card_transactions(data)
            if record_count == 0:
                raise InternalServerError("No transactions found in PDF")

            # Generate output path
            output_path, output_display = self._get_credit_card_output_path(
                pdf_path,
                output_filename,
                export_format,
                output_dir
            )

            # Export
            sheets = self._export_credit_card(data, output_path, export_format)

            return DataExportResponse(
                source_file=filename,
                output_file=output_display,
                format=export_format,
                record_count=record_count,
                sheets=sheets,
                message="Data exported successfully"
            )

    def validate_savings_data(
        self,
        filename: str,
        password: Optional[str] = None
    ) -> ValidationResultSchema:
        """
        Validate savings account data consistency.

        Args:
            filename: Source PDF filename
            password: PDF password (optional)

        Returns:
            ValidationResultSchema with validation results
        """
        pdf_path = self._resolve_and_validate_path(filename)

        with self._map_exceptions("validate savings data"):
            data = self.savings_processor.process(str(pdf_path), validate=True)

            validation = data.get('validacion')
            record_count = len(data.get('transacciones', []))

            return self._validation_to_schema(validation, record_count)

    def validate_credit_card_data(
        self,
        filename: str,
        password: Optional[str] = None
    ) -> ValidationResultSchema:
        """
        Validate credit card data by attempting to process it.

        Args:
            filename: Source PDF filename
            password: PDF password (optional)

        Returns:
            ValidationResultSchema with validation results
        """
        pdf_path = self._resolve_and_validate_path(filename)

        with self._map_exceptions("validate credit card data"):
            data = self.credit_processor.process(str(pdf_path))
            record_count = self._count_credit_card_transactions(data)

            # If we got here without exception, data is valid
            return ValidationResultSchema(
                is_valid=True,
                errors=[],
                warnings=[],
                record_count=record_count
            )

    # =========================================================================
    # Private Helper Methods
    # =========================================================================

    def _count_credit_card_transactions(self, data: dict) -> int:
        """Count total transactions from both currencies."""
        count = 0
        if data.get('pesos') and data['pesos'].get('transacciones') is not None:
            count += len(data['pesos']['transacciones'])
        if data.get('dolares') and data['dolares'].get('transacciones') is not None:
            count += len(data['dolares']['transacciones'])
        return count

    def _export_savings(
        self,
        data: dict,
        output_path: Path,
        export_format: str
    ) -> Optional[list[str]]:
        """Export savings data and return sheet names."""
        if export_format == "excel":
            self.savings_processor.export_to_excel(data, output_path)
            return ["Transacciones", "Resumen", "Información"]
        elif export_format == "csv":
            self.savings_processor.export_to_csv(data, output_path)
            return None
        else:
            raise InternalServerError(
                f"Format '{export_format}' not supported. Use 'csv' or 'excel'"
            )

    def _export_credit_card(
        self,
        data: dict,
        output_path: Path,
        export_format: str
    ) -> Optional[list[str]]:
        """Export credit card data and return sheet names."""
        if export_format == "excel":
            self.credit_processor.export_to_excel(data, output_path)
            return [
                "Información", "Cupos",
                "Transacciones Pesos", "Resumen Pesos",
                "Transacciones Dólares", "Resumen Dólares"
            ]
        elif export_format == "csv":
            self.credit_processor.export_to_csv(data, output_path)
            return None
        else:
            raise InternalServerError(
                f"Format '{export_format}' not supported. Use 'csv' or 'excel'"
            )

    def _get_credit_card_output_path(
        self,
        pdf_path: Path,
        output_filename: Optional[str],
        export_format: str,
        output_dir: Path
    ) -> tuple[Path, str]:
        """
        Get output path for credit card export.

        Returns tuple of (actual_path, display_path) because CSV exports
        to a directory with multiple files.
        """
        if output_filename:
            output_path = output_dir / output_filename
            return output_path, str(output_path)

        base_name = pdf_path.stem
        if export_format == "csv":
            output_path = output_dir / base_name
            return output_path, f"{output_path}/ (multiple CSV files)"
        else:
            output_path = output_dir / f"{base_name}.xlsx"
            return output_path, str(output_path)

    def _validation_to_schema(
        self,
        validation,
        record_count: int
    ) -> ValidationResultSchema:
        """Convert validation result to API schema."""
        if validation:
            return ValidationResultSchema(
                is_valid=validation.is_valid,
                errors=validation.errors,
                warnings=validation.warnings,
                record_count=record_count
            )
        else:
            return ValidationResultSchema(
                is_valid=True,
                errors=[],
                warnings=[],
                record_count=record_count
            )
