"""
Procesador de datos para extractos de Tarjeta de Crédito usando pandas.
"""

import os
from pathlib import Path
from typing import Optional

import pandas as pd

from logger import setup_logger, setup_processor_logger
from pdf_analyzer import CreditCardExtractor
from pdf_analyzer.models import PDFDocument

logger = setup_processor_logger(setup_logger, __name__)


def get_default_password() -> Optional[str]:
    """Obtiene la contraseña por defecto desde variable de entorno."""
    return os.environ.get("PDF_PASSWORD")


class CreditCardProcessor:
    """
    Procesador de extractos de tarjeta de crédito con pandas.

    Convierte datos extraídos a DataFrames por moneda.
    """

    def __init__(self, password: Optional[str] = None):
        """
        Inicializa el procesador.

        Args:
            password: Contraseña para PDFs protegidos.
        """
        self._password = password or get_default_password()
        self._extractor = CreditCardExtractor(password)
        logger.debug("CreditCardProcessor inicializado")

    def process(self, document: PDFDocument | Path | str) -> dict:
        """
        Procesa un extracto de tarjeta de crédito.

        Args:
            document: Documento PDF a procesar

        Returns:
            Diccionario con:
                - 'info': Información de la tarjeta (dict)
                - 'cupos': Información de cupos (dict)
                - 'pesos': DataFrame y resumen en pesos (o None)
                - 'dolares': DataFrame y resumen en dólares (o None)
        """
        path = self._resolve_path(document)
        logger.info(f"Procesando extracto de tarjeta de crédito: {path.name}")  # pylint: disable=logging-fstring-interpolation

        # Extraer datos
        statement = self._extractor.extract(path)

        # Preparar resultado  
        result = {
            "info": statement.card_info.to_dict(),
            "cupos": statement.credit_limit.to_dict(),
            "pesos": None,
            "dolares": None,
        }

        # Procesar pesos si existe
        if statement.pesos_statement:
            pesos_df = self._to_dataframe(statement.pesos_statement.transactions)
            result["pesos"] = {
                "transacciones": pesos_df,
                "resumen": statement.pesos_statement.balance_summary.to_dict(),
                "pago_minimo": statement.pesos_statement.minimum_payment.to_dict(),
                "tasas": statement.pesos_statement.interest_rates.to_dict(),
            }
            logger.info(f"Procesadas {len(pesos_df)} transacciones en pesos")  # pylint: disable=logging-fstring-interpolation

        # Procesar dólares si existe
        if statement.dolares_statement:
            dolares_df = self._to_dataframe(statement.dolares_statement.transactions)
            result["dolares"] = {
                "transacciones": dolares_df,
                "resumen": statement.dolares_statement.balance_summary.to_dict(),
            }
            logger.info(f"Procesadas {len(dolares_df)} transacciones en dólares")  # pylint: disable=logging-fstring-interpolation

        return result

    def _to_dataframe(self, transactions: list) -> pd.DataFrame:
        """
        Convierte transacciones a DataFrame.

        Args:
            transactions: Lista de CreditCardTransaction

        Returns:
            DataFrame con las transacciones
        """
        if not transactions:
            return pd.DataFrame(
                data=None,
                columns=[
                    "fecha",
                    "descripcion",
                    "valor_original",
                    "cargos_abonos",
                    "saldo_diferir",
                    "cuotas",
                    "tipo",
                    "numero_autorizacion",
                ]
            )

        # Convertir a lista de diccionarios
        data = []
        for tx in transactions:
            cuotas = f"{tx.cuota_actual}/{tx.cuota_total}" if tx.cuota_total > 0 else ""
            data.append(
                {
                    "fecha": tx.fecha,
                    "descripcion": tx.descripcion,
                    "valor_original": tx.valor_original,
                    "cargos_abonos": tx.cargos_abonos,
                    "saldo_diferir": tx.saldo_diferir,
                    "cuotas": cuotas,
                    "tipo": "abono" if tx.es_abono else "cargo",
                    "numero_autorizacion": tx.numero_autorizacion,
                }
            )

        df = pd.DataFrame(data)

        # Convertir tipos numéricos
        for col in ["valor_original", "cargos_abonos", "saldo_diferir"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def export_to_csv(self, data: dict, output_dir: Path):
        """
        Exporta transacciones a CSVs separados por moneda.

        Args:
            data: Diccionario resultado de process()
            output_dir: Directorio de salida
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        if data["pesos"]:
            pesos_path = output_dir / "transacciones_pesos.csv"
            data["pesos"]["transacciones"].to_csv(
                pesos_path, index=False, encoding="utf-8"
            )
            logger.info(f"Exportado pesos a CSV: {pesos_path}")  # pylint: disable=logging-fstring-interpolation

        if data["dolares"]:
            dolares_path = output_dir / "transacciones_dolares.csv"
            data["dolares"]["transacciones"].to_csv(
                dolares_path, index=False, encoding="utf-8"
            )
            logger.info(f"Exportado dólares a CSV: {dolares_path}")  # pylint: disable=logging-fstring-interpolation

    def export_to_excel(self, data: dict, output_path: Path):
        """
        Exporta a Excel con hojas por moneda.

        Args:
            data: Diccionario resultado de process()
            output_path: Ruta del archivo Excel
        """
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            # Información general
            info_df = pd.DataFrame([data["info"]])
            info_df.to_excel(writer, sheet_name="Información", index=False)

            cupos_df = pd.DataFrame([data["cupos"]])
            cupos_df.to_excel(writer, sheet_name="Cupos", index=False)

            # Pesos
            if data["pesos"]:
                data["pesos"]["transacciones"].to_excel(
                    writer, sheet_name="Transacciones Pesos", index=False
                )
                resumen_pesos = pd.DataFrame([data["pesos"]["resumen"]])
                resumen_pesos.to_excel(writer, sheet_name="Resumen Pesos", index=False)

            # Dólares
            if data["dolares"]:
                data["dolares"]["transacciones"].to_excel(
                    writer, sheet_name="Transacciones Dólares", index=False
                )
                resumen_dolares = pd.DataFrame([data["dolares"]["resumen"]])
                resumen_dolares.to_excel(
                    writer, sheet_name="Resumen Dólares", index=False
                )

        logger.info(f"Exportado a Excel: {output_path}")  # pylint: disable=logging-fstring-interpolation

    @staticmethod
    def _resolve_path(document: PDFDocument | Path | str) -> Path:
        """Resuelve la ruta de un documento."""
        if isinstance(document, PDFDocument):
            return document.path
        return Path(document)
