# Data Processor - Guía Rápida

Módulo para procesamiento de datos de extractos bancarios usando pandas.

## Uso Básico

### Procesar Todos los PDFs

```bash
python extract_with_pandas.py
```

### Procesar PDF Específico

```bash
python extract_with_pandas.py Extracto_857238199_202506_CTA_AHORROS_4332.pdf
```

### Exportar a Excel

```bash
python extract_with_pandas.py --format excel
```

### Exportar a CSV

```bash
python extract_with_pandas.py --format csv
```

### Modo Verbose (Mostrar Validaciones)

```bash
python extract_with_pandas.py --verbose
```

### Usar Carpeta Diferente

```bash
python extract_with_pandas.py --source data/
```

## API Programática

### Cuenta de Ahorros

```python
from data_processor import SavingsAccountProcessor

# Crear procesador
processor = SavingsAccountProcessor()

# Procesar PDF
data = processor.process("archivo.pdf", validate=True)

# Acceder a datos
print(data["info"])  # Información de cuenta
print(data["resumen"])  # Resumen financiero
print(data[" transacciones"])  # DataFrame de pandas

# Validación
if "validacion" in data:
    validation = data["validacion"]
    if validation.is_valid:
        print("✅ Datos válidos")
    else:
        print(f"❌ {len(validation.errors)} errores:")
        for error in validation.errors:
            print(f"  - {error}")

# Exportar
processor.export_to_excel(data, "output.xlsx")
processor.export_to_csv(data, "output.csv")
```

### Tarjeta de Crédito

```python
from data_processor import CreditCardProcessor

processor = CreditCardProcessor()
data = processor.process("tarjeta.pdf")

# Transacciones en pesos
if data["pesos"]:
    df_pesos = data["pesos"]["transacciones"]
    resumen = data["pesos"]["resumen"]
    print(f"Pago total: ${resumen['pago_total']:,.2f}")

# Exportar a Excel con todas las hojas
processor.export_to_excel(data, "tarjeta.xlsx")
```

## Estructura de Datos

### Cuenta de Ahorros

```python
{
    "info": {
        "titular": str,
        "numero": str,
        "tipo_cuenta": str,
        "sucursal": str,
        "direccion": str,
        "periodo_desde": date,
        "periodo_hasta": date
    },
    "resumen": {
        "saldo_anterior": float,
        "total_abonos": float,
        "total_cargos": float,
        "saldo_actual": float,
        "saldo_promedio": float,
        "intereses_pagados": float,
        "retefuente": float
    },
    "transacciones": DataFrame  # Columnas: fecha, descripcion, valor, saldo, tipo
    "validacion": ValidationResult  # Si validate=True
}
```

### Tarjeta de Crédito

```python
{
    "info": {...},  # Información de tarjeta
    "cupos": {...},  # Cupos y disponibles
    "pesos": {
        "transacciones": DataFrame,
        "resumen": {...},
        "pago_minimo": {...},
        "tasas": {...}
    },
    "dolares": {  # Si hay transacciones en dólares
        "transacciones": DataFrame,
        "resumen": {...}
    }
}
```

## Validaciones

El módulo valida automáticamente:

✅ **Consistencia de saldos**: Cada saldo = saldo_anterior + valor
✅ **Totales**: Suma de transacciones = totales declarados
✅ **Saldo final**: Último saldo = saldo_actual declarado

### Resultado de Validación

```python
validation = data["validacion"]

validation.is_valid  # bool
validation.errors    # list[str]
validation.warnings  # list[str]
validation.info      # dict con métricas
```

## Ventajas sobre extract_to_markdown.py

1. **Validación automática** de integridad de datos
2. **DataFrames de pandas** para análisis avanzado
3. **Exportación a Excel** con múltiples hojas
4. **Exportación a CSV** para procesamiento externo
5. **Detección de inconsistencias** con reportes detallados

## Ejemplos Avanzados

### Analizar Transacciones con Pandas

```python
from data_processor import SavingsAccountProcessor
import pandas as pd

processor = SavingsAccountProcessor()
data = processor.process("extracto.pdf")

df = data["transacciones"]

# Filtrar solo créditos
creditos = df[df["tipo"] == "credito"]
print(f"Total créditos: ${creditos['valor'].sum():,.2f}")

# Agrupar por tipo
resumen = df.groupby("tipo")["valor"].agg(["count", "sum", "mean"])
print(resumen)

# Transacciones mayores a $100,000
grandes = df[df["valor"].abs() > 100000]
print(grandes[["fecha", "descripcion", "valor"]])
```

### Consolidar Múltiples Extractos

```python
from pathlib import Path
import pandas as pd

processor = SavingsAccountProcessor()

# Procesar todos los extractos
extractos = Path("password-less").glob("*CTA_AHORROS*.pdf")
todos_df = []

for pdf in extractos:
    data = processor.process(pdf, validate=False)
    df = data["transacciones"].copy()
    df["archivo"] = pdf.stem
    todos_df.append(df)

# Consolidar
consolidado = pd.concat(todos_df, ignore_index=True)

# Exportar todo a Excel
consolidado.to_excel("todas_transacciones.xlsx", index=False)
```

## Notas

- El módulo es **independiente** de `pdf_analyzer` pero usa sus extractores base
- Compatible con Python 3.10+
- Requiere: `pandas>=2.0.0`, `openpyxl>=3.1.0`, `tabulate>=0.9.0`
