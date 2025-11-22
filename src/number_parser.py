import re
from typing import Union, Optional
from decimal import Decimal


class NumberParser:
    """
    Parser for monetary values in Colombian bank statements
    """
    
    def __init__(self):
        # Patrones regex para identificar formato numérico
        self.patterns = {
            'us_format': re.compile(r'^\$?\s*-?\d{1,3}(,\d{3})*(\.\d{2})?$'),
            'co_format': re.compile(r'^\$?\s*-?\d{1,3}(\.\d{3})*(,\d{2})?$')
        }
    
    def clean_currency_string(self, value: str) -> str:
        """
        Limpia el string de símbolos de moneda y espacios
        """
        if not isinstance(value, str):
            return str(value)
        
        # Elimina símbolos de moneda y espacios
        cleaned = value.strip()
        cleaned = cleaned.replace('$', '').strip()
        
        return cleaned
    
    def detect_format(self, value: str) -> Optional[str]:
        """
        Detecta si el valor está en formato US o colombiano
        """
        cleaned = self.clean_currency_string(value)
        
        if self.patterns['us_format'].match(cleaned):
            return 'us'
        elif self.patterns['co_format'].match(cleaned):
            return 'co'
        
        return None
    
    def parse_us_format(self, value: str) -> Decimal:
        """
        Convierte formato US: 1,234,567.89 a número
        """
        cleaned = self.clean_currency_string(value)
        
        # Remueve las comas de separación de miles
        normalized = cleaned.replace(',', '')
        
        return Decimal(normalized)
    
    def parse_co_format(self, value: str) -> Decimal:
        """
        Convierte formato colombiano: 1.234.567,89 a número
        """
        cleaned = self.clean_currency_string(value)
        
        # Remueve puntos de miles y cambia coma decimal por punto
        normalized = cleaned.replace('.', '')
        normalized = normalized.replace(',', '.')
        
        return Decimal(normalized)
    
    def parse(self, value: Union[str, int, float, Decimal]) -> Decimal:
        """
        Método principal que detecta y convierte automáticamente
        """
        # Si ya es un número, retorna como Decimal
        if isinstance(value, (int, float, Decimal)):
            return Decimal(str(value))
        
        if not isinstance(value, str):
            raise ValueError(f"Cannot parse type {type(value)}")
        
        # Limpia el string
        cleaned = self.clean_currency_string(value)
        
        if not cleaned or cleaned == '-':
            return Decimal('0')
        
        # Detecta el formato
        format_type = self.detect_format(cleaned)
        
        if format_type == 'us':
            return self.parse_us_format(cleaned)
        elif format_type == 'co':
            return self.parse_co_format(cleaned)
        else:
            # Intenta conversión directa como último recurso
            try:
                return Decimal(cleaned)
            except:
                raise ValueError(f"Cannot parse value: {value}")
    
    def parse_to_float(self, value: Union[str, int, float]) -> float:
        """
        Convierte a float para compatibilidad
        """
        return float(self.parse(value))


def create_parser() -> NumberParser:
    """
    Factory function para crear instancia del parser
    """
    return NumberParser()


# Función helper para uso rápido
def parse_currency(value: Union[str, int, float]) -> float:
    """
    Función de conveniencia para parsing rápido
    """
    parser = create_parser()
    return parser.parse_to_float(value)
