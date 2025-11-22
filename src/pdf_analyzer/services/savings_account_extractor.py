"""
Extractor de cuentas de ahorro que usa BancolombiaExtractor como motor.

Este extractor es un wrapper que adapta BancolombiaExtractor a la interfaz
esperada por pdf_analyzer manteniendo compatibilidad con el sistema existente.
"""

import os
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

from logger import setup_logger, setup_processor_logger
from pdf_analyzer.models import PDFDocument
from pdf_analyzer.services.bancolombia_extractor import BancolombiaExtractor, Transaction as BancoTransaction

logger = setup_processor_logger(setup_logger, __name__)


def get_default_password() -> Optional[str]:
    """Obtiene la contraseña por defecto desde variable de entorno."""
    return os.environ.get("PDF_PASSWORD")


@dataclass
class AccountInfo:
    """Información de la cuenta bancaria."""

    titular: str
    numero: str
    tipo_cuenta: str
    sucursal: str
    direccion: str
    periodo_desde: Optional[date] = None
    periodo_hasta: Optional[date] = None

    def to_dict(self) -> dict:
        return {
            "titular": self.titular,
            "numero": self.numero,
            "tipo_cuenta": self.tipo_cuenta,
            "sucursal": self.sucursal,
            "direccion": self.direccion,
            "periodo_desde": self.periodo_desde.isoformat() if self.periodo_desde else None,
            "periodo_hasta": self.periodo_hasta.isoformat() if self.periodo_hasta else None,
        }


@dataclass
class FinancialSummary:
    """Resumen financiero del extracto."""

    saldo_anterior: float = 0.0
    saldo_promedio: float = 0.0
    total_abonos: float = 0.0
    total_cargos: float = 0.0
    saldo_actual: float = 0.0
    intereses_pagados: float = 0.0
    cuentas_por_cobrar: float = 0.0
    retefuente: float = 0.0

    def to_dict(self) -> dict:
        return {
            "saldo_anterior": self.saldo_anterior,
            "saldo_promedio": self.saldo_promedio,
            "total_abonos": self.total_abonos,
            "total_cargos": self.total_cargos,
            "saldo_actual": self.saldo_actual,
            "intereses_pagados": self.intereses_pagados,
            "cuentas_por_cobrar": self.cuentas_por_cobrar,
            "retefuente": self.retefuente,
        }


@dataclass
class Transaction:
    """Transacción individual del extracto."""

    fecha: str
    descripcion: str
    valor: float
    saldo: float
    sucursal: str = ""
    dcto: str = ""

    @property
    def es_credito(self) -> bool:
        """Retorna True si es un abono (crédito)."""
        return self.valor > 0

    @property
    def es_debito(self) -> bool:
        """Retorna True si es un cargo (débito)."""
        return self.valor < 0

    def to_dict(self) -> dict:
        return {
            "fecha": self.fecha,
            "descripcion": self.descripcion,
            "valor": self.valor,
            "saldo": self.saldo,
            "sucursal": self.sucursal,
            "dcto": self.dcto,
            "tipo": "credito" if self.es_credito else "debito",
        }


@dataclass
class SavingsAccountStatement:
    """Extracto completo de cuenta de ahorros."""

    account_info: AccountInfo
    summary: FinancialSummary
    transactions: list[Transaction] = field(default_factory=list)

    @property
    def total_transactions(self) -> int:
        return len(self.transactions)

    @property
    def total_creditos(self) -> float:
        return sum(t.valor for t in self.transactions if t.es_credito)

    @property
    def total_debitos(self) -> float:
        return sum(t.valor for t in self.transactions if t.es_debito)

    def to_dict(self) -> dict:
        return {
            "account_info": self.account_info.to_dict(),
            "summary": self.summary.to_dict(),
            "transactions": [t.to_dict() for t in self.transactions],
            "total_transactions": self.total_transactions,
        }


class SavingsAccountExtractor:
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
        self._password = password or get_default_password()
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
        logger.info(f"Extracting savings account statement: {path.name}")  # pylint: disable=logging-fstring-interpolation

        # Usa BancolombiaExtractor para la extracción
        data = self._bancolombia.extract_text_sections(str(path))

        # Convierte a las clases esperadas
        account_info = self._convert_account_info(data)
        summary = self._convert_summary(data)
        transactions = self._convert_transactions(data['transactions'])

        statement = SavingsAccountStatement(
            account_info=account_info,
            summary=summary,
            transactions=transactions,
        )

        logger.info(  # pylint: disable=logging-fstring-interpolation
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
    ) -> list[Transaction]:
        """Extrae solo las transacciones."""
        path = self._resolve_path(document)
        data = self._bancolombia.extract_text_sections(str(path))
        return self._convert_transactions(data['transactions'])

    def _convert_account_info(self, data: dict) -> AccountInfo:
        """Convierte header a AccountInfo."""
        header = data.get('header', {})

        # Parsear fechas si están disponibles
        periodo_desde = None
        periodo_hasta = None
        if 'period_start' in header and header['period_start']:
            try:
                parts = header['period_start'].split('/')
                if len(parts) == 3:
                    periodo_desde = date(int(parts[0]), int(parts[1]), int(parts[2]))
            except (ValueError, IndexError):
                pass

        if 'period_end' in header and header['period_end']:
            try:
                parts = header['period_end'].split('/')
                if len(parts) == 3:
                    periodo_hasta = date(int(parts[0]), int(parts[1]), int(parts[2]))
            except (ValueError, IndexError):
                pass

        return AccountInfo(
            titular=header.get('account_holder', ''),
            numero=header.get('account_number', ''),
            tipo_cuenta="CUENTA DE AHORROS",
            sucursal="",
            direccion="",
            periodo_desde=periodo_desde,
            periodo_hasta=periodo_hasta,
        )

    def _convert_summary(self, data: dict) -> FinancialSummary:
        """Convierte summary a FinancialSummary."""
        summary = data.get('summary', {})

        return FinancialSummary(
            saldo_anterior=summary.get('previous_balance', 0.0),
            saldo_promedio=0.0,  # No disponible en bancolombia_extractor
            total_abonos=summary.get('total_credits', 0.0),
            total_cargos=summary.get('total_debits', 0.0),
            saldo_actual=summary.get('current_balance', 0.0),
            intereses_pagados=0.0,
            cuentas_por_cobrar=0.0,
            retefuente=0.0,
        )

    def _convert_transactions(self, banco_transactions: list) -> list[Transaction]:
        """Convierte Transaction de Bancolombia a Transaction de pdf_analyzer."""
        transactions = []

        for bt in banco_transactions:
            # bt puede ser un objeto BancoTransaction o un dict
            if isinstance(bt, BancoTransaction):
                fecha = bt.date
                descripcion = bt.description
                valor = bt.amount
                saldo = bt.balance if bt.balance is not None else 0.0
            else:
                # Es un dict
                fecha = bt.get('date', '')
                descripcion = bt.get('description', '')
                valor = bt.get('amount', 0.0)
                saldo = bt.get('balance', 0.0)

            transaction = Transaction(
                fecha=fecha,
                descripcion=descripcion,
                valor=valor,
                saldo=saldo,
            )
            transactions.append(transaction)

        return transactions

    @staticmethod
    def _resolve_path(document: PDFDocument | Path | str) -> Path:
        """Resuelve la ruta de un documento."""
        if isinstance(document, PDFDocument):
            return document.path
        return Path(document)
