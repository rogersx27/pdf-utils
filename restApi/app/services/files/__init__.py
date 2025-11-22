"""
File Management Service.

Provides file operations for PDFs: copy, move, rename, delete,
organization by type/year, and registry generation.
"""

from .manager_service import FileManagerService

__all__ = ["FileManagerService"]
