"""
Procesador de datos para extractos de Cuenta de Ahorros usando pandas.
"""

import os
from pathlib import Path
from typing import Optional

import pandas as pd

from logger import setup_logger, setup_processor_logger
from pdf_analyzer import SavingsAccountExtractor
from pdf_analyzer.models import PDFDocument

from .validators import validate_data, ValidationResult

logger = setup_processor_logger(setup_logger, __name__)


def get_default_password() -> Optional[str]:
    """Obtiene la contraseña por defecto desde variable de entorno."""
    return os.environ.get("PDF_PASSWORD")


class SavingsAccountProcessor:
    """
    Procesador de extractos de cuenta de ahorros con pandas.

    Convierte datos extraídos a DataFrames y proporciona validaciones.
    """

    def __init__(self, password: Optional[str] = None):
        """
        Inicializa el procesador.

        Args:
            password: Contraseña para PDFs protegidos.
        """
        self._password = password or get_default_password()
        self._extractor = SavingsAccountExtractor(password)
        logger.debug("SavingsAccountProcessor inicializado")

    def process(
        self, document: PDFDocument | Path | str, validate: bool = True
    ) -> dict:
        """
        Procesa un extracto de cuenta de ahorros.

        Args:
            document: Documento PDF a procesar
            validate: Si True, ejecuta validaciones de datos

        Returns:
            Diccionario con:
                - 'info': Información de la cuenta (dict)
                - 'resumen': Resumen financiero (dict)
                - 'transacciones': DataFrame de transacciones
                - 'validacion': ValidationResult (si validate=True)
        """
        path = self._resolve_path(document)
        logger.info(f"Procesando extracto de cuenta de ahorros: {path.name}")  # pylint: disable=logging-fstring-interpolation

        # Extraer datos usando el extractor existente
        statement = self._extractor.extract(path)

        # Convertir a DataFrame
        transacciones_df = self._to_dataframe(statement)

        # Preparar resultado
        result = {
            "info": statement.account_info.to_dict(),
            "resumen": statement.summary.to_dict(),
            "transacciones": transacciones_df,
        }

        # Validar si se solicita
        if validate:
            validation = validate_data(
                transacciones_df,
                statement.summary.saldo_anterior,
                statement.summary.saldo_actual,
                statement.summary.total_abonos,
                statement.summary.total_cargos,
            )
            result["validacion"] = validation

            if not validation.is_valid:
                logger.warning(f"Validación falló con {len(validation.errors)} errores")  # pylint: disable=logging-fstring-interpolation
            else:
                logger.info("Validación exitosa")

        logger.info(f"Procesadas {len(transacciones_df)} transacciones")  # pylint: disable=logging-fstring-interpolation

        return result

    def _to_dataframe(self, statement) -> pd.DataFrame:
        """
        Convierte transacciones a DataFrame.

        Args:
            statement: SavingsAccountStatement

        Returns:
            DataFrame con las transacciones
        """
        if not statement.transactions:
            return pd.DataFrame(
                columns=["fecha", "descripcion", "valor", "saldo", "tipo", "sucursal", "dcto"]
            )

        # Convertir transacciones a lista de diccionarios
        data = []
        for tx in statement.transactions:
            data.append(
                {
                    "fecha": tx.fecha,
                    "descripcion": tx.descripcion,
                    "valor": tx.valor,
                    "saldo": tx.saldo,
                    "tipo": "credito" if tx.es_credito else "debito",
                    "sucursal": tx.sucursal,
                    "dcto": tx.dcto,
                }
            )

        df = pd.DataFrame(data)

        # Convertir tipos de datos
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
        df["saldo"] = pd.to_numeric(df["saldo"], errors="coerce")

        return df

    def export_to_csv(self, data: dict, output_path: Path):
        """
        Exporta transacciones a CSV.

        Args:  
            data: Diccionario resultado de process()
            output_path: Ruta del archivo CSV de salida
        """
        df = data["transacciones"]
        df.to_csv(output_path, index=False, encoding="utf-8")
        logger.info(f"Exportado a CSV: {output_path}")  # pylint: disable=logging-fstring-interpolation

    def export_to_excel(self, data: dict, output_path: Path):
        """
        Exporta a Excel con múltiples hojas.

        Args:
            data: Diccionario resultado de process()
            output_path: Ruta del archivo Excel de salida
        """
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            # Hoja de transacciones
            data["transacciones"].to_excel(
                writer, sheet_name="Transacciones", index=False
            )

            # Hoja de resumen
            resumen_df = pd.DataFrame([data["resumen"]])
            resumen_df.to_excel(writer, sheet_name="Resumen", index=False)

            # Hoja de información
            info_df = pd.DataFrame([data["info"]])
            info_df.to_excel(writer, sheet_name="Información", index=False)

        logger.info(f"Exportado a Excel: {output_path}")  # pylint: disable=logging-fstring-interpolation

    @staticmethod
    def _resolve_path(document: PDFDocument | Path | str) -> Path:
        """Resuelve la ruta de un documento."""
        if isinstance(document, PDFDocument):
            return document.path
        return Path(document)
