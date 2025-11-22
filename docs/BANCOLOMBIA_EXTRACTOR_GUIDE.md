# Extractor de PDFs de Bancolombia - Guía de Uso

## Resumen de la Solución

### Problema Resuelto
El problema principal era extraer datos de PDFs de Bancolombia manejando correctamente los **formatos numéricos mixtos**:
- Formato US: `1,234,567.89` (coma para miles, punto para decimales)
- Formato CO: `1.234.567,89` (punto para miles, coma para decimales)

### Componentes Desarrollados

1. **number_parser.py** - Parser inteligente de números
   - Detecta automáticamente el formato (US o CO)
   - Convierte correctamente a float/Decimal
   - Maneja símbolos de moneda y espacios

2. **bancolombia_extractor.py** - Extractor de PDFs
   - Soporta extractos de cuenta de ahorros
   - Soporta extractos de tarjeta de crédito
   - Extrae header, resumen y transacciones
   - Exporta a JSON y CSV

3. **test_extraction.py** - Suite de pruebas
   - Valida el parser de números
   - Prueba extracción de ambos tipos de PDFs
   - Genera outputs de ejemplo

## Uso Básico

### 1. Uso Rápido (Función Helper)

```python
from bancolombia_extractor import process_bancolombia_pdf

# Exportar a JSON
json_output = process_bancolombia_pdf('extracto.pdf', output_format='json')

# Exportar a CSV
csv_path = process_bancolombia_pdf('extracto.pdf', output_format='csv')
```

### 2. Uso Avanzado (Control Total)

```python
from bancolombia_extractor import BancolombiaExtractor

# Crea instancia del extractor
extractor = BancolombiaExtractor()

# Extrae datos estructurados
data = extractor.extract_text_sections('extracto.pdf')

# Accede a las secciones
print(data['header'])        # Info de cuenta y periodo
print(data['summary'])       # Resumen de saldos
print(data['transactions'])  # Lista de Transaction objects

# Exporta manualmente
extractor.extract_to_json('extracto.pdf', 'output.json')
extractor.extract_to_csv('extracto.pdf', 'output.csv')
```

### 3. Parser de Números Independiente

```python
from number_parser import NumberParser

parser = NumberParser()

# Detecta y convierte automáticamente
parser.parse_to_float('$ 1,400,000.00')  # 1400000.0
parser.parse_to_float('1.305.022,88')    # 1305022.88
parser.parse_to_float('-300,000.00')     # -300000.0
```

## Estructura de Datos

### Transaction Object

```python
@dataclass
class Transaction:
    date: str                        # Fecha de transacción
    description: str                 # Descripción
    amount: float                    # Monto (negativo = débito)
    balance: Optional[float]         # Saldo después de transacción
    authorization: Optional[str]     # Código de autorización (tarjetas)
    installments: Optional[str]      # Cuotas (tarjetas)
```

### Estructura JSON de Salida

```json
{
  "header": {
    "period_start": "2025/03/31",
    "period_end": "2025/06/30",
    "account_number": "25321894332"
  },
  "summary": {
    "previous_balance": 1305022.88,
    "current_balance": 749441.08,
    "total_credits": 14422565.0,
    "total_debits": 14978146.8
  },
  "transactions": [
    {
      "date": "1/04",
      "description": "TRANSFERENCIA DESDE NEQUI",
      "amount": 2560000.0,
      "balance": 3865022.88,
      "authorization": null,
      "installments": null
    }
  ]
}
```

## Análisis de Datos

### Ejemplo: Análisis de Gastos

```python
from bancolombia_extractor import BancolombiaExtractor

extractor = BancolombiaExtractor()
data = extractor.extract_text_sections('extracto.pdf')

# Filtra por tipo de transacción
debits = [t for t in data['transactions'] if t.amount < 0]
credits = [t for t in data['transactions'] if t.amount > 0]

# Calcula totales
total_debits = sum(t.amount for t in debits)
total_credits = sum(t.amount for t in credits)

print(f"Total Débitos: ${abs(total_debits):,.2f}")
print(f"Total Créditos: ${total_credits:,.2f}")
print(f"Balance Neto: ${total_credits + total_debits:,.2f}")

# Agrupa por tipo de gasto
from collections import defaultdict

gastos_por_tipo = defaultdict(float)
for t in debits:
    if 'UBER' in t.description:
        gastos_por_tipo['Transporte'] += abs(t.amount)
    elif 'QR' in t.description:
        gastos_por_tipo['Pagos QR'] += abs(t.amount)
    elif 'TRANSFERENCIA' in t.description:
        gastos_por_tipo['Transferencias'] += abs(t.amount)
    else:
        gastos_por_tipo['Otros'] += abs(t.amount)

for tipo, monto in gastos_por_tipo.items():
    print(f"{tipo}: ${monto:,.2f}")
```

### Ejemplo: Exportar a Excel con Análisis

```python
import pandas as pd
from bancolombia_extractor import BancolombiaExtractor

extractor = BancolombiaExtractor()
data = extractor.extract_text_sections('extracto.pdf')

# Convierte a DataFrame
df = pd.DataFrame([t.to_dict() for t in data['transactions']])

# Convierte fecha a datetime
df['date'] = pd.to_datetime(df['date'], format='%d/%m')

# Agrega columnas de análisis
df['tipo'] = df['amount'].apply(lambda x: 'Crédito' if x > 0 else 'Débito')
df['mes'] = df['date'].dt.month

# Exporta a Excel con formato
with pd.ExcelWriter('analisis_extracto.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Transacciones', index=False)
    
    # Hoja de resumen
    resumen = df.groupby('tipo')['amount'].agg(['count', 'sum']).reset_index()
    resumen.to_excel(writer, sheet_name='Resumen', index=False)
```

