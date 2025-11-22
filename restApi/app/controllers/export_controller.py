"""
Export Controller - HTTP response handler for data export operations.

This controller is responsible for handling HTTP requests/responses
for data processing and export operations. It delegates business logic to
DataProcessorService and uses core utilities for consistent responses.
"""
from typing import Optional, Literal
from fastapi.responses import JSONResponse, FileResponse

from app.controllers.base import BaseController
from app.controllers.concerns import PasswordAwareMixin, BatchOperationMixin
from app.core.decorators import handle_controller_errors
from app.services.export import DataProcessorService


class ExportController(BaseController, PasswordAwareMixin, BatchOperationMixin):
    """
    Controller for data export endpoints.

    Handles HTTP responses for export operations using APIResponse utilities
    and delegates business logic to DataProcessorService.
    """

    def __init__(self, password: Optional[str] = None):
        """
        Initialize controller with service.

        Args:
            password: Default password for encrypted PDFs
        """
        super().__init__()
        self._init_password(password)
        self.service = DataProcessorService(password=password)

    @handle_controller_errors
    async def export_savings_account(
        self,
        filename: str,
        export_format: Literal["csv", "excel"] = "excel",
        output_filename: Optional[str] = None,
        return_file: bool = False
    ) -> JSONResponse | FileResponse:
        """
        Export savings account statement data.

        Args:
            filename: Source PDF filename
            export_format: Export format ('csv' or 'excel')
            output_filename: Custom output filename
            return_file: If True, return file for download

        Returns:
            JSONResponse with export details or FileResponse for download
        """
        result = self.service.export_savings_account(
            filename=filename,
            export_format=export_format,
            output_filename=output_filename
        )

        if return_file:
            return self._file_response(result.output_file)

        return self._export_response(result)

    @handle_controller_errors
    async def export_credit_card(
        self,
        filename: str,
        export_format: Literal["csv", "excel"] = "excel",
        output_filename: Optional[str] = None,
        return_file: bool = False
    ) -> JSONResponse | FileResponse:
        """
        Export credit card statement data.

        Args:
            filename: Source PDF filename
            export_format: Export format ('csv' or 'excel')
            output_filename: Custom output filename
            return_file: If True, return file for download

        Returns:
            JSONResponse with export details or FileResponse for download
        """
        result = self.service.export_credit_card(
            filename=filename,
            export_format=export_format,
            output_filename=output_filename
        )

        if return_file and export_format == "excel":
            return self._file_response(result.output_file)

        return self._export_response(result)

    @handle_controller_errors
    async def validate_savings_data(
        self,
        filename: str
    ) -> JSONResponse:
        """
        Validate savings account data consistency.

        Args:
            filename: Source PDF filename

        Returns:
            JSONResponse with validation results
        """
        result = self.service.validate_savings_data(filename)
        return self._validation_response(result)

    @handle_controller_errors
    async def validate_credit_card_data(
        self,
        filename: str
    ) -> JSONResponse:
        """
        Validate credit card data consistency.

        Args:
            filename: Source PDF filename

        Returns:
            JSONResponse with validation results
        """
        result = self.service.validate_credit_card_data(filename)
        return self._validation_response(result)

    @handle_controller_errors
    async def batch_export_savings(
        self,
        filenames: list[str],
        export_format: Literal["csv", "excel"] = "excel"
    ) -> JSONResponse:
        """
        Batch export multiple savings account statements.

        Args:
            filenames: List of PDF filenames
            export_format: Export format ('csv' or 'excel')

        Returns:
            JSONResponse with batch export results
        """
        def process_file(filename: str):
            return self.service.export_savings_account(
                filename=filename,
                export_format=export_format
            )

        response = await self._batch_process(
            items=filenames,
            processor=process_file,
            item_name_key="filename",
            operation_name="savings export"
        )

        # Add format to meta
        content = response.body.decode()
        import json
        data = json.loads(content)
        data["meta"]["format"] = export_format
        return JSONResponse(content=data, status_code=response.status_code)

    @handle_controller_errors
    async def batch_export_credit_cards(
        self,
        filenames: list[str],
        export_format: Literal["csv", "excel"] = "excel"
    ) -> JSONResponse:
        """
        Batch export multiple credit card statements.

        Args:
            filenames: List of PDF filenames
            export_format: Export format ('csv' or 'excel')

        Returns:
            JSONResponse with batch export results
        """
        def process_file(filename: str):
            return self.service.export_credit_card(
                filename=filename,
                export_format=export_format
            )

        response = await self._batch_process(
            items=filenames,
            processor=process_file,
            item_name_key="filename",
            operation_name="credit card export"
        )

        # Add format to meta
        content = response.body.decode()
        import json
        data = json.loads(content)
        data["meta"]["format"] = export_format
        return JSONResponse(content=data, status_code=response.status_code)

    # -------------------------------------------------------------------------
    # Private helper methods
    # -------------------------------------------------------------------------

    def _export_response(self, result) -> JSONResponse:
        """Create standardized export response."""
        return self._success(
            data=result,
            message=result.message,
            meta={
                "format": result.format,
                "record_count": result.record_count,
                "sheets": result.sheets
            }
        )

    def _validation_response(self, result) -> JSONResponse:
        """Create standardized validation response."""
        status = "valid" if result.is_valid else "invalid"

        return self._success(
            data=result,
            message=f"Data validation completed: {status}",
            meta={
                "is_valid": result.is_valid,
                "record_count": result.record_count,
                "error_count": len(result.errors) if result.errors else 0
            }
        )
