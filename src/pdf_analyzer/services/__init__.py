"""
Servicios de lógica de negocio para pdf_analyzer.

Contiene los servicios que implementan las operaciones
de lectura, análisis y seguridad de PDFs.

Estructura:
    - reader_service: Lectura de texto y tablas
    - analyzer_service: Análisis y búsqueda
    - security_service: Gestión de contraseñas
    - extractors/: Extractores especializados por tipo de documento
    - parsers/: Utilidades de parseo (números, monedas)
"""

from pdf_analyzer.services.reader_service import ReaderService
from pdf_analyzer.services.analyzer_service import AnalyzerService
from pdf_analyzer.services.security_service import SecurityService

# Extractores (desde nueva ubicación)
from pdf_analyzer.services.extractors import (
    # Extractors
    ExtractorService,
    BancolombiaExtractor,
    SavingsAccountExtractor,
    CreditCardExtractor,
    # Base models
    TableInfo,
    Section,
    Transaction,
    BancolombiaTransaction,
    AccountSummary,
    # Savings Account models
    AccountInfo,
    FinancialSummary,
    SavingsTransaction,
    SavingsAccountStatement,
    # Credit Card models
    CardInfo,
    CreditLimit,
    InterestRates,
    BalanceSummary,
    MinimumPayment,
    CreditCardTransaction,
    CurrencyStatement,
    CreditCardStatement,
)

# Parsers
from pdf_analyzer.services.parsers import NumberParser, parse_currency

__all__ = [
    # Core Services
    "ReaderService",
    "AnalyzerService",
    "SecurityService",
    # Extractors
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
    # Parsers
    "NumberParser",
    "parse_currency",
]