## Casos de Uso Avanzados

### 1. Procesamiento por Lotes

```python
import os
from bancolombia_extractor import BancolombiaExtractor

extractor = BancolombiaExtractor()

# Directorio con múltiples PDFs
pdf_dir = '/path/to/pdfs'
output_dir = '/path/to/outputs'

for filename in os.listdir(pdf_dir):
    if filename.endswith('.pdf'):
        pdf_path = os.path.join(pdf_dir, filename)
        output_name = filename.replace('.pdf', '.json')
        output_path = os.path.join(output_dir, output_name)
        
        try:
            extractor.extract_to_json(pdf_path, output_path)
            print(f"✓ Processed: {filename}")
        except Exception as e:
            print(f"✗ Error in {filename}: {e}")
```

### 2. Integración con Base de Datos

```python
import sqlite3
from bancolombia_extractor import BancolombiaExtractor

# Conexión a DB
conn = sqlite3.connect('extractos.db')
cursor = conn.cursor()

# Crea tabla
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        description TEXT,
        amount REAL,
        balance REAL,
        account_number TEXT,
        extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Extrae y guarda
extractor = BancolombiaExtractor()
data = extractor.extract_text_sections('extracto.pdf')

account_number = data['header'].get('account_number', '')

for transaction in data['transactions']:
    cursor.execute('''
        INSERT INTO transactions (date, description, amount, balance, account_number)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        transaction.date,
        transaction.description,
        transaction.amount,
        transaction.balance,
        account_number
    ))

conn.commit()
conn.close()
```

### 3. API REST con Flask

```python
from flask import Flask, request, jsonify
from bancolombia_extractor import BancolombiaExtractor
import tempfile
import os

app = Flask(__name__)
extractor = BancolombiaExtractor()

@app.route('/extract', methods=['POST'])
def extract_pdf():
    # Verifica que se subió un archivo
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Guarda temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name
    
    try:
        # Extrae datos
        data = extractor.extract_text_sections(tmp_path)
        
        # Convierte a dict serializable
        response = {
            'header': data['header'],
            'summary': data['summary'],
            'transactions': [t.to_dict() for t in data['transactions']],
            'total_transactions': len(data['transactions'])
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
    finally:
        # Limpia archivo temporal
        os.unlink(tmp_path)

if __name__ == '__main__':
    app.run(debug=True)
```

## Solución de Problemas

### 1. Error: "Cannot parse value"

**Causa**: Formato numérico no reconocido

**Solución**: Verifica que el valor sea un número válido. El parser maneja:
- `1,234,567.89` (US)
- `1.234.567,89` (CO)
- `-123.45` (negativos)
- `$ 123.45` (con símbolos)

### 2. No se extraen transacciones

**Causa**: Formato de PDF diferente al esperado

**Solución**: 
1. Verifica que el PDF sea de Bancolombia
2. Asegúrate que no esté encriptado
3. Revisa que contenga texto (no sea solo imagen)

### 3. Valores incorrectos

**Causa**: Confusión entre formato US y CO

**Solución**: El parser detecta automáticamente, pero si falla:
```python
# Forzar formato específico
parser.parse_us_format('1,234.56')  # 1234.56
parser.parse_co_format('1.234,56')  # 1234.56
```

## Mejores Prácticas

1. **Validación de Datos**
   ```python
   # Siempre valida los datos extraídos
   if data['transactions']:
       print(f"✓ Extraídas {len(data['transactions'])} transacciones")
   else:
       print("⚠ No se encontraron transacciones")
   ```

2. **Manejo de Errores**
   ```python
   # Usa try-except para manejo robusto
   try:
       data = extractor.extract_text_sections(pdf_path)
   except Exception as e:
       logger.error(f"Error extracting {pdf_path}: {e}")
       # Implementa lógica de retry o notificación
   ```

3. **Performance**
   ```python
   # Para múltiples PDFs, considera procesamiento paralelo
   from concurrent.futures import ProcessPoolExecutor
   
   def process_pdf(path):
       extractor = BancolombiaExtractor()
       return extractor.extract_text_sections(path)
   
   with ProcessPoolExecutor(max_workers=4) as executor:
       results = executor.map(process_pdf, pdf_paths)
   ```

## Resultado de Tests

```
TESTING NUMBER PARSER
✓ PASS: US Format with currency (10/10 tests passed)
✓ PASS: US Format
✓ PASS: Negative US Format
✓ PASS: CO Format
✓ PASS: Negative CO Format

TESTING PDF EXTRACTION
✓ Cuenta de Ahorros: 33 transacciones extraídas
✓ Tarjeta de Crédito: 18 transacciones extraídas
```

## Archivos Generados

Para tus PDFs se generaron:
1. `Extracto_857238199_202506_CTA_AHORROS_4332.json` - 33 transacciones
2. `Extracto_857238199_202506_CTA_AHORROS_4332.csv`
3. `Extracto_871741206_202507_TARJETA_MASTERCARD_1325.json` - 18 transacciones
4. `Extracto_871741206_202507_TARJETA_MASTERCARD_1325.csv`
