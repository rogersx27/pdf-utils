"""
Extractor de cuentas de ahorro que usa BancolombiaExtractor como motor.

Este extractor es un wrapper que adapta BancolombiaExtractor a la interfaz
esperada por pdf_analyzer manteniendo compatibilidad con el sistema existente.
"""

from datetime import date
from pathlib import Path
from typing import Optional

from logger import setup_logger, setup_processor_logger
from pdf_analyzer.models import (
    PDFDocument,
    AccountInfo,
    FinancialSummary,
    SavingsTransaction,
    SavingsAccountStatement,
    Transaction as BancoTransaction,
)
from pdf_analyzer.services.extractors.bancolombia import BancolombiaExtractor
from pdf_analyzer.concerns import PathResolvableMixin, PasswordAwareMixin

logger = setup_processor_logger(setup_logger, __name__)


class SavingsAccountExtractor(PathResolvableMixin, PasswordAwareMixin):
    """
    Extractor para cuentas de ahorro que usa BancolombiaExtractor.

    Este es un wrapper que adapta la salida de BancolombiaExtractor
    a las clases específicas esperadas por el sistema.
    """

    def __init__(self, password: Optional[str] = None):
        """
        Inicializa el extractor.

        Args:
            password: Contraseña para PDFs protegidos.
        """
        self._init_password(password)
        self._bancolombia = BancolombiaExtractor(password=self._password)
        logger.debug("SavingsAccountExtractor initialized (using BancolombiaExtractor)")

    def extract(
        self, document: PDFDocument | Path | str
    ) -> SavingsAccountStatement:
        """
        Extrae toda la información del extracto de cuenta de ahorros.

        Args:
            document: Documento PDF a procesar.

        Returns:
            SavingsAccountStatement con toda la información extraída.
        """
        path = self._resolve_path(document)
        logger.info(f"Extracting savings account statement: {path.name}")

        # Usa BancolombiaExtractor para la extracción
        data = self._bancolombia.extract_text_sections(str(path))

        # Convierte a las clases esperadas
        account_info = self._convert_account_info(data)
        summary = self._convert_summary(data)
        transactions = self._convert_transactions(data["transactions"])

        statement = SavingsAccountStatement(
            account_info=account_info,
            summary=summary,
            transactions=transactions,
        )

        logger.info(
            f"Statement processed: {len(transactions)} transactions, "
            f"current balance: {summary.saldo_actual}"
        )

        return statement

    def extract_account_info(
        self, document: PDFDocument | Path | str
    ) -> AccountInfo:
        """Extrae solo la información de la cuenta."""
        path = self._resolve_path(document)
        data = self._bancolombia.extract_text_sections(str(path))
        return self._convert_account_info(data)

    def extract_summary(
        self, document: PDFDocument | Path | str
    ) -> FinancialSummary:
        """Extrae solo el resumen financiero."""
        path = self._resolve_path(document)
        data = self._bancolombia.extract_text_sections(str(path))
        return self._convert_summary(data)

    def extract_transactions(
        self, document: PDFDocument | Path | str
    ) -> list[SavingsTransaction]:
        """Extrae solo las transacciones."""
        path = self._resolve_path(document)
        data = self._bancolombia.extract_text_sections(str(path))
        return self._convert_transactions(data["transactions"])

    def _convert_account_info(self, data: dict) -> AccountInfo:
        """Convierte header a AccountInfo."""
        header = data.get("header", {})

        # Parsear fechas si están disponibles
        periodo_desde = None
        periodo_hasta = None
        if "period_start" in header and header["period_start"]:
            try:
                parts = header["period_start"].split("/")
                if len(parts) == 3:
                    periodo_desde = date(int(parts[0]), int(parts[1]), int(parts[2]))
            except (ValueError, IndexError):
                pass

        if "period_end" in header and header["period_end"]:
            try:
                parts = header["period_end"].split("/")
                if len(parts) == 3:
                    periodo_hasta = date(int(parts[0]), int(parts[1]), int(parts[2]))
            except (ValueError, IndexError):
                pass

        return AccountInfo(
            titular=header.get("account_holder", ""),
            numero=header.get("account_number", ""),
            tipo_cuenta="CUENTA DE AHORROS",
            sucursal="",
            direccion="",
            periodo_desde=periodo_desde,
            periodo_hasta=periodo_hasta,
        )

    def _convert_summary(self, data: dict) -> FinancialSummary:
        """Convierte summary a FinancialSummary."""
        summary = data.get("summary", {})

        return FinancialSummary(
            saldo_anterior=summary.get("previous_balance", 0.0),
            saldo_promedio=0.0,  # No disponible en bancolombia_extractor
            total_abonos=summary.get("total_credits", 0.0),
            total_cargos=summary.get("total_debits", 0.0),
            saldo_actual=summary.get("current_balance", 0.0),
            intereses_pagados=0.0,
            cuentas_por_cobrar=0.0,
            retefuente=0.0,
        )

    def _convert_transactions(self, banco_transactions: list) -> list[SavingsTransaction]:
        """Convierte Transaction de Bancolombia a SavingsTransaction."""
        transactions: list[SavingsTransaction] = []

        for bt in banco_transactions:
            # bt puede ser un objeto BancoTransaction o un dict
            if isinstance(bt, BancoTransaction):
                fecha = bt.date
                descripcion = bt.description
                valor = bt.amount
                saldo = bt.balance if bt.balance is not None else 0.0
            else:
                # Es un dict
                fecha = bt.get("date", "")
                descripcion = bt.get("description", "")
                valor = bt.get("amount", 0.0)
                saldo = bt.get("balance", 0.0)

            transaction = SavingsTransaction(
                fecha=fecha,
                descripcion=descripcion,
                valor=valor,
                saldo=saldo,
            )
            transactions.append(transaction)

        return transactions
