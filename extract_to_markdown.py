"""
Script para extraer información de PDFs y generar reportes en Markdown.

Uso:
    python extract_to_markdown.py                     # Procesa todos los PDFs
    python extract_to_markdown.py archivo.pdf         # Procesa un PDF específico
    python extract_to_markdown.py --source data/      # Usa carpeta específica
"""

import sys
from pathlib import Path
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf_analyzer import (
    LocalPDFRepository,
    SavingsAccountExtractor,
    CreditCardExtractor,
    ensure_directory,
)


def generate_savings_markdown(statement, filename: str) -> str:
    """Genera Markdown para extracto de cuenta de ahorros."""
    info = statement.account_info
    summary = statement.summary

    md = f"""# Extracto de Cuenta de Ahorros

**Archivo:** `{filename}`
**Generado:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Información de la Cuenta

| Campo | Valor |
|-------|-------|
| Titular | {info.titular} |
| Número de Cuenta | {info.numero} |
| Tipo | {info.tipo_cuenta} |
| Sucursal | {info.sucursal} |
| Dirección | {info.direccion} |
| Periodo | {info.periodo_desde} a {info.periodo_hasta} |

---

## Resumen Financiero

| Concepto | Valor |
|----------|------:|
| Saldo Anterior | ${summary.saldo_anterior:,.2f} |
| Total Abonos | ${summary.total_abonos:,.2f} |
| Total Cargos | ${summary.total_cargos:,.2f} |
| **Saldo Actual** | **${summary.saldo_actual:,.2f}** |
| Saldo Promedio | ${summary.saldo_promedio:,.2f} |
| Intereses Pagados | ${summary.intereses_pagados:,.2f} |
| Retefuente | ${summary.retefuente:,.2f} |

---

## Transacciones ({len(statement.transactions)})

| Fecha | Descripción | Valor | Saldo |
|-------|-------------|------:|------:|
"""

    for tx in statement.transactions:
        tipo = "+" if tx.es_credito else ""
        md += f"| {tx.fecha} | {tx.descripcion} | {tipo}${tx.valor:,.2f} | ${tx.saldo:,.2f} |\n"

    # Totales
    md += f"""
---

## Totales Calculados

| Concepto | Valor |
|----------|------:|
| Total Créditos | ${statement.total_creditos:,.2f} |
| Total Débitos | ${statement.total_debitos:,.2f} |
| Transacciones | {statement.total_transactions} |
"""

    return md


def generate_credit_card_markdown(statement, filename: str) -> str:
    """Genera Markdown para extracto de tarjeta de crédito."""
    info = statement.card_info
    limit = statement.credit_limit

    md = f"""# Extracto de Tarjeta de Crédito

**Archivo:** `{filename}`
**Generado:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Información de la Tarjeta

| Campo | Valor |
|-------|-------|
| Titular | {info.titular} |
| Tarjeta | {info.numero_tarjeta} |
| Dirección | {info.direccion} |
| Ciudad | {info.ciudad} |
| Periodo | {info.periodo_desde} a {info.periodo_hasta} |
| Fecha Límite Pago | {info.fecha_pago} |

---

## Cupos

| Concepto | Valor |
|----------|------:|
| Cupo Total | ${limit.cupo_total:,.2f} |
| Cupo Avances | ${limit.cupo_avances:,.2f} |
| Disponible Total | ${limit.disponible_total:,.2f} |
| Disponible Avances | ${limit.disponible_avances:,.2f} |

---

## Resumen de Pagos

| Concepto | Pesos | Dólares |
|----------|------:|--------:|
| Pago Total | ${statement.pago_total_pesos:,.2f} | ${statement.pago_total_dolares:,.2f} |
| Pago Mínimo | ${statement.pago_minimo_pesos:,.2f} | ${statement.pago_minimo_dolares:,.2f} |
"""

    # Estado de cuenta en Pesos
    if statement.pesos_statement:
        pesos = statement.pesos_statement
        balance = pesos.balance_summary
        minimum = pesos.minimum_payment
        rates = pesos.interest_rates

        md += f"""
---

## Estado de Cuenta en PESOS

### Resumen Saldo Total

| Concepto | Valor |
|----------|------:|
| Saldo Anterior | ${balance.saldo_anterior:,.2f} |
| + Compras del mes | ${balance.compras_mes:,.2f} |
| + Intereses corrientes | ${balance.intereses_corrientes:,.2f} |
| + Intereses de mora | ${balance.intereses_mora:,.2f} |
| + Avances | ${balance.avances:,.2f} |
| + Otros cargos | ${balance.otros_cargos:,.2f} |
| - Pagos/Abonos | ${balance.pagos_abonos:,.2f} |
| **= Pago Total** | **${balance.pago_total:,.2f}** |

### Resumen Pago Mínimo

| Concepto | Valor |
|----------|------:|
| Cuota compras del mes | ${minimum.cuota_compras_mes:,.2f} |
| + Intereses corrientes | ${minimum.intereses_corrientes:,.2f} |
| + Cuota avances | ${minimum.cuota_avances:,.2f} |
| + Otros cargos | ${minimum.otros_cargos:,.2f} |
| **= Pago Mínimo** | **${minimum.pago_minimo:,.2f}** |

### Tasas de Interés

| Tipo | M.V. | E.A. |
|------|-----:|-----:|
| Compra 1 mes | {rates.compra_un_mes_mv}% | {rates.compra_un_mes_ea}% |
| Compra 2-36 meses | {rates.compra_2_36_mv}% | {rates.compra_2_36_ea}% |
| Avances | {rates.avances_mv}% | {rates.avances_ea}% |
| Mora | {rates.mora_mv}% | {rates.mora_ea}% |

### Transacciones ({len(pesos.transactions)})

| Fecha | Descripción | Valor | Cuotas |
|-------|-------------|------:|--------|
"""
        for tx in pesos.transactions:
            cuotas = f"{tx.cuota_actual}/{tx.cuota_total}" if tx.cuota_total > 0 else "-"
            md += f"| {tx.fecha} | {tx.descripcion} | ${tx.cargos_abonos:,.2f} | {cuotas} |\n"

    # Estado de cuenta en Dólares
    if statement.dolares_statement:
        dolares = statement.dolares_statement
        balance = dolares.balance_summary

        if dolares.transactions:
            md += f"""
---

## Estado de Cuenta en DÓLARES

### Resumen

| Concepto | Valor |
|----------|------:|
| Pago Total | ${balance.pago_total:,.2f} |

### Transacciones ({len(dolares.transactions)})

| Fecha | Descripción | Valor | Cuotas |
|-------|-------------|------:|--------|
"""
            for tx in dolares.transactions:
                cuotas = f"{tx.cuota_actual}/{tx.cuota_total}" if tx.cuota_total > 0 else "-"
                md += f"| {tx.fecha} | {tx.descripcion} | ${tx.cargos_abonos:,.2f} | {cuotas} |\n"

    return md


