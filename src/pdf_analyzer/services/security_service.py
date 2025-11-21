"""
Servicio de seguridad para PDFs.

Proporciona funcionalidades para gestionar contraseñas
y encriptación de documentos PDF.
"""

import os
from pathlib import Path
from typing import Optional

from pypdf import PdfReader, PdfWriter

from logger import setup_logger, setup_processor_logger

from pdf_analyzer.models import PDFDocument

logger = setup_processor_logger(setup_logger, __name__)


def get_default_password() -> Optional[str]:
    """Obtiene la contraseña por defecto desde variable de entorno."""
    return os.environ.get("PDF_PASSWORD")


class SecurityService:
    """
    Servicio para gestión de seguridad de PDFs.

    Permite agregar, quitar y verificar contraseñas en documentos PDF.
    """

    def __init__(self, password: Optional[str] = None):
        """
        Inicializa el servicio de seguridad.

        Args:
            password: Contraseña por defecto para operaciones.
        """
        self._password = password or get_default_password()
        logger.debug("SecurityService inicializado")

    def is_encrypted(self, document: PDFDocument | Path | str) -> bool:
        """
        Verifica si un PDF está encriptado.

        Args:
            document: Documento a verificar.

        Returns:
            True si está encriptado.
        """
        path = self._resolve_path(document)
        reader = PdfReader(path)
        return reader.is_encrypted

    def remove_password(
        self,
        document: PDFDocument | Path | str,
        output_path: Optional[Path | str] = None,
        password: Optional[str] = None,
    ) -> Path:
        """
        Quita la contraseña de un PDF.

        Args:
            document: Documento protegido.
            output_path: Ruta de salida. Si es None, agrega '_unlocked'.
            password: Contraseña del PDF.

        Returns:
            Ruta al archivo sin contraseña.

        Raises:
            ValueError: Si la contraseña es incorrecta o el PDF no está encriptado.
        """
        path = self._resolve_path(document)
        pwd = password or self._password

        logger.debug(f"Quitando contraseña de: {path.name}")

        reader = PdfReader(path)

        if not reader.is_encrypted:
            logger.warning(f"PDF no está encriptado: {path.name}")
            raise ValueError(f"El PDF no está encriptado: {path}")

        if not reader.decrypt(pwd or ""):
            logger.error(f"Contraseña incorrecta para: {path.name}")
            raise ValueError(f"Contraseña incorrecta para: {path}")

        # Determinar ruta de salida
        if output_path is None:
            output_path = path.parent / f"{path.stem}_unlocked{path.suffix}"
        output_path = Path(output_path)

        # Escribir PDF sin contraseña
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        if reader.metadata:
            writer.add_metadata(reader.metadata)

        with open(output_path, "wb") as f:
            writer.write(f)

        logger.info(f"PDF sin contraseña: {output_path.name}")
        return output_path

    def add_password(
        self,
        document: PDFDocument | Path | str,
        output_path: Optional[Path | str] = None,
        user_password: Optional[str] = None,
        owner_password: Optional[str] = None,
    ) -> Path:
        """
        Agrega contraseña a un PDF.

        Args:
            document: Documento a proteger.
            output_path: Ruta de salida. Si es None, agrega '_locked'.
            user_password: Contraseña para abrir el PDF.
            owner_password: Contraseña de propietario.

        Returns:
            Ruta al archivo protegido.
        """
        path = self._resolve_path(document)
        user_pwd = user_password or self._password

        if not user_pwd:
            raise ValueError("Se requiere una contraseña")

        owner_pwd = owner_password or user_pwd

        logger.debug(f"Agregando contraseña a: {path.name}")

        reader = PdfReader(path)

        # Si está encriptado, desencriptar primero
        if reader.is_encrypted:
            if not reader.decrypt(self._password or ""):
                raise ValueError("No se pudo desencriptar el PDF existente")

        # Determinar ruta de salida
        if output_path is None:
            output_path = path.parent / f"{path.stem}_locked{path.suffix}"
        output_path = Path(output_path)

        # Escribir PDF con contraseña
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        if reader.metadata:
            writer.add_metadata(reader.metadata)

        writer.encrypt(
            user_password=user_pwd,
            owner_password=owner_pwd,
            permissions_flag=0xFFFF,
        )

        with open(output_path, "wb") as f:
            writer.write(f)

        logger.info(f"PDF protegido: {output_path.name}")
        return output_path

    def change_password(
        self,
        document: PDFDocument | Path | str,
        new_password: str,
        current_password: Optional[str] = None,
        output_path: Optional[Path | str] = None,
    ) -> Path:
        """
        Cambia la contraseña de un PDF.

        Args:
            document: Documento a modificar.
            new_password: Nueva contraseña.
            current_password: Contraseña actual.
            output_path: Ruta de salida.

        Returns:
            Ruta al archivo con nueva contraseña.
        """
        path = self._resolve_path(document)
        current_pwd = current_password or self._password

        logger.debug(f"Cambiando contraseña de: {path.name}")

        reader = PdfReader(path)

        if reader.is_encrypted:
            if not reader.decrypt(current_pwd or ""):
                raise ValueError("Contraseña actual incorrecta")

        # Determinar ruta de salida
        if output_path is None:
            output_path = path.parent / f"{path.stem}_newpwd{path.suffix}"
        output_path = Path(output_path)

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        if reader.metadata:
            writer.add_metadata(reader.metadata)

        writer.encrypt(user_password=new_password, owner_password=new_password)

        with open(output_path, "wb") as f:
            writer.write(f)

        logger.info(f"Contraseña cambiada: {output_path.name}")
        return output_path

    def batch_remove_password(
        self,
        documents: list[PDFDocument | Path | str],
        output_dir: Optional[Path | str] = None,
        password: Optional[str] = None,
    ) -> list[dict]:
        """
        Quita contraseña de múltiples PDFs.

        Args:
            documents: Lista de documentos.
            output_dir: Directorio de salida.
            password: Contraseña de los PDFs.

        Returns:
            Lista de resultados por documento.
        """
        results = []
        pwd = password or self._password

        for doc in documents:
            path = self._resolve_path(doc)
            result = {"input": path.name, "success": False, "output": None, "error": None}

            try:
                if output_dir:
                    output_path = Path(output_dir) / path.name
                else:
                    output_path = None

                out = self.remove_password(doc, output_path, pwd)
                result["success"] = True
                result["output"] = str(out)
            except Exception as e:
                result["error"] = str(e)
                logger.error(f"Error en {path.name}: {e}")

            results.append(result)

        success = sum(1 for r in results if r["success"])
        logger.info(f"Batch completado: {success}/{len(results)} exitosos")

        return results

    @staticmethod
    def _resolve_path(document: PDFDocument | Path | str) -> Path:
        """Resuelve la ruta de un documento."""
        if isinstance(document, PDFDocument):
            return document.path
        return Path(document)
