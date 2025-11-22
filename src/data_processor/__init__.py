"""
Data Processor - Módulo para procesamiento de datos de extractos bancarios con pandas.

Este módulo proporciona procesadores especializados que:
- Convierten datos extraídos a pandas DataFrames
- Validan integridad y consistencia de datos
- Facilitan análisis y transformaciones
- Exportan a múltiples formatos (CSV, Excel, JSON)
"""

from .savings_processor import SavingsAccountProcessor
from .credit_card_processor import CreditCardProcessor
from .validators import validate_data, ValidationResult

__version__ = "1.0.0"

__all__ = [
    "SavingsAccountProcessor",
    "CreditCardProcessor",
    "validate_data",
    "ValidationResult",
]
