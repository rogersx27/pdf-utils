"""
Protocolo para objetos serializables.

Define la interfaz que deben implementar los objetos
que pueden convertirse a diccionario.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class Serializable(Protocol):
    """
    Protocolo para objetos que pueden serializarse a diccionario.

    Las clases que implementen este protocolo deben proveer
    un método to_dict() que retorne una representación en dict.

    Uso:
        @dataclass
        class MyModel:
            name: str
            value: int

            def to_dict(self) -> dict:
                return {"name": self.name, "value": self.value}

        # Verificar si implementa el protocolo
        obj = MyModel("test", 42)
        assert isinstance(obj, Serializable)
    """

    def to_dict(self) -> dict:
        """
        Convierte el objeto a un diccionario.

        Returns:
            Representación del objeto como diccionario.
        """
        ...
