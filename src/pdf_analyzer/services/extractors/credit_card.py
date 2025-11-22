"""
Extractor de tarjetas de crédito que usa BancolombiaExtractor como motor.

Este extractor es un wrapper que adapta BancolombiaExtractor a la interfaz
esperada por pdf_analyzer manteniendo compatibilidad con el sistema existente.
"""

import re
from datetime import date
from pathlib import Path
from typing import Optional

from logger import setup_logger, setup_processor_logger
from pdf_analyzer.models import (
    PDFDocument,
    CardInfo,
    CreditLimit,
    InterestRates,
    BalanceSummary,
    MinimumPayment,
    CreditCardTransaction,
    CurrencyStatement,
    CreditCardStatement,
    Transaction as BancoTransaction,
)
from pdf_analyzer.services.extractors.bancolombia import BancolombiaExtractor
from pdf_analyzer.services.extractors.base import ExtractorService
from pdf_analyzer.concerns import PathResolvableMixin, PasswordAwareMixin

logger = setup_processor_logger(setup_logger, __name__)


class CreditCardExtractor(PathResolvableMixin, PasswordAwareMixin):
    """
    Extractor para tarjetas de crédito que usa BancolombiaExtractor.

    Este es un wrapper que usa BancolombiaExtractor como motor principal
    y ExtractorService para funcionalidad adicional específica de tarjetas.
    """

    def __init__(self, password: Optional[str] = None):
        """
        Inicializa el extractor.

        Args:
            password: Contraseña para PDFs protegidos.
        """
        self._init_password(password)
        self._bancolombia = BancolombiaExtractor(password=self._password)
        self._extractor = ExtractorService(password=self._password)
        logger.debug("CreditCardExtractor initialized (using BancolombiaExtractor)")

    def extract(self, document: PDFDocument | Path | str) -> CreditCardStatement:
        """
        Extrae toda la información del extracto de tarjeta de crédito.

        Args:
            document: Documento PDF a procesar.

        Returns:
            CreditCardStatement con toda la información extraída.
        """
        path = self._resolve_path(document)
        logger.info(f"Extracting credit card statement: {path.name}")

        # Obtener texto por página para manejar múltiples monedas
        text_by_page = self._extractor.extract_text_by_page(path)

        # Identificar páginas por moneda
        pesos_text = ""
        dolares_text = ""

        for content in text_by_page.values():
            if "ESTADO DE CUENTA EN: PESOS" in content:
                pesos_text = content
            elif "ESTADO DE CUENTA EN: DOLARES" in content:
                dolares_text = content

        # Usar el primer texto disponible para info general
        first_text = pesos_text or dolares_text or "\n".join(text_by_page.values())

        # Extraer componentes
        card_info = self._extract_card_info(first_text)
        credit_limit = self._extract_credit_limit(first_text)

        pesos_statement = None
        dolares_statement = None

        if pesos_text:
            pesos_statement = self._extract_currency_statement(pesos_text, "PESOS")

        if dolares_text:
            dolares_statement = self._extract_currency_statement(dolares_text, "DOLARES")

        statement = CreditCardStatement(
            card_info=card_info,
            credit_limit=credit_limit,
            pesos_statement=pesos_statement,
            dolares_statement=dolares_statement,
        )

        total_tx = 0
        if pesos_statement:
            total_tx += len(pesos_statement.transactions)
        if dolares_statement:
            total_tx += len(dolares_statement.transactions)

        logger.info(
            f"Statement processed: {total_tx} transactions, "
            f"pago total pesos: {statement.pago_total_pesos}"
        )

        return statement

    def extract_card_info(self, document: PDFDocument | Path | str) -> CardInfo:
        """Extrae solo la información de la tarjeta."""
        path = self._resolve_path(document)
        text_by_page = self._extractor.extract_text_by_page(path)
        full_text = "\n".join(text_by_page.values())
        return self._extract_card_info(full_text)

    def extract_credit_limit(self, document: PDFDocument | Path | str) -> CreditLimit:
        """Extrae solo la información de cupos."""
        path = self._resolve_path(document)
        text_by_page = self._extractor.extract_text_by_page(path)
        full_text = "\n".join(text_by_page.values())
        return self._extract_credit_limit(full_text)

    def extract_transactions(
        self, document: PDFDocument | Path | str, moneda: str = "PESOS"
    ) -> list[CreditCardTransaction]:
        """
        Extrae las transacciones de una moneda específica.

        Args:
            document: Documento PDF a procesar.
            moneda: "PESOS" o "DOLARES"

        Returns:
            Lista de CreditCardTransaction.
        """
        path = self._resolve_path(document)
        data = self._bancolombia.extract_text_sections(str(path))
        return self._convert_to_credit_card_transactions(data["transactions"])

    def _extract_card_info(self, text: str) -> CardInfo:
        """Extrae información de la tarjeta del texto."""
        logger.debug("Extracting card information")

        # Titular
        titular = ""
        titular_match = re.search(r"SE[ÑN]OR \(A\):\s*([A-Z\s]+?)(?:\n|TARJETA)", text)
        if titular_match:
            titular = titular_match.group(1).strip()

        # Número de tarjeta
        numero_tarjeta = ""
        tarjeta_match = re.search(r"TARJETA:\s*(\*+\d+)", text)
        if tarjeta_match:
            numero_tarjeta = tarjeta_match.group(1)

        # Dirección y ciudad
        direccion = ""
        ciudad = ""
        departamento = ""

        lines = text.split("\n")
        for i, line in enumerate(lines):
            if "SEÑOR (A):" in line or "SENOR (A):" in line:
                if i + 2 < len(lines):
                    direccion = lines[i + 1].strip() if lines[i + 1].strip() else ""
                if i + 3 < len(lines):
                    ciudad = lines[i + 2].strip() if lines[i + 2].strip() else ""
                if i + 4 < len(lines):
                    departamento = lines[i + 3].strip() if lines[i + 3].strip() else ""
                break

        # Periodo facturado
        periodo_desde = None
        periodo_hasta = None
        periodo_match = re.search(
            r"Desde:\s*(\d{2}/\d{2}/\d{4})\s*Hasta:\s*(\d{2}/\d{2}/\d{4})", text
        )
        if periodo_match:
            try:
                desde_parts = periodo_match.group(1).split("/")
                periodo_desde = date(
                    int(desde_parts[2]), int(desde_parts[1]), int(desde_parts[0])
                )
                hasta_parts = periodo_match.group(2).split("/")
                periodo_hasta = date(
                    int(hasta_parts[2]), int(hasta_parts[1]), int(hasta_parts[0])
                )
            except (ValueError, IndexError):
                logger.warning("Could not parse period")

        # Fecha de pago
        fecha_pago = None
        pago_match = re.search(r"Pague antes de\s*(\d{2}/\d{2}/\d{4})", text)
        if pago_match:
            try:
                pago_parts = pago_match.group(1).split("/")
                if pago_parts[0] != "00":
                    fecha_pago = date(
                        int(pago_parts[2]), int(pago_parts[1]), int(pago_parts[0])
                    )
            except (ValueError, IndexError):
                pass

        return CardInfo(
            titular=titular,
            numero_tarjeta=numero_tarjeta,
            direccion=direccion,
            ciudad=ciudad,
            departamento=departamento,
            periodo_desde=periodo_desde,
            periodo_hasta=periodo_hasta,
            fecha_pago=fecha_pago,
        )

    def _extract_credit_limit(self, text: str) -> CreditLimit:
        """Extrae información de cupos del texto."""
        logger.debug("Extracting credit limit")
        parser = self._bancolombia.parser

        def parse_money(pattern: str, txt: str) -> float:
            match = re.search(pattern, txt)
            if match:
                try:
                    return parser.parse_to_float(match.group(1))
                except Exception:
                    return 0.0
            return 0.0

        return CreditLimit(
            cupo_total=parse_money(r"Cupo Total\s*\$?\s*([\d.,]+)", text),
            cupo_avances=parse_money(r"Cupo de Avances\s*\$?\s*([\d.,]+)", text),
            disponible_total=parse_money(r"Disponible Total\s*\$?\s*([\d.,]+)", text),
            disponible_avances=parse_money(r"Disponible Avances\s*\$?\s*([\d.,]+)", text),
        )

    def _extract_currency_statement(self, text: str, moneda: str) -> CurrencyStatement:
        """Extrae el estado de cuenta de una moneda específica."""
        logger.debug(f"Extracting {moneda} statement")

        return CurrencyStatement(
            moneda=moneda,
            balance_summary=self._extract_balance_summary(text),
            minimum_payment=self._extract_minimum_payment(text),
            interest_rates=self._extract_interest_rates(text),
            transactions=self._extract_transactions_from_text(text),
        )

    def _extract_balance_summary(self, text: str) -> BalanceSummary:
        """Extrae el resumen de saldo total."""
        parser = self._bancolombia.parser

        def parse_money(pattern: str, txt: str) -> float:
            match = re.search(pattern, txt)
            if match:
                try:
                    return parser.parse_to_float(match.group(1))
                except Exception:
                    return 0.0
            return 0.0

        return BalanceSummary(
            saldo_anterior=parse_money(r"Saldo anterior\s+([\d.,\-]+)", text),
            compras_mes=parse_money(r"\+ Compras del mes\s+([\d.,\-]+)", text),
            intereses_mora=parse_money(r"\+ Intereses de mora\s+([\d.,\-]+)", text),
            intereses_corrientes=parse_money(r"\+ Intereses corrientes\s+([\d.,\-]+)", text),
            avances=parse_money(r"\+ Avances\s+([\d.,\-]+)", text),
            otros_cargos=parse_money(r"\+ Otros cargos\s+([\d.,\-]+)", text),
            pagos_abonos=parse_money(r"- Pagos / abonos\s+([\d.,\-]+)", text),
            saldo_favor=parse_money(r"Saldo a favor\s+([\d.,\-]+)", text),
            pago_total=parse_money(r"= Pagos total\s+([\d.,\-]+)", text),
        )

    def _extract_minimum_payment(self, text: str) -> MinimumPayment:
        """Extrae el resumen de pago mínimo."""
        parser = self._bancolombia.parser

        def parse_money(pattern: str, txt: str) -> float:
            match = re.search(pattern, txt)
            if match:
                try:
                    return parser.parse_to_float(match.group(1))
                except Exception:
                    return 0.0
            return 0.0

        return MinimumPayment(
            saldo_mora=parse_money(r"Saldo en mora\s+([\d.,\-]+)", text),
            cuota_compras_mes=parse_money(r"\+ Cuota compras del mes\s+([\d.,\-]+)", text),
            intereses_mora=parse_money(r"\+ Intereses de mora\s+([\d.,\-]+)", text),
            intereses_corrientes=parse_money(r"\+ Intereses corrientes\s+([\d.,\-]+)", text),
            cuota_avances=parse_money(r"\+ Cuota avances\s+([\d.,\-]+)", text),
            otros_cargos=parse_money(r"\+ Otros cargos\s+([\d.,\-]+)", text),
            cuota_compras_anteriores=parse_money(r"\+ Cuota compras anteriores\s+([\d.,\-]+)", text),
            saldo_favor=parse_money(r"- Saldo a favor\s+([\d.,\-]+)", text),
            pago_minimo=parse_money(r"= Pago m[ií]nimo\s+([\d.,\-]+)", text),
        )

    def _extract_interest_rates(self, text: str) -> InterestRates:
        """Extrae las tasas de interés."""

        def parse_rate(pattern: str, txt: str) -> tuple[float, float]:
            match = re.search(pattern, txt)
            if match:
                try:
                    mv = float(match.group(1).replace(",", "."))
                    ea = float(match.group(2).replace(",", "."))
                    return mv, ea
                except (ValueError, IndexError):
                    pass
            return 0.0, 0.0

        compra_un_mes = parse_rate(r"Compra un mes\s+([\d,]+)\s*%\s*([\d,]+)\s*%", text)
        compra_2_36 = parse_rate(r"Compra 2 - 36 meses\s+([\d,]+)\s*%\s*([\d,]+)\s*%", text)
        impuestos = parse_rate(r"Impuestos\s+([\d,]+)\s*%\s*([\d,]+)\s*%", text)
        avances = parse_rate(r"Avances\s+([\d,]+)\s*%\s*([\d,]+)\s*%", text)
        mora = parse_rate(r"Mora\s+([\d,]+)\s*%\s*([\d,]+)\s*%", text)
        compra_intl = parse_rate(r"Compra Internacional\s+([\d,]+)\s*%\s*([\d,]+)\s*%", text)
        avance_intl = parse_rate(r"Avance Internacional\s+([\d,]+)\s*%\s*([\d,]+)\s*%", text)

        return InterestRates(
            compra_un_mes_mv=compra_un_mes[0],
            compra_un_mes_ea=compra_un_mes[1],
            compra_2_36_mv=compra_2_36[0] or compra_intl[0],
            compra_2_36_ea=compra_2_36[1] or compra_intl[1],
            impuestos_mv=impuestos[0],
            impuestos_ea=impuestos[1],
            avances_mv=avances[0] or avance_intl[0],
            avances_ea=avances[1] or avance_intl[1],
            mora_mv=mora[0],
            mora_ea=mora[1],
        )

    def _extract_transactions_from_text(self, text: str) -> list[CreditCardTransaction]:
        """Extrae transacciones usando lógica de regex."""
        transactions: list[CreditCardTransaction] = []
        parser = self._bancolombia.parser

        for line in text.split("\n"):
            match = re.match(
                r"^([A-Z]?\d{5,6})\s+"
                r"(\d{2}/\d{2}/\d{4})\s+"
                r"(.+?)\s+"
                r"([\d.,]+)-?\s+"
                r"(?:([\d,]+)\s+([\d,]+)\s+)?"
                r"([\d.,]+)-?\s+"
                r"([\d.,]+)\s*"
                r"(?:(\d+)/(\d+))?",
                line.strip(),
            )

            if match:
                try:
                    num_auth = match.group(1)
                    fecha = match.group(2)
                    descripcion = match.group(3).strip()

                    valor_original = parser.parse_to_float(match.group(4))
                    if match.group(4) + "-" in line:
                        valor_original = -valor_original

                    tasa_pactada = float(match.group(5).replace(",", ".")) if match.group(5) else 0.0
                    tasa_ea = float(match.group(6).replace(",", ".")) if match.group(6) else 0.0

                    cargos_abonos = parser.parse_to_float(match.group(7))
                    if match.group(7) + "-" in line:
                        cargos_abonos = -cargos_abonos

                    saldo_diferir = parser.parse_to_float(match.group(8))
                    cuota_actual = int(match.group(9)) if match.group(9) else 0
                    cuota_total = int(match.group(10)) if match.group(10) else 0

                    transactions.append(
                        CreditCardTransaction(
                            numero_autorizacion=num_auth,
                            fecha=fecha,
                            descripcion=descripcion,
                            valor_original=valor_original,
                            tasa_pactada=tasa_pactada,
                            tasa_ea=tasa_ea,
                            cargos_abonos=cargos_abonos,
                            saldo_diferir=saldo_diferir,
                            cuota_actual=cuota_actual,
                            cuota_total=cuota_total,
                        )
                    )
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error parsing transaction: {e}")
                    continue

        logger.debug(f"Transactions extracted: {len(transactions)}")
        return transactions

    def _convert_to_credit_card_transactions(
        self, banco_transactions: list
    ) -> list[CreditCardTransaction]:
        """Convierte Transaction de Bancolombia a CreditCardTransaction."""
        transactions: list[CreditCardTransaction] = []

        for bt in banco_transactions:
            if isinstance(bt, BancoTransaction):
                fecha = bt.date
                descripcion = bt.description
                cargos_abonos = bt.amount
                numero_auth = bt.authorization if bt.authorization else ""
            else:
                fecha = bt.get("date", "")
                descripcion = bt.get("description", "")
                cargos_abonos = bt.get("amount", 0.0)
                numero_auth = bt.get("authorization", "")

            transactions.append(
                CreditCardTransaction(
                    fecha=fecha,
                    descripcion=descripcion,
                    cargos_abonos=cargos_abonos,
                    numero_autorizacion=numero_auth,
                )
            )

        return transactions
