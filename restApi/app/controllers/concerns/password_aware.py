"""
Password Aware Mixin - Shared password handling for controllers.

Provides password initialization and management for controllers
that interact with encrypted PDFs.
"""
from typing import Optional


class PasswordAwareMixin:
    """
    Mixin for controllers that handle PDF password operations.

    Provides standardized password initialization and storage
    for services that require PDF encryption handling.
    """

    _password: Optional[str] = None

    def _init_password(self, password: Optional[str] = None) -> None:
        """
        Initialize password for PDF operations.

        Args:
            password: Default password for encrypted PDFs.
                     Falls back to PDF_PASSWORD environment variable
                     if not provided.
        """
        self._password = password

    @property
    def password(self) -> Optional[str]:
        """Get the configured password."""
        return self._password
