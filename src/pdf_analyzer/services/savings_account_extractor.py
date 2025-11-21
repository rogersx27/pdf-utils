"""
Extractor específico para extractos de Cuenta de Ahorros (CTA_AHORROS).

Parsea la información estructurada de los extractos bancarios
de cuentas de ahorro de Bancolombia.
"""

import os
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

from logger import setup_logger, setup_processor_logger
from pdf_analyzer.models import PDFDocument
from pdf_analyzer.services.extractor_service import ExtractorService

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
    Extractor especializado para extractos de Cuenta de Ahorros.

    Parsea extractos de Bancolombia con formato CTA_AHORROS
    extrayendo información de cuenta, resumen y transacciones.
    """

    def __init__(self, password: Optional[str] = None):
        """
        Inicializa el extractor.

        Args:
            password: Contraseña para PDFs protegidos.
        """
        self._password = password or get_default_password()
        self._extractor = ExtractorService(password)
        logger.debug("SavingsAccountExtractor inicializado")

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
        logger.info(f"Extrayendo extracto de cuenta de ahorros: {path.name}")

        # Obtener texto completo
        text_by_page = self._extractor.extract_text_by_page(path)
        full_text = "\n".join(text_by_page.values())

        # Extraer componentes
        account_info = self._extract_account_info(full_text)
        summary = self._extract_summary(full_text)
        transactions = self._extract_transactions(full_text)

        statement = SavingsAccountStatement(
            account_info=account_info,
            summary=summary,
            transactions=transactions,
        )

        logger.info(
            f"Extracto procesado: {len(transactions)} transacciones, "
            f"saldo actual: {summary.saldo_actual}"
        )

        return statement

    def extract_account_info(
        self, document: PDFDocument | Path | str
    ) -> AccountInfo:
        """
        Extrae solo la información de la cuenta.

        Args:
            document: Documento PDF a procesar.

        Returns:
            AccountInfo con los datos de la cuenta.
        """
        path = self._resolve_path(document)
        text_by_page = self._extractor.extract_text_by_page(path)
        full_text = "\n".join(text_by_page.values())
        return self._extract_account_info(full_text)

    def extract_summary(
        self, document: PDFDocument | Path | str
    ) -> FinancialSummary:
        """
        Extrae solo el resumen financiero.

        Args:
            document: Documento PDF a procesar.

        Returns:
            FinancialSummary con los totales del extracto.
        """
        path = self._resolve_path(document)
        text_by_page = self._extractor.extract_text_by_page(path)
        full_text = "\n".join(text_by_page.values())
        return self._extract_summary(full_text)

    def extract_transactions(
        self, document: PDFDocument | Path | str
    ) -> list[Transaction]:
        """
        Extrae solo las transacciones.

        Args:
            document: Documento PDF a procesar.

        Returns:
            Lista de Transaction.
        """
        path = self._resolve_path(document)
        text_by_page = self._extractor.extract_text_by_page(path)
        full_text = "\n".join(text_by_page.values())
        return self._extract_transactions(full_text)

    def _extract_account_info(self, text: str) -> AccountInfo:
        """Extrae información de la cuenta del texto."""
        logger.debug("Extrayendo información de cuenta")

        # Periodo: DESDE: YYYY/MM/DD HASTA: YYYY/MM/DD
        periodo_match = re.search(
            r"DESDE:\s*(\d{4}/\d{2}/\d{2})\s*HASTA:\s*(\d{4}/\d{2}/\d{2})",
            text
        )
        periodo_desde = None
        periodo_hasta = None
        if periodo_match:
            try:
                desde_parts = periodo_match.group(1).split("/")
                periodo_desde = date(
                    int(desde_parts[0]), int(desde_parts[1]), int(desde_parts[2])
                )
                hasta_parts = periodo_match.group(2).split("/")
                periodo_hasta = date(
                    int(hasta_parts[0]), int(hasta_parts[1]), int(hasta_parts[2])
                )
            except (ValueError, IndexError):
                logger.warning("No se pudo parsear el periodo")

        # Tipo de cuenta
        tipo_cuenta = "CUENTA DE AHORROS"
        if "CUENTA CORRIENTE" in text:
            tipo_cuenta = "CUENTA CORRIENTE"

        # Número de cuenta: NÚMERO XXXXXXXXXXX
        numero_match = re.search(r"N[UÚ]MERO\s+(\d+)", text)
        numero = numero_match.group(1) if numero_match else ""

        # Titular: línea después de CUENTA DE AHORROS
        titular = ""
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if "CUENTA DE AHORROS" in line or "CUENTA CORRIENTE" in line:
                if i + 1 < len(lines):
                    titular = lines[i + 1].strip()
                break

        # Sucursal: SUCURSAL XXXX
        sucursal_match = re.search(r"SUCURSAL\s+(.+?)(?:\n|$)", text)
        sucursal = sucursal_match.group(1).strip() if sucursal_match else ""

        # Dirección: línea después del número (si no es SUCURSAL)
        direccion = ""
        for i, line in enumerate(lines):
            if numero and numero in line:
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if not next_line.startswith("SUCURSAL"):
                        direccion = next_line
                break

        return AccountInfo(
            titular=titular,
            numero=numero,
            tipo_cuenta=tipo_cuenta,
            sucursal=sucursal,
            direccion=direccion,
            periodo_desde=periodo_desde,
            periodo_hasta=periodo_hasta,
        )

    def _extract_summary(self, text: str) -> FinancialSummary:
        """Extrae el resumen financiero del texto."""
        logger.debug("Extrayendo resumen financiero")

        def parse_money(pattern: str, txt: str) -> float:
            """Parsea un valor monetario del texto."""
            match = re.search(pattern, txt)
            if match:
                value_str = match.group(1)
                # Limpiar formato: quitar puntos de miles, cambiar coma por punto
                value_str = value_str.replace(".", "").replace(",", ".")
                try:
                    return float(value_str)
                except ValueError:
                    return 0.0
            return 0.0

        # Patrones para extraer valores
        saldo_anterior = parse_money(
            r"SALDO ANTERIOR\s*\$\s*([\d.,]+)", text
        )
        saldo_promedio = parse_money(
            r"SALDO PROMEDIO\s*\$\s*([\d.,]+)", text
        )
        total_abonos = parse_money(
            r"TOTAL ABONOS\s*\$\s*([\d.,]+)", text
        )
        total_cargos = parse_money(
            r"TOTAL CARGOS\s*\$\s*([\d.,]+)", text
        )
        saldo_actual = parse_money(
            r"SALDO ACTUAL\s*\$\s*([\d.,]+)", text
        )
        intereses = parse_money(
            r"(?:VALOR )?INTERESES PAGADOS\s*\$\s*([\d.,]+)", text
        )
        cuentas_cobrar = parse_money(
            r"CUENTAS X COBRAR\s*\$\s*([\d.,]+)", text
        )
        retefuente = parse_money(
            r"RETEFUENTE\s*\$\s*([\d.,]+)", text
        )

        return FinancialSummary(
            saldo_anterior=saldo_anterior,
            saldo_promedio=saldo_promedio,
            total_abonos=total_abonos,
            total_cargos=total_cargos,
            saldo_actual=saldo_actual,
            intereses_pagados=intereses,
            cuentas_por_cobrar=cuentas_cobrar,
            retefuente=retefuente,
        )

    def _extract_transactions(self, text: str) -> list[Transaction]:
        """Extrae las transacciones del texto."""
        logger.debug("Extrayendo transacciones")

        transactions: list[Transaction] = []

        # Patrón para transacciones:
        # FECHA DESCRIPCIÓN ... VALOR SALDO
        # Ejemplos:
        # 29/09 PAGO DE PROV PROTECCION SA 569,576.00 569,576.00
        # 29/09 TRANSFERENCIA A NEQUI -543,500.00 26,076.00
        # 1/04 TRANSFERENCIA DESDE NEQUI 2,560,000.00 3,865,022.88

        # Patrón regex para capturar transacciones
        pattern = re.compile(
            r"^(\d{1,2}/\d{2})\s+"  # Fecha: D/MM o DD/MM
            r"(.+?)\s+"  # Descripción
            r"(-?[\d.,]+)\s+"  # Valor (puede ser negativo)
            r"(-?[\d.,]+)$",  # Saldo
            re.MULTILINE
        )

        for match in pattern.finditer(text):
            fecha = match.group(1)
            descripcion = match.group(2).strip()
            valor_str = match.group(3).replace(".", "").replace(",", ".")
            saldo_str = match.group(4).replace(".", "").replace(",", ".")

            try:
                valor = float(valor_str)
                saldo = float(saldo_str)

                transaction = Transaction(
                    fecha=fecha,
                    descripcion=descripcion,
                    valor=valor,
                    saldo=saldo,
                )
                transactions.append(transaction)

            except ValueError as e:
                logger.warning(f"Error parseando transacción: {e}")
                continue

        logger.debug(f"Transacciones extraídas: {len(transactions)}")
        return transactions

    @staticmethod
    def _resolve_path(document: PDFDocument | Path | str) -> Path:
        """Resuelve la ruta de un documento."""
        if isinstance(document, PDFDocument):
            return document.path
        return Path(document)
