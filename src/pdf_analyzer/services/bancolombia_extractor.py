from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import json
import pdfplumber

from pdf_analyzer.services.utils.number_parser import NumberParser


@dataclass
class Transaction:
    """
    Representa una transacción individual
    """
    date: str
    description: str
    amount: float
    balance: Optional[float] = None
    authorization: Optional[str] = None
    installments: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AccountSummary:
    """
    Resumen de la cuenta
    """
    account_number: str
    account_holder: str
    period_start: str
    period_end: str
    previous_balance: float
    current_balance: float
    total_credits: float
    total_debits: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BancolombiaExtractor:
    """
    Extractor especializado para extractos de Bancolombia
    """
    
    def __init__(self, password: Optional[str] = None):
        self.parser = NumberParser()
        self.password = password
    
    def extract_text_sections(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extrae secciones de texto del PDF
        """
        sections = {
            'header': {},
            'summary': {},
            'transactions': []
        }
        
        with pdfplumber.open(pdf_path, password=self.password) as pdf:
            full_text = ""
            
            for page in pdf.pages:
                text = page.extract_text()
                
                if text:
                    full_text += text + "\n"
                    
                    # Extrae información del header
                    if 'CUENTA DE AHORROS' in text or 'TARJETA' in text:
                        sections['header'] = self._extract_header(text)
                
                # Intenta primero con extract_tables
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        if self._is_transaction_table(table):
                            sections['transactions'].extend(
                                self._parse_transaction_table(table)
                            )
            
            # Extrae summary del texto completo
            sections['summary'] = self._extract_summary(full_text)
            
            # Si no encuentra tablas, parsea el texto directamente
            if not sections['transactions']:
                sections['transactions'].extend(
                    self._extract_transactions_from_text(full_text)
                )
        
        return sections
    
    def _extract_header(self, text: str) -> Dict[str, str]:
        """
        Extrae información del encabezado
        """
        lines = text.split('\n')
        header = {}
        
        for i, line in enumerate(lines):
            if 'NÚMERO' in line and i + 1 < len(lines):
                header['account_number'] = lines[i + 1].strip()
            elif 'DESDE:' in line:
                # Extrae fechas del periodo
                parts = line.split()
                for j, part in enumerate(parts):
                    if part == 'DESDE:' and j + 1 < len(parts):
                        header['period_start'] = parts[j + 1]
                    elif part == 'HASTA:' and j + 1 < len(parts):
                        header['period_end'] = parts[j + 1]
        
        return header
    
    def _extract_summary(self, text: str) -> Dict[str, float]:
        """
        Extrae el resumen de saldos
        """
        import re
        
        summary = {}
        
        # Patrones para extraer valores del resumen
        patterns = {
            'previous_balance': r'SALDO ANTERIOR\s+\$?\s*([\d,.-]+)',
            'current_balance': r'SALDO ACTUAL\s+\$?\s*([\d,.-]+)',
            'total_credits': r'TOTAL ABONOS\s+\$?\s*([\d,.-]+)',
            'total_debits': r'TOTAL CARGOS\s+\$?\s*([\d,.-]+)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                try:
                    summary[key] = self.parser.parse_to_float(match.group(1))
                except:
                    summary[key] = 0.0
        
        return summary
    
    def _is_transaction_table(self, table: List[List[str]]) -> bool:
        """
        Verifica si una tabla contiene transacciones
        """
        if not table or len(table) < 2:
            return False
        
        # Busca headers típicos de transacciones
        header_keywords = ['FECHA', 'DESCRIPCIÓN', 'VALOR', 'SALDO']
        first_row = [cell.upper() if cell else '' for cell in table[0]]
        
        return any(keyword in ' '.join(first_row) for keyword in header_keywords)
    
    def _extract_transactions_from_text(self, text: str) -> List[Transaction]:
        """
        Extrae transacciones parseando el texto directamente
        Usado cuando extract_tables no funciona
        """
        import re
        
        transactions = []
        lines = text.split('\n')
        
        # Detecta el tipo de extracto
        is_credit_card = 'TARJETA' in text or 'Número de\nAutorización' in text
        
        if is_credit_card:
            return self._extract_credit_card_transactions(lines)
        else:
            return self._extract_account_transactions(lines)
    
    def _extract_account_transactions(self, lines: List[str]) -> List[Transaction]:
        """
        Extrae transacciones de cuenta de ahorros/corriente
        """
        import re
        
        transactions = []
        
        # Encuentra donde empiezan las transacciones
        start_index = -1
        for i, line in enumerate(lines):
            if 'FECHA' in line and ('DESCRIPCIÓN' in line or 'VALOR' in line):
                start_index = i + 1
                break
        
        if start_index == -1:
            return transactions
        
        # Patrón para líneas de transacción
        transaction_pattern = re.compile(r'^(\d{1,2}/\d{2})\s+(.+?)(-?[\d,.-]+)\s+(-?[\d,.-]+)$')
        
        for line in lines[start_index:]:
            if not line.strip() or 'DCF:' in line or 'PÁGINA' in line:
                continue
            
            match = transaction_pattern.match(line.strip())
            
            if match:
                date = match.group(1)
                description = match.group(2).strip()
                amount_str = match.group(3).strip()
                balance_str = match.group(4).strip()
                
                try:
                    amount = self.parser.parse_to_float(amount_str)
                    balance = self.parser.parse_to_float(balance_str)
                    
                    transaction = Transaction(
                        date=date,
                        description=description,
                        amount=amount,
                        balance=balance
                    )
                    
                    transactions.append(transaction)
                except:
                    continue
        
        return transactions
    
    def _extract_credit_card_transactions(self, lines: List[str]) -> List[Transaction]:
        """
        Extrae transacciones de tarjeta de crédito
        Formato: [Auth] [Date] [Description] [Amount] [Rates...] [Charges] [Balance] [Installments]
        """
        import re
        
        transactions = []
        
        # Encuentra donde empiezan las transacciones
        start_index = -1
        for i, line in enumerate(lines):
            # Busca el header de tarjeta (puede estar en varias líneas)
            if 'Número de' in line or 'Autorización' in line:
                # Las transacciones empiezan después del header (usualmente 3-4 líneas)
                start_index = i + 3
                break
        
        if start_index == -1:
            return transactions
        
        # Patrón para líneas de transacción de tarjeta
        # Puede empezar con código de autorización o fecha directa
        patterns = [
            # Con autorización: CODE DD/MM/YYYY DESCRIPTION AMOUNT ...
            re.compile(r'^([A-Z0-9]+)\s+(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([\d,.-]+)\s+'),
            # Sin autorización: DD/MM/YYYY DESCRIPTION AMOUNT ...
            re.compile(r'^(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([\d,.-]+)\s+'),
        ]
        
        for line in lines[start_index:]:
            if not line.strip() or 'DCF:' in line or 'Pag.' in line:
                continue
            
            # Intenta con patrón de autorización primero
            match = patterns[0].match(line.strip())
            if match:
                auth = match.group(1)
                date = match.group(2)
                description = match.group(3).strip()
                amount_str = match.group(4).strip()
                
                # El monto puede tener '-' al final para indicar crédito
                if amount_str.endswith('-'):
                    amount_str = '-' + amount_str[:-1]
                
                try:
                    amount = self.parser.parse_to_float(amount_str)
                    
                    transaction = Transaction(
                        date=date,
                        description=description,
                        amount=amount,
                        authorization=auth
                    )
                    
                    transactions.append(transaction)
                except Exception as e:
                    continue
            else:
                # Intenta sin autorización
                match = patterns[1].match(line.strip())
                if match:
                    date = match.group(1)
                    description = match.group(2).strip()
                    amount_str = match.group(3).strip()
                    
                    if amount_str.endswith('-'):
                        amount_str = '-' + amount_str[:-1]
                    
                    try:
                        amount = self.parser.parse_to_float(amount_str)
                        
                        transaction = Transaction(
                            date=date,
                            description=description,
                            amount=amount
                        )
                        
                        transactions.append(transaction)
                    except:
                        continue
        
        return transactions
    
    def _parse_transaction_table(self, table: List[List[str]]) -> List[Transaction]:
        """
        Procesa una tabla de transacciones
        """
        transactions = []
        
        # Identifica índices de columnas
        header = table[0]
        col_indices = self._identify_columns(header)
        
        # Procesa cada fila (salta el header)
        for row in table[1:]:
            if not row or all(not cell for cell in row):
                continue
            
            try:
                transaction = self._parse_transaction_row(row, col_indices)
                if transaction:
                    transactions.append(transaction)
            except Exception as e:
                # Log error pero continúa procesando
                print(f"Error parsing row: {row}, Error: {e}")
                continue
        
        return transactions
    
    def _identify_columns(self, header: List[str]) -> Dict[str, int]:
        """
        Identifica los índices de las columnas importantes
        """
        indices = {}
        
        for i, cell in enumerate(header):
            if not cell:
                continue
            
            cell_upper = cell.upper()
            
            if 'FECHA' in cell_upper:
                indices['date'] = i
            elif 'DESCRIPCIÓN' in cell_upper or 'DESCRIPCION' in cell_upper:
                indices['description'] = i
            elif 'VALOR' in cell_upper and 'SALDO' not in cell_upper:
                indices['amount'] = i
            elif 'SALDO' in cell_upper:
                indices['balance'] = i
            elif 'AUTORIZACIÓN' in cell_upper or 'AUTORIZACION' in cell_upper:
                indices['authorization'] = i
            elif 'CUOTAS' in cell_upper:
                indices['installments'] = i
        
        return indices
    
    def _parse_transaction_row(
        self, 
        row: List[str], 
        col_indices: Dict[str, int]
    ) -> Optional[Transaction]:
        """
        Convierte una fila en un objeto Transaction
        """
        # Extrae valores según los índices identificados
        date = row[col_indices.get('date', 0)] if 'date' in col_indices else ''
        description = row[col_indices.get('description', 1)] if 'description' in col_indices else ''
        amount_str = row[col_indices.get('amount', 2)] if 'amount' in col_indices else '0'
        
        # Valida que tenga información mínima
        if not date or not description:
            return None
        
        # Parsea el monto usando el NumberParser
        try:
            amount = self.parser.parse_to_float(amount_str)
        except:
            amount = 0.0
        
        # Parsea balance si existe
        balance = None
        if 'balance' in col_indices:
            balance_str = row[col_indices['balance']]
            try:
                balance = self.parser.parse_to_float(balance_str)
            except:
                pass
        
        # Campos opcionales
        authorization = row[col_indices.get('authorization', -1)] if 'authorization' in col_indices else None
        installments = row[col_indices.get('installments', -1)] if 'installments' in col_indices else None
        
        return Transaction(
            date=date.strip(),
            description=description.strip(),
            amount=amount,
            balance=balance,
            authorization=authorization.strip() if authorization else None,
            installments=installments.strip() if installments else None
        )
    
    def extract_to_json(self, pdf_path: str, output_path: Optional[str] = None) -> str:
        """
        Extrae datos y los convierte a JSON
        """
        data = self.extract_text_sections(pdf_path)
        
        # Convierte transacciones a diccionarios
        data['transactions'] = [t.to_dict() for t in data['transactions']]
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
        
        return json_str
    
    def extract_to_csv(self, pdf_path: str, output_path: str):
        """
        Extrae transacciones a CSV
        """
        import csv
        
        data = self.extract_text_sections(pdf_path)
        transactions = data['transactions']
        
        if not transactions:
            print("No transactions found")
            return
        
        # Obtiene todas las keys de las transacciones
        fieldnames = list(transactions[0].to_dict().keys())
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for transaction in transactions:
                writer.writerow(transaction.to_dict())


def process_bancolombia_pdf(pdf_path: str, output_format: str = 'json') -> str:
    """
    Función helper para procesamiento rápido
    """
    extractor = BancolombiaExtractor()
    
    if output_format == 'json':
        output_path = pdf_path.replace('.pdf', '.json')
        return extractor.extract_to_json(pdf_path, output_path)
    elif output_format == 'csv':
        output_path = pdf_path.replace('.pdf', '.csv')
        extractor.extract_to_csv(pdf_path, output_path)
        return output_path
    else:
        raise ValueError(f"Unsupported format: {output_format}")
