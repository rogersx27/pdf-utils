"""
Modelos para extractos de cuentas de ahorro.

Define las estructuras de datos para representar la información
extraída de extractos de cuentas de ahorro.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


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
class SavingsTransaction:
    """Transacción individual del extracto de cuenta de ahorros."""

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
    transactions: list[SavingsTransaction] = field(default_factory=list)

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
