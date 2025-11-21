"""
Extractor específico para extractos de Tarjeta de Crédito MasterCard.

Parsea la información estructurada de los extractos bancarios
de tarjetas de crédito de Bancolombia.
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
class CardInfo:
    """Información de la tarjeta de crédito."""

    titular: str
    numero_tarjeta: str  # Enmascarado: ************8989
    direccion: str
    ciudad: str
    departamento: str
    periodo_desde: Optional[date] = None
    periodo_hasta: Optional[date] = None
    fecha_pago: Optional[date] = None

    def to_dict(self) -> dict:
        return {
            "titular": self.titular,
            "numero_tarjeta": self.numero_tarjeta,
            "direccion": self.direccion,
            "ciudad": self.ciudad,
            "departamento": self.departamento,
            "periodo_desde": self.periodo_desde.isoformat() if self.periodo_desde else None,
            "periodo_hasta": self.periodo_hasta.isoformat() if self.periodo_hasta else None,
            "fecha_pago": self.fecha_pago.isoformat() if self.fecha_pago else None,
        }


@dataclass
class CreditLimit:
    """Información de cupos de la tarjeta."""

    cupo_total: float = 0.0
    cupo_avances: float = 0.0
    disponible_total: float = 0.0
    disponible_avances: float = 0.0

    def to_dict(self) -> dict:
        return {
            "cupo_total": self.cupo_total,
            "cupo_avances": self.cupo_avances,
            "disponible_total": self.disponible_total,
            "disponible_avances": self.disponible_avances,
        }


@dataclass
class InterestRates:
    """Tasas de interés vigentes."""

    compra_un_mes_mv: float = 0.0
    compra_un_mes_ea: float = 0.0
    compra_2_36_mv: float = 0.0
    compra_2_36_ea: float = 0.0
    impuestos_mv: float = 0.0
    impuestos_ea: float = 0.0
    avances_mv: float = 0.0
    avances_ea: float = 0.0
    mora_mv: float = 0.0
    mora_ea: float = 0.0

    def to_dict(self) -> dict:
        return {
            "compra_un_mes": {"mv": self.compra_un_mes_mv, "ea": self.compra_un_mes_ea},
            "compra_2_36_meses": {"mv": self.compra_2_36_mv, "ea": self.compra_2_36_ea},
            "impuestos": {"mv": self.impuestos_mv, "ea": self.impuestos_ea},
            "avances": {"mv": self.avances_mv, "ea": self.avances_ea},
            "mora": {"mv": self.mora_mv, "ea": self.mora_ea},
        }


@dataclass
class BalanceSummary:
    """Resumen de saldo total."""

    saldo_anterior: float = 0.0
    compras_mes: float = 0.0
    intereses_mora: float = 0.0
    intereses_corrientes: float = 0.0
    avances: float = 0.0
    otros_cargos: float = 0.0
    pagos_abonos: float = 0.0
    saldo_favor: float = 0.0
    pago_total: float = 0.0

    def to_dict(self) -> dict:
        return {
            "saldo_anterior": self.saldo_anterior,
            "compras_mes": self.compras_mes,
            "intereses_mora": self.intereses_mora,
            "intereses_corrientes": self.intereses_corrientes,
            "avances": self.avances,
            "otros_cargos": self.otros_cargos,
            "pagos_abonos": self.pagos_abonos,
            "saldo_favor": self.saldo_favor,
            "pago_total": self.pago_total,
        }


@dataclass
class MinimumPayment:
    """Resumen de pago mínimo."""

    saldo_mora: float = 0.0
    cuota_compras_mes: float = 0.0
    intereses_mora: float = 0.0
    intereses_corrientes: float = 0.0
    cuota_avances: float = 0.0
    otros_cargos: float = 0.0
    cuota_compras_anteriores: float = 0.0
    saldo_favor: float = 0.0
    pago_minimo: float = 0.0

    def to_dict(self) -> dict:
        return {
            "saldo_mora": self.saldo_mora,
            "cuota_compras_mes": self.cuota_compras_mes,
            "intereses_mora": self.intereses_mora,
            "intereses_corrientes": self.intereses_corrientes,
            "cuota_avances": self.cuota_avances,
            "otros_cargos": self.otros_cargos,
            "cuota_compras_anteriores": self.cuota_compras_anteriores,
            "saldo_favor": self.saldo_favor,
            "pago_minimo": self.pago_minimo,
        }


@dataclass
class CreditCardTransaction:
    """Transacción de tarjeta de crédito."""

    fecha: str
    descripcion: str
    valor_original: float = 0.0
    tasa_pactada: float = 0.0
    tasa_ea: float = 0.0
    cargos_abonos: float = 0.0
    saldo_diferir: float = 0.0
    cuota_actual: int = 0
    cuota_total: int = 0
    numero_autorizacion: str = ""

    @property
    def es_abono(self) -> bool:
        """Retorna True si es un abono/pago."""
        return self.cargos_abonos < 0

    @property
    def es_diferido(self) -> bool:
        """Retorna True si es una compra diferida."""
        return self.cuota_total > 1

    def to_dict(self) -> dict:
        return {
            "numero_autorizacion": self.numero_autorizacion,
            "fecha": self.fecha,
            "descripcion": self.descripcion,
            "valor_original": self.valor_original,
            "tasa_pactada": self.tasa_pactada,
            "tasa_ea": self.tasa_ea,
            "cargos_abonos": self.cargos_abonos,
            "saldo_diferir": self.saldo_diferir,
            "cuotas": f"{self.cuota_actual}/{self.cuota_total}" if self.cuota_total > 0 else "",
            "tipo": "abono" if self.es_abono else "cargo",
            "diferido": self.es_diferido,
        }


@dataclass
class CurrencyStatement:
    """Estado de cuenta por moneda (Pesos o Dólares)."""

    moneda: str  # "PESOS" o "DOLARES"
    balance_summary: BalanceSummary
    minimum_payment: MinimumPayment
    interest_rates: InterestRates
    transactions: list[CreditCardTransaction] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "moneda": self.moneda,
            "balance_summary": self.balance_summary.to_dict(),
            "minimum_payment": self.minimum_payment.to_dict(),
            "interest_rates": self.interest_rates.to_dict(),
            "transactions": [t.to_dict() for t in self.transactions],
            "total_transactions": len(self.transactions),
        }


@dataclass
class CreditCardStatement:
    """Extracto completo de tarjeta de crédito."""

    card_info: CardInfo
    credit_limit: CreditLimit
    pesos_statement: Optional[CurrencyStatement] = None
    dolares_statement: Optional[CurrencyStatement] = None

    @property
    def pago_total_pesos(self) -> float:
        return self.pesos_statement.balance_summary.pago_total if self.pesos_statement else 0.0

    @property
    def pago_minimo_pesos(self) -> float:
        return self.pesos_statement.minimum_payment.pago_minimo if self.pesos_statement else 0.0

    @property
    def pago_total_dolares(self) -> float:
        return self.dolares_statement.balance_summary.pago_total if self.dolares_statement else 0.0

    @property
    def pago_minimo_dolares(self) -> float:
        return self.dolares_statement.minimum_payment.pago_minimo if self.dolares_statement else 0.0

    def to_dict(self) -> dict:
        return {
            "card_info": self.card_info.to_dict(),
            "credit_limit": self.credit_limit.to_dict(),
            "pesos": self.pesos_statement.to_dict() if self.pesos_statement else None,
            "dolares": self.dolares_statement.to_dict() if self.dolares_statement else None,
        }


class CreditCardExtractor:
    """
    Extractor especializado para extractos de Tarjeta de Crédito MasterCard.

    Parsea extractos de Bancolombia con formato TARJETA_MASTERCARD
    extrayendo información de tarjeta, cupos, tasas y transacciones
    en pesos y dólares.
    """

    def __init__(self, password: Optional[str] = None):
        """
        Inicializa el extractor.

        Args:
            password: Contraseña para PDFs protegidos.
        """
        self._password = password or get_default_password()
        self._extractor = ExtractorService(password)
        logger.debug("CreditCardExtractor inicializado")

    def extract(
        self, document: PDFDocument | Path | str
    ) -> CreditCardStatement:
        """
        Extrae toda la información del extracto de tarjeta de crédito.

        Args:
            document: Documento PDF a procesar.

        Returns:
            CreditCardStatement con toda la información extraída.
        """
        path = self._resolve_path(document)
        logger.info(f"Extrayendo extracto de tarjeta de crédito: {path.name}")

        # Obtener texto por página
        text_by_page = self._extractor.extract_text_by_page(path)

        # Identificar páginas por moneda
        pesos_text = ""
        dolares_text = ""

        for page_num, content in text_by_page.items():
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
            f"Extracto procesado: {total_tx} transacciones, "
            f"pago total pesos: {statement.pago_total_pesos}"
        )

        return statement

    def extract_card_info(
        self, document: PDFDocument | Path | str
    ) -> CardInfo:
        """Extrae solo la información de la tarjeta."""
        path = self._resolve_path(document)
        text_by_page = self._extractor.extract_text_by_page(path)
        full_text = "\n".join(text_by_page.values())
        return self._extract_card_info(full_text)

    def extract_credit_limit(
        self, document: PDFDocument | Path | str
    ) -> CreditLimit:
        """Extrae solo la información de cupos."""
        path = self._resolve_path(document)
        text_by_page = self._extractor.extract_text_by_page(path)
        full_text = "\n".join(text_by_page.values())
        return self._extract_credit_limit(full_text)

    def extract_transactions(
        self, document: PDFDocument | Path | str,
        moneda: str = "PESOS"
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
        text_by_page = self._extractor.extract_text_by_page(path)

        target_text = ""
        for content in text_by_page.values():
            if f"ESTADO DE CUENTA EN: {moneda}" in content:
                target_text = content
                break

        if not target_text:
            return []

        return self._extract_transactions(target_text)

    def _extract_card_info(self, text: str) -> CardInfo:
        """Extrae información de la tarjeta del texto."""
        logger.debug("Extrayendo información de tarjeta")

        # Titular: SEÑOR (A): NOMBRE
        titular = ""
        titular_match = re.search(r"SE[ÑN]OR \(A\):\s*([A-Z\s]+?)(?:\n|TARJETA)", text)
        if titular_match:
            titular = titular_match.group(1).strip()

        # Número de tarjeta: TARJETA: ************8989
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
                # Las siguientes líneas suelen tener dirección
                if i + 2 < len(lines):
                    direccion = lines[i + 1].strip() if lines[i + 1].strip() else ""
                if i + 3 < len(lines):
                    ciudad = lines[i + 2].strip() if lines[i + 2].strip() else ""
                if i + 4 < len(lines):
                    departamento = lines[i + 3].strip() if lines[i + 3].strip() else ""
                break

        # Periodo facturado: Desde: DD/MM/YYYY Hasta: DD/MM/YYYY
        periodo_desde = None
        periodo_hasta = None
        periodo_match = re.search(
            r"Desde:\s*(\d{2}/\d{2}/\d{4})\s*Hasta:\s*(\d{2}/\d{2}/\d{4})",
            text
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
                logger.warning("No se pudo parsear el periodo")

        # Fecha de pago: Pague antes de DD/MM/YYYY
        fecha_pago = None
        pago_match = re.search(r"Pague antes de\s*(\d{2}/\d{2}/\d{4})", text)
        if pago_match:
            try:
                pago_parts = pago_match.group(1).split("/")
                if pago_parts[0] != "00":  # Ignorar fechas inválidas
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
        logger.debug("Extrayendo información de cupos")

        def parse_money(pattern: str, txt: str) -> float:
            match = re.search(pattern, txt)
            if match:
                value_str = match.group(1).replace(".", "").replace(",", ".")
                try:
                    return float(value_str)
                except ValueError:
                    return 0.0
            return 0.0

        cupo_total = parse_money(r"Cupo Total\s*\$\s*([\d.,]+)", text)
        cupo_avances = parse_money(r"Cupo de Avances\s*\$\s*([\d.,]+)", text)
        disponible_total = parse_money(r"Disponible Total\s*\$\s*([\d.,]+)", text)
        disponible_avances = parse_money(r"Disponible Avances\s*\$\s*([\d.,]+)", text)

        return CreditLimit(
            cupo_total=cupo_total,
            cupo_avances=cupo_avances,
            disponible_total=disponible_total,
            disponible_avances=disponible_avances,
        )

    def _extract_currency_statement(
        self, text: str, moneda: str
    ) -> CurrencyStatement:
        """Extrae el estado de cuenta de una moneda específica."""
        logger.debug(f"Extrayendo estado de cuenta en {moneda}")

        balance = self._extract_balance_summary(text)
        minimum = self._extract_minimum_payment(text)
        rates = self._extract_interest_rates(text)
        transactions = self._extract_transactions(text)

        return CurrencyStatement(
            moneda=moneda,
            balance_summary=balance,
            minimum_payment=minimum,
            interest_rates=rates,
            transactions=transactions,
        )

    def _extract_balance_summary(self, text: str) -> BalanceSummary:
        """Extrae el resumen de saldo total."""
        logger.debug("Extrayendo resumen de saldo")

        def parse_money(pattern: str, txt: str) -> float:
            match = re.search(pattern, txt)
            if match:
                value_str = match.group(1).replace(".", "").replace(",", ".")
                try:
                    return float(value_str)
                except ValueError:
                    return 0.0
            return 0.0

        # Buscar en sección "Resumen Saldo Total"
        saldo_anterior = parse_money(r"Saldo anterior\s+([\d.,]+)", text)
        compras_mes = parse_money(r"\+ Compras del mes\s+([\d.,]+)", text)
        intereses_mora = parse_money(r"\+ Intereses de mora\s+([\d.,]+)", text)
        intereses_corrientes = parse_money(r"\+ Intereses corrientes\s+([\d.,]+)", text)
        avances = parse_money(r"\+ Avances\s+([\d.,]+)", text)
        otros_cargos = parse_money(r"\+ Otros cargos\s+([\d.,]+)", text)
        pagos_abonos = parse_money(r"- Pagos / abonos\s+([\d.,]+)", text)
        saldo_favor = parse_money(r"Saldo a favor\s+([\d.,]+)", text)
        pago_total = parse_money(r"= Pagos total\s+([\d.,]+)", text)

        return BalanceSummary(
            saldo_anterior=saldo_anterior,
            compras_mes=compras_mes,
            intereses_mora=intereses_mora,
            intereses_corrientes=intereses_corrientes,
            avances=avances,
            otros_cargos=otros_cargos,
            pagos_abonos=pagos_abonos,
            saldo_favor=saldo_favor,
            pago_total=pago_total,
        )

    def _extract_minimum_payment(self, text: str) -> MinimumPayment:
        """Extrae el resumen de pago mínimo."""
        logger.debug("Extrayendo pago mínimo")

        def parse_money(pattern: str, txt: str) -> float:
            match = re.search(pattern, txt)
            if match:
                value_str = match.group(1).replace(".", "").replace(",", ".")
                try:
                    return float(value_str)
                except ValueError:
                    return 0.0
            return 0.0

        # Buscar en sección "Resumen Pago Mínimo"
        saldo_mora = parse_money(r"Saldo en mora\s+([\d.,]+)", text)
        cuota_compras_mes = parse_money(r"\+ Cuota compras del mes\s+([\d.,]+)", text)
        intereses_mora = parse_money(r"\+ Intereses de mora\s+([\d.,]+)", text)
        intereses_corrientes = parse_money(r"\+ Intereses corrientes\s+([\d.,]+)", text)
        cuota_avances = parse_money(r"\+ Cuota avances\s+([\d.,]+)", text)
        otros_cargos = parse_money(r"\+ Otros cargos\s+([\d.,]+)", text)
        cuota_anteriores = parse_money(r"\+ Cuota compras anteriores\s+([\d.,]+)", text)
        saldo_favor = parse_money(r"- Saldo a favor\s+([\d.,]+)", text)
        pago_minimo = parse_money(r"= Pago m[ií]nimo\s+([\d.,]+)", text)

        return MinimumPayment(
            saldo_mora=saldo_mora,
            cuota_compras_mes=cuota_compras_mes,
            intereses_mora=intereses_mora,
            intereses_corrientes=intereses_corrientes,
            cuota_avances=cuota_avances,
            otros_cargos=otros_cargos,
            cuota_compras_anteriores=cuota_anteriores,
            saldo_favor=saldo_favor,
            pago_minimo=pago_minimo,
        )

    def _extract_interest_rates(self, text: str) -> InterestRates:
        """Extrae las tasas de interés."""
        logger.debug("Extrayendo tasas de interés")

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

        # Para dólares
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

    def _extract_transactions(self, text: str) -> list[CreditCardTransaction]:
        """Extrae las transacciones del texto."""
        logger.debug("Extrayendo transacciones")

        transactions: list[CreditCardTransaction] = []

        # Patrón para transacciones de tarjeta de crédito
        # Formato: NumAuth Fecha Descripción ValorOrig TasaPact TasaEA CargosAbonos SaldoDif Cuotas
        # Ejemplo: R02990 14/05/2025 UBER RIDES 8,791.00 0,0000 00,0000 8,791.00 0.00 1/1
        # Abono:   C04028 06/05/2025 ABONO SUCURSAL VIRTUAL 100,000.00- 100,000.00- 0.00

        lines = text.split("\n")

        for line in lines:
            # Buscar líneas que empiecen con código de autorización o fecha
            # Código: letra + números (R02990, C04028, T05825, etc.) o solo números (000000)
            match = re.match(
                r"^([A-Z]?\d{5,6})\s+"  # Número autorización
                r"(\d{2}/\d{2}/\d{4})\s+"  # Fecha
                r"(.+?)\s+"  # Descripción
                r"([\d.,]+)-?\s+"  # Valor original (puede tener - al final)
                r"(?:([\d,]+)\s+([\d,]+)\s+)?"  # Tasa pactada y EA (opcional)
                r"([\d.,]+)-?\s+"  # Cargos/Abonos
                r"([\d.,]+)\s*"  # Saldo a diferir
                r"(?:(\d+)/(\d+))?",  # Cuotas (opcional)
                line.strip()
            )

            if match:
                try:
                    num_auth = match.group(1)
                    fecha = match.group(2)
                    descripcion = match.group(3).strip()

                    valor_str = match.group(4).replace(".", "").replace(",", ".")
                    valor_original = float(valor_str)
                    if line.count(match.group(4) + "-") > 0:
                        valor_original = -valor_original

                    tasa_pactada = float(match.group(5).replace(",", ".")) if match.group(5) else 0.0
                    tasa_ea = float(match.group(6).replace(",", ".")) if match.group(6) else 0.0

                    cargos_str = match.group(7).replace(".", "").replace(",", ".")
                    cargos_abonos = float(cargos_str)
                    # Verificar si es negativo (abono)
                    if match.group(7) + "-" in line:
                        cargos_abonos = -cargos_abonos

                    saldo_str = match.group(8).replace(".", "").replace(",", ".")
                    saldo_diferir = float(saldo_str)

                    cuota_actual = int(match.group(9)) if match.group(9) else 0
                    cuota_total = int(match.group(10)) if match.group(10) else 0

                    transaction = CreditCardTransaction(
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
                    transactions.append(transaction)

                except (ValueError, IndexError) as e:
                    logger.warning(f"Error parseando transacción: {e}")
                    continue

            # También buscar líneas sin número de autorización (intereses, etc.)
            elif re.match(r"^\d{2}/\d{2}/\d{4}\s+", line.strip()):
                match2 = re.match(
                    r"^(\d{2}/\d{2}/\d{4})\s+"  # Fecha
                    r"(.+?)\s+"  # Descripción
                    r"([\d.,]+)\s+"  # Cargos/Abonos
                    r"([\d.,]+)",  # Saldo
                    line.strip()
                )
                if match2:
                    try:
                        fecha = match2.group(1)
                        descripcion = match2.group(2).strip()
                        cargos_str = match2.group(3).replace(".", "").replace(",", ".")
                        cargos_abonos = float(cargos_str)
                        saldo_str = match2.group(4).replace(".", "").replace(",", ".")
                        saldo_diferir = float(saldo_str)

                        transaction = CreditCardTransaction(
                            numero_autorizacion="",
                            fecha=fecha,
                            descripcion=descripcion,
                            cargos_abonos=cargos_abonos,
                            saldo_diferir=saldo_diferir,
                        )
                        transactions.append(transaction)
                    except (ValueError, IndexError):
                        continue

        logger.debug(f"Transacciones extraídas: {len(transactions)}")
        return transactions

    @staticmethod
    def _resolve_path(document: PDFDocument | Path | str) -> Path:
        """Resuelve la ruta de un documento."""
        if isinstance(document, PDFDocument):
            return document.path
        return Path(document)
