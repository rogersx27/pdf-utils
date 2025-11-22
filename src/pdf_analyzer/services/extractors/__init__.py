"""
Extractores de datos para diferentes tipos de documentos PDF.

Este submódulo contiene extractores especializados para procesar
diferentes tipos de extractos bancarios.
"""

# Extractores (clases de servicio)
from pdf_analyzer.services.extractors.base import ExtractorService
from pdf_analyzer.services.extractors.bancolombia import BancolombiaExtractor
from pdf_analyzer.services.extractors.savings_account import SavingsAccountExtractor
from pdf_analyzer.services.extractors.credit_card import CreditCardExtractor

# Modelos (re-exportados desde models/ para compatibilidad)
from pdf_analyzer.models import (
    # Extractor models
    TableInfo,
    Section,
    # Base transaction models
    Transaction,
    Transaction as BancolombiaTransaction,
    AccountSummary,
    # Savings account models
    AccountInfo,
    FinancialSummary,
    SavingsTransaction,
    SavingsAccountStatement,
    # Credit card models
    CardInfo,
    CreditLimit,
    InterestRates,
    BalanceSummary,
    MinimumPayment,
    CreditCardTransaction,
    CurrencyStatement,
    CreditCardStatement,
)

__all__ = [
    # Extractors (services)
    "ExtractorService",
    "BancolombiaExtractor",
    "SavingsAccountExtractor",
    "CreditCardExtractor",
    # Base models
    "TableInfo",
    "Section",
    "Transaction",
    "BancolombiaTransaction",
    "AccountSummary",
    # Savings Account models
    "AccountInfo",
    "FinancialSummary",
    "SavingsTransaction",
    "SavingsAccountStatement",
    # Credit Card models
    "CardInfo",
    "CreditLimit",
    "InterestRates",
    "BalanceSummary",
    "MinimumPayment",
    "CreditCardTransaction",
    "CurrencyStatement",
    "CreditCardStatement",
]
