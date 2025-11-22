"""
Script para extraer información de PDFs usando el módulo data_processor con pandas.

Este script reemplaza extract_to_markdown.py con capacidades mejoradas:
- Validación de datos con reportes detallados
- Exportación a múltiples formatos (Markdown, CSV, Excel)
- Detección de inconsistencias

Uso:
    python extract_with_pandas.py                          # Procesa todos los PDFs
    python extract_with_pandas.py archivo.pdf              # PDF específico
    python extract_with_pandas.py --source password-less/  # Carpeta específica
    python extract_with_pandas.py --format excel           # Exportar a Excel
    python extract_with_pandas.py --format csv             # Exportar a CSV
    python extract_with_pandas.py --no-markdown            # No generar Markdown
    python extract_with_pandas.py --verbose                # Modo detallado
"""

import sys
from pathlib import Path
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from tabulate import tabulate

from data_processor import SavingsAccountProcessor, CreditCardProcessor
from pdf_analyzer import ensure_directory

# Cargar variables de entorno
load_dotenv()


def generate_savings_markdown(data: dict, filename: str) -> str:
    """Genera Markdown para cuenta de ahorros con validación incluida."""
    info = data["info"]
    resumen = data["resumen"]
    df = data["transacciones"]
    
    md = f"""# Extracto de Cuenta de Ahorros

**Archivo:** `{filename}`
**Generado:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Información de la Cuenta

| Campo | Valor |
|-------|-------|
| Titular | {info['titular']} |
| Número de Cuenta | {info['numero']} |
| Tipo | {info['tipo_cuenta']} |
| Sucursal | {info['sucursal']} |
| Dirección | {info['direccion']} |
| Periodo | {info['periodo_desde']} a {info['periodo_hasta']} |

---

## Resumen Financiero

| Concepto | Valor |
|----------|------:|
| Saldo Anterior | ${resumen['saldo_anterior']:,.2f} |
| Total Abonos | ${resumen['total_abonos']:,.2f} |
| Total Cargos | ${resumen['total_cargos']:,.2f} |
| **Saldo Actual** | **${resumen['saldo_actual']:,.2f}** |
| Saldo Promedio | ${resumen['saldo_promedio']:,.2f} |
| Intereses Pagados | ${resumen['intereses_pagados']:,.2f} |
| Retefuente | ${resumen['retefuente']:,.2f} |

---

## Transacciones ({len(df)})

| Fecha | Descripción | Valor | Saldo |
|-------|-------------|------:|------:|
"""

    for _, row in df.iterrows():
        signo = "+" if row["tipo"] == "credito" else ""
        md += f"| {row['fecha']} | {row['descripcion']} | {signo}${row['valor']:,.2f} | ${row['saldo']:,.2f} |\n"

    # Validación
    if "validacion" in data:
        validation = data["validacion"]
        md += "\n---\n\n## Validación de Datos\n\n"
        
        if validation.is_valid:
            md += "✅ **Todos los datos son consistentes**\n"
        else:
            md += f"❌ **Se encontraron {len(validation.errors)} errores**\n\n"
            for error in validation.errors:
                md += f"- {error}\n"
        
        if validation.warnings:
            md += f"\n⚠️ **Advertencias ({len(validation.warnings)})**\n\n"
            for warning in validation.warnings:
                md += f"- {warning}\n"

    return md


def generate_credit_card_markdown(data: dict, filename: str) -> str:
    """Genera Markdown para tarjeta de crédito."""
    info = data["info"]
    cupos = data["cupos"]
    
    md = f"""# Extracto de Tarjeta de Crédito

**Archivo:** `{filename}`
**Generado:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Información de la Tarjeta

| Campo | Valor |
|-------|-------|
| Titular | {info['titular']} |
| Tarjeta | {info['numero_tarjeta']} |
| Dirección | {info['direccion']} |
| Ciudad | {info['ciudad']} |
| Periodo | {info['periodo_desde']} a {info['periodo_hasta']} |
| Fecha Límite Pago | {info['fecha_pago']} |

---

## Cupos

| Concepto | Valor |
|----------|------:|
| Cupo Total | ${cupos['cupo_total']:,.2f} |
| Cupo Avances | ${cupos['cupo_avances']:,.2f} |
| Disponible Total | ${cupos['disponible_total']:,.2f} |
| Disponible Avances | ${cupos['disponible_avances']:,.2f} |

"""

    # Estado de cuenta en Pesos
    if data["pesos"]:
        pesos = data["pesos"]
        balance = pesos["resumen"]
        pago_min = pesos["pago_minimo"]
        tasas = pesos["tasas"]
        
        md += f"""---

## Estado de Cuenta en PESOS

### Resumen Saldo Total

| Concepto | Valor |
|----------|------:|
| Saldo Anterior | ${balance['saldo_anterior']:,.2f} |
| + Compras del mes | ${balance['compras_mes']:,.2f} |
| + Intereses corrientes | ${balance['intereses_corrientes']:,.2f} |
| + Intereses de mora | ${balance['intereses_mora']:,.2f} |
| + Avances | ${balance['avances']:,.2f} |
| + Otros cargos | ${balance['otros_cargos']:,.2f} |
| - Pagos/Abonos | ${balance['pagos_abonos']:,.2f} |
| **= Pago Total** | **${balance['pago_total']:,.2f}** |

### Resumen Pago Mínimo

| Concepto | Valor |
|----------|------:|
| Cuota compras del mes | ${pago_min['cuota_compras_mes']:,.2f} |
| + Intereses corrientes | ${pago_min['intereses_corrientes']:,.2f} |
| + Cuota avances | ${pago_min['cuota_avances']:,.2f} |
| + Otros cargos | ${pago_min['otros_cargos']:,.2f} |
| **= Pago Mínimo** | **${pago_min['pago_minimo']:,.2f}** |

### Transacciones ({len(pesos['transacciones'])})

| Fecha | Descripción | Valor | Cuotas |
|-------|-------------|------:|--------|
"""

        for _, row in pesos['transacciones'].iterrows():
            md += f"| {row['fecha']} | {row['descripcion']} | ${row['cargos_abonos']:,.2f} | {row['cuotas']} |\n"

    # Estado de cuenta en Dólares
    if data["dolares"]:
        dolares = data["dolares"]
        
        if not dolares["transacciones"].empty:
            md += f"""---

## Estado de Cuenta en DÓLARES

### Transacciones ({len(dolares['transacciones'])})

| Fecha | Descripción | Valor | Cuotas |
|-------|-------------|------:|--------|
"""
            for _, row in dolares['transacciones'].iterrows():
                md += f"| {row['fecha']} | {row['descripcion']} | ${row['cargos_abonos']:,.2f} | {row['cuotas']} |\n"

    return md


