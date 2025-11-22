"""
Validadores para verificar integridad y consistencia de datos extraídos.
"""

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class ValidationResult:
    """Resultado de una validación."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: dict[str, Any] = field(default_factory=dict)

    def add_error(self, message: str):
        """Agrega un error."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str):
        """Agrega una advertencia."""
        self.warnings.append(message)

    def __str__(self) -> str:
        lines = [f"Validación: {'✓ VÁLIDA' if self.is_valid else '✗ INVÁLIDA'}"]
        if self.errors:
            lines.append(f"\nErrores ({len(self.errors)}):")
            for error in self.errors:
                lines.append(f"  - {error}")
        if self.warnings:
            lines.append(f"\nAdvertencias ({len(self.warnings)}):")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
        return "\n".join(lines)


def validate_balance_consistency(
    transactions_df: pd.DataFrame, saldo_inicial: float
) -> ValidationResult:
    """
    Valida que los saldos sean consistentes en las transacciones.

    Args:
        transactions_df: DataFrame con columnas 'valor' y 'saldo'
        saldo_inicial: Saldo inicial del período

    Returns:
        ValidationResult con el resultado de la validación
    """
    result = ValidationResult(is_valid=True)

    if transactions_df.empty:
        result.add_warning("No hay transacciones para validar")
        return result

    if "valor" not in transactions_df.columns or "saldo" not in transactions_df.columns:
        result.add_error("DataFrame debe tener columnas 'valor' y 'saldo'")
        return result

    # Validar cada transacción
    saldo_esperado = saldo_inicial
    inconsistencias = 0

    for idx, row in transactions_df.iterrows():
        saldo_esperado += row["valor"]
        saldo_real = row["saldo"]

        # Tolerancia de ±0.01 para errores de redondeo
        if abs(saldo_esperado - saldo_real) > 0.01:
            inconsistencias += 1
            if inconsistencias <= 5:  # Solo reportar primeras 5
                result.add_error(
                    f"Fila {idx}: Saldo inconsistente. "
                    f"Esperado: ${saldo_esperado:,.2f}, "
                    f"Real: ${saldo_real:,.2f}"
                )

    if inconsistencias > 5:
        result.add_error(
            f"... y {inconsistencias - 5} inconsistencias más"
        )

    result.info["inconsistencias"] = inconsistencias
    return result


def validate_totals(
    transactions_df: pd.DataFrame,
    total_creditos_declarado: float,
    total_debitos_declarado: float,
) -> ValidationResult:
    """
    Valida que los totales calculados coincidan con los declarados.

    Args:
        transactions_df: DataFrame con columna 'valor'
        total_creditos_declarado: Total de créditos según el extracto
        total_debitos_declarado: Total de débitos según el extracto (valor absoluto esperado)

    Returns:
        ValidationResult con el resultado de la validación
    """
    result = ValidationResult(is_valid=True)

    if "valor" not in transactions_df.columns:
        result.add_error("DataFrame debe tener columna 'valor'")
        return result

    # Calcular totales
    creditos = transactions_df[transactions_df["valor"] > 0]["valor"].sum()
    # Los débitos en transacciones son negativos, necesitamos valor absoluto
    debitos_abs = abs(transactions_df[transactions_df["valor"] < 0]["valor"].sum())

    # Validar con tolerancia
    tolerancia = 0.01

    if abs(creditos - total_creditos_declarado) > tolerancia:
        result.add_error(
            f"Total créditos inconsistente. "
            f"Calculado: ${creditos:,.2f}, "
            f"Declarado: ${total_creditos_declarado:,.2f}"
        )

    # Comparar valores absolutos
    if abs(debitos_abs - total_debitos_declarado) > tolerancia:
        result.add_error(
            f"Total débitos inconsistente. "
            f"Calculado: ${debitos_abs:,.2f}, "
            f"Declarado: ${total_debitos_declarado:,.2f}"
        )

    result.info["creditos_calculado"] = creditos
    result.info["debitos_calculado"] = debitos_abs

    return result


def validate_data(
    transactions_df: pd.DataFrame,
    saldo_anterior: float,
    saldo_actual: float,
    total_creditos: float,
    total_debitos: float,
) -> ValidationResult:
    """
    Validación completa de datos de cuenta de ahorros.

    Args:
        transactions_df: DataFrame de transacciones
        saldo_anterior: Saldo inicial del período
        saldo_actual: Saldo final del período
        total_creditos: Total de créditos declarado
        total_debitos: Total de débitos declarado

    Returns:
        ValidationResult consolidado
    """
    result = ValidationResult(is_valid=True)

    # Validar consistencia de saldos
    balance_result = validate_balance_consistency(transactions_df, saldo_anterior)
    result.errors.extend(balance_result.errors)
    result.warnings.extend(balance_result.warnings)
    result.is_valid = result.is_valid and balance_result.is_valid

    # Validar totales
    totals_result = validate_totals(transactions_df, total_creditos, abs(total_debitos))
    result.errors.extend(totals_result.errors)
    result.warnings.extend(totals_result.warnings)
    result.is_valid = result.is_valid and totals_result.is_valid

    # Validar saldo final
    if not transactions_df.empty:
        ultimo_saldo = transactions_df.iloc[-1]["saldo"]
        if abs(ultimo_saldo - saldo_actual) > 0.01:
            result.add_error(
                f"Saldo final inconsistente. "
                f"Último en transacciones: ${ultimo_saldo:,.2f}, "
                f"Declarado: ${saldo_actual:,.2f}"
            )

    return result
