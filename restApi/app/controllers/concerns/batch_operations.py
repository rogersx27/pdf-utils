"""
Batch Operations Mixin - Generic batch processing for controllers.

Provides reusable batch operation patterns to avoid code duplication
in controllers that process multiple items.
"""
import logging
from typing import Any, Callable, TypeVar
from fastapi.responses import JSONResponse

from app.core.responses import APIResponse

T = TypeVar('T')

logger = logging.getLogger(__name__)


class BatchOperationMixin:
    """
    Mixin for controllers that perform batch operations.

    Provides a generic pattern for processing multiple items
    with consistent error handling and response formatting.
    """

    async def _batch_process(
        self,
        items: list[Any],
        processor: Callable[[Any], T],
        item_name_key: str = "filename",
        operation_name: str = "batch operation"
    ) -> JSONResponse:
        """
        Process multiple items with consistent error handling.

        Args:
            items: List of items to process
            processor: Callable that processes each item and returns a result
            item_name_key: Key name for identifying items in error messages
            operation_name: Name of the operation for logging/messages

        Returns:
            JSONResponse with successful and failed results
        """
        results: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []

        for item in items:
            item_id = item if isinstance(item, str) else getattr(item, item_name_key, str(item))
            try:
                result = processor(item)
                # Auto-convert Pydantic models
                if hasattr(result, 'model_dump'):
                    result = result.model_dump()
                results.append(result)
            except Exception as e:
                logger.warning(
                    f"Batch {operation_name} failed for {item_id}: {str(e)}"
                )
                errors.append({
                    item_name_key: item_id,
                    "error": str(e)
                })

        success_count = len(results)
        error_count = len(errors)

        return APIResponse.success(
            data={
                "successful": results,
                "failed": errors
            },
            message=f"Batch {operation_name} completed: {success_count} successful, {error_count} failed",
            meta={
                "total": len(items),
                "successful_count": success_count,
                "failed_count": error_count
            }
        )
