"""
Data Export Service.

Provides data processing and export functionality for bank statements
to CSV, Excel, and other formats.
"""

from .processor_service import DataProcessorService

__all__ = ["DataProcessorService"]