def process_pdf(
    pdf_path: Path,
    output_dir: Path,
    savings_processor: SavingsAccountProcessor,
    credit_processor: CreditCardProcessor,
    options: dict,
) -> bool:
    """Procesa un PDF con el procesador correspondiente."""
    filename = pdf_path.name
    
    try:
        # Determinar tipo
        if "CTA_AHORROS" in filename:
            print(f"  Tipo: Cuenta de Ahorros")
            data = savings_processor.process(pdf_path, validate=True)
            
            # Generar Markdown
            if not options.get("no_markdown"):
                markdown = generate_savings_markdown(data, filename)
                md_file = output_dir / f"{pdf_path.stem}.md"
                md_file.write_text(markdown, encoding="utf-8")
                print(f"  ✓ Markdown: {md_file.name}")
            
            # Exportar según formato
            if options.get("format") == "csv":
                csv_file = output_dir / f"{pdf_path.stem}.csv"
                savings_processor.export_to_csv(data, csv_file)
                print(f"  ✓ CSV: {csv_file.name}")
            elif options.get("format") == "excel":
                excel_file = output_dir / f"{pdf_path.stem}.xlsx"
                savings_processor.export_to_excel(data, excel_file)
                print(f"  ✓ Excel: {excel_file.name}")
            
            # Mostrar validación
            if options.get("verbose") and "validacion" in data:
                print(f"\n{data['validacion']}\n")
                
        elif "TARJETA_MASTERCARD" in filename:
            print(f"  Tipo: Tarjeta MasterCard")
            data = credit_processor.process(pdf_path)
            
            # Generar Markdown
            if not options.get("no_markdown"):
                markdown = generate_credit_card_markdown(data, filename)
                md_file = output_dir / f"{pdf_path.stem}.md"
                md_file.write_text(markdown, encoding="utf-8")
                print(f"  ✓ Markdown: {md_file.name}")
            
            # Exportar según formato
            if options.get("format") == "excel":
                excel_file = output_dir / f"{pdf_path.stem}.xlsx"
                credit_processor.export_to_excel(data, excel_file)
                print(f"  ✓ Excel: {excel_file.name}")
        else:
            print(f"  Tipo desconocido, saltando...")
            return False
            
        return True
        
    except Exception as e:  # pylint: disable=broad-except
        print(f"  ERROR: {e}")
        if options.get("verbose"):
            import traceback
            traceback.print_exc()
        return False


def main():
    # Parsear argumentos
    args = sys.argv[1:]
    
    options = {
        "verbose": "--verbose" in args,
        "no_markdown": "--no-markdown" in args,
        "format": None,
    }
    
    # Formato de exportación
    if "--format" in args:
        idx = args.index("--format")
        if idx + 1 < len(args):
            options["format"] = args[idx + 1]
    
    # Directorio fuente
    source_dir = Path(__file__).parent.parent / "password-less"
    if "--source" in args:
        idx = args.index("--source")
        if idx + 1 < len(args):
            source_dir = Path(args[idx + 1])
    
    # Directorio de salida
    output_dir = Path(__file__).parent.parent / "data-extracted"
    ensure_directory(output_dir)
    
    print(f"📂 Fuente: {source_dir}")
    print(f"📂 Salida: {output_dir}")
    print()
    
    # Inicializar procesadores
    savings_processor = SavingsAccountProcessor()
    credit_processor = CreditCardProcessor()
    
    # Obtener PDFs a procesar
    pdf_args = [a for a in args if not a.startswith("--") and a.endswith(".pdf")]
    
    if pdf_args:
        pdfs = []
        for pdf_name in pdf_args:
            pdf_path = Path(pdf_name)
            if not pdf_path.is_absolute():
                pdf_path = source_dir / pdf_name
            if pdf_path.exists():
                pdfs.append(pdf_path)
            else:
                print(f"❌ No encontrado: {pdf_path}")
    else:
        if not source_dir.exists():
            print(f"❌ Carpeta no existe: {source_dir}")
            return
        pdfs = sorted(source_dir.glob("*.pdf"))
    
    if not pdfs:
        print("❌ No se encontraron PDFs")
        return
    
    print(f"📄 Procesando {len(pdfs)} PDFs...\n")
    
    success = 0
    errors = 0
    
    for pdf_path in pdfs:
        print(f"Procesando: {pdf_path.name}")
        if process_pdf(pdf_path, output_dir, savings_processor, credit_processor, options):
            success += 1
        else:
            errors += 1
        print()
    
    print("=" * 60)
    print(f"✅ Completado: {success} exitosos, {errors} errores")
    print(f"📂 Archivos en: {output_dir}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por el usuario.")
        sys.exit(0)