def process_pdf(pdf_path: Path, output_dir: Path, savings_extractor, credit_extractor) -> bool:
    """Procesa un PDF y genera el Markdown correspondiente."""
    filename = pdf_path.name

    try:
        # Determinar tipo de extracto por nombre
        if "CTA_AHORROS" in filename:
            print(f"  Tipo: Cuenta de Ahorros")
            statement = savings_extractor.extract(pdf_path)
            markdown = generate_savings_markdown(statement, filename)

        elif "TARJETA_MASTERCARD" in filename:
            print(f"  Tipo: Tarjeta MasterCard")
            statement = credit_extractor.extract(pdf_path)
            markdown = generate_credit_card_markdown(statement, filename)

        else:
            print(f"  Tipo desconocido, saltando...")
            return False

        # Guardar Markdown
        output_file = output_dir / f"{pdf_path.stem}.md"
        output_file.write_text(markdown, encoding="utf-8")
        print(f"  Generado: {output_file.name}")
        return True

    except (OSError, ValueError, RuntimeError) as e:
        print(f"  ERROR: {e}")
        return False


def main():
    # Parsear argumentos
    args = sys.argv[1:]
    source_dir = Path(__file__).parent / "password-less"

    # Buscar --source
    for i, arg in enumerate(args):
        if arg == "--source" and i + 1 < len(args):
            source_dir = Path(args[i + 1])
            args = args[:i] + args[i + 2:]
            break

    # Crear carpeta de salida
    output_dir = Path(__file__).parent / "data-extracted"
    ensure_directory(output_dir)
    print(f"Carpeta de salida: {output_dir}")

    # Inicializar extractores
    savings_extractor = SavingsAccountExtractor()
    credit_extractor = CreditCardExtractor()

    # Filtrar PDFs específicos o procesar todos
    pdf_args = [a for a in args if not a.startswith("--")]

    if pdf_args:
        # Procesar PDFs específicos
        pdfs = []
        for pdf_name in pdf_args:
            pdf_path = Path(pdf_name)
            if not pdf_path.is_absolute():
                pdf_path = source_dir / pdf_name
            if pdf_path.exists():
                pdfs.append(pdf_path)
            else:
                print(f"No encontrado: {pdf_path}")
    else:
        # Procesar todos los PDFs de la carpeta
        if not source_dir.exists():
            print(f"Carpeta no existe: {source_dir}")
            return

        pdfs = sorted(source_dir.glob("*.pdf"))

    if not pdfs:
        print("No se encontraron PDFs")
        return

    print(f"Procesando {len(pdfs)} PDFs...\n")

    success = 0
    errors = 0

    for pdf_path in pdfs:
        print(f"Procesando: {pdf_path.name}")
        if process_pdf(pdf_path, output_dir, savings_extractor, credit_extractor):
            success += 1
        else:
            errors += 1
        print()

    print("=" * 50)
    print(f"Completado: {success} exitosos, {errors} errores")
    print(f"Archivos en: {output_dir}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario.")
        sys.exit(0)
