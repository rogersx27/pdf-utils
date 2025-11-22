"""
Concerns (Mixins) para pdf_analyzer.

Módulos que encapsulan comportamiento reutilizable entre diferentes clases.
"""

from pdf_analyzer.concerns.path_resolvable import PathResolvableMixin
from pdf_analyzer.concerns.password_aware import PasswordAwareMixin, get_default_password
from pdf_analyzer.concerns.cacheable import CacheableMixin
from pdf_analyzer.concerns.serializable import Serializable

__all__ = [
    "PathResolvableMixin",
    "PasswordAwareMixin",
    "get_default_password",
    "CacheableMixin",
    "Serializable",
]
