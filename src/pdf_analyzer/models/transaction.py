"""
Modelos base de transacciones bancarias.

Define las estructuras de datos para transacciones y resúmenes
utilizados por los extractores de Bancolombia.
"""

from dataclasses import dataclass, asdict
from typing import Any, Optional


@dataclass
class Transaction:
    """Representa una transacción bancaria individual."""

    date: str
    description: str
    amount: float
    balance: Optional[float] = None
    authorization: Optional[str] = None
    installments: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AccountSummary:
    """Resumen de cuenta bancaria."""

    account_number: str
    account_holder: str
    period_start: str
    period_end: str
    previous_balance: float
    current_balance: float
    total_credits: float
    total_debits: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
