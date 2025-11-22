"""
Mixin para manejo de contraseñas de PDFs.

Proporciona funcionalidad para obtener y gestionar contraseñas
de PDFs protegidos, incluyendo lectura desde variables de entorno.
"""

import os
from typing import Optional


def get_default_password() -> Optional[str]:
    """
    Obtiene la contraseña por defecto desde variable de entorno.

    Returns:
        Contraseña desde PDF_PASSWORD o None si no está definida.
    """
    return os.environ.get("PDF_PASSWORD")


class PasswordAwareMixin:
    """
    Mixin para servicios que manejan PDFs protegidos con contraseña.

    Proporciona inicialización y acceso a la contraseña,
    con fallback a la variable de entorno PDF_PASSWORD.

    Uso:
        class MyService(PasswordAwareMixin):
            def __init__(self, password: Optional[str] = None):
                self._init_password(password)

            def process(self, path):
                # usar self._password...
    """

    _password: Optional[str] = None

    def _init_password(self, password: Optional[str] = None) -> None:
        """
        Inicializa la contraseña del servicio.

        Args:
            password: Contraseña explícita o None para usar la del entorno.
        """
        self._password = password or get_default_password()

    @property
    def password(self) -> Optional[str]:
        """Retorna la contraseña configurada."""
        return self._password
