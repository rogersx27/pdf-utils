"""
Modelos de dominio para pdf_analyzer.

Contiene las estructuras de datos para:
- PDFDocument: Representación de documentos PDF
- Transaction: Transacciones bancarias base
- SavingsAccount: Extractos de cuenta de ahorro
- CreditCard: Extractos de tarjeta de crédito
- Extractor: Modelos para extracción de datos
"""

from .pdf_document import PDFDocument, PDFDocumentInfo

# Modelos base de transacciones
from .transaction import Transaction, AccountSummary

# Modelos de extracción
from .extractor import TableInfo, Section

# Modelos de cuenta de ahorros
from .savings_account import (
    AccountInfo,
    FinancialSummary,
    SavingsTransaction,
    SavingsAccountStatement,
)

# Modelos de tarjeta de crédito
from .credit_card import (
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
    # PDF Document
    "PDFDocument",
    "PDFDocumentInfo",
    # Base Transaction
    "Transaction",
    "AccountSummary",
    # Extractor
    "TableInfo",
    "Section",
    # Savings Account
    "AccountInfo",
    "FinancialSummary",
    "SavingsTransaction",
    "SavingsAccountStatement",
    # Credit Card
    "CardInfo",
    "CreditLimit",
    "InterestRates",
    "BalanceSummary",
    "MinimumPayment",
    "CreditCardTransaction",
    "CurrencyStatement",
    "CreditCardStatement",
]
