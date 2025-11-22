"""
Mixin para caché interno en clases.

Proporciona funcionalidad de caché en memoria para evitar
operaciones costosas repetidas.
"""

from typing import Any, Optional


class CacheableMixin:
    """
    Mixin para clases que necesitan caché interno.

    Proporciona métodos para inicializar, acceder y limpiar
    un diccionario de caché.

    Uso:
        class MyService(CacheableMixin):
            def __init__(self):
                self._init_cache()

            def expensive_operation(self, key: str):
                cached = self._get_cached(key)
                if cached is not None:
                    return cached

                result = self._do_expensive_work()
                self._set_cached(key, result)
                return result
    """

    _cache: dict[str, Any]

    def _init_cache(self) -> None:
        """Inicializa el diccionario de caché."""
        self._cache = {}

    def _get_cached(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del caché.

        Args:
            key: Clave del valor a obtener.

        Returns:
            Valor cacheado o None si no existe.
        """
        return self._cache.get(key)

    def _set_cached(self, key: str, value: Any) -> None:
        """
        Almacena un valor en el caché.

        Args:
            key: Clave para identificar el valor.
            value: Valor a almacenar.
        """
        self._cache[key] = value

    def _has_cached(self, key: str) -> bool:
        """
        Verifica si existe un valor en el caché.

        Args:
            key: Clave a verificar.

        Returns:
            True si existe el valor.
        """
        return key in self._cache

    def _remove_cached(self, key: str) -> bool:
        """
        Elimina un valor del caché.

        Args:
            key: Clave del valor a eliminar.

        Returns:
            True si se eliminó, False si no existía.
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear_cache(self) -> None:
        """Limpia todo el caché."""
        self._cache.clear()

    @property
    def cache_size(self) -> int:
        """Retorna el número de elementos en el caché."""
        return len(self._cache)
