"""
Modelos para extractos de tarjetas de crédito.

Define las estructuras de datos para representar la información
extraída de extractos de tarjetas de crédito.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


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
