"""
Script para explorar la estructura de los PDFs usando ExtractorService.

Uso:
    python explore_pdfs.py                    # Explora todos los PDFs
    python explore_pdfs.py archivo.pdf        # Explora un PDF específico
    python explore_pdfs.py --text             # Solo texto por página
    python explore_pdfs.py --tables           # Solo tablas
    python explore_pdfs.py --structure        # Solo estructura
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdf_analyzer import ExtractorService, LocalPDFRepository


def print_separator(char="=", length=60):
    print(char * length)


def explore_text(extractor: ExtractorService, pdf_path: Path):
    """Muestra el texto por página."""
    print("\n[TEXTO POR PÁGINA]")
    print_separator("-")

    text_by_page = extractor.extract_text_by_page(pdf_path)

    for page, content in text_by_page.items():
        print(f"\n--- Página {page} ({len(content)} caracteres) ---")
        if content:
            # Mostrar primeras 500 chars
            preview = content[:500]
            print(preview)
            if len(content) > 500:
                print(f"... [{len(content) - 500} caracteres más]")
        else:
            print("(vacío)")


def explore_tables(extractor: ExtractorService, pdf_path: Path):
    """Muestra las tablas con posición."""
    print("\n[TABLAS]")
    print_separator("-")

    tables = extractor.extract_tables_with_position(pdf_path)

    if not tables:
        print("No se encontraron tablas estructuradas.")
        return

    print(f"Total: {len(tables)} tabla(s)\n")

    for i, table in enumerate(tables):
        print(f"Tabla {i + 1}: Página {table.page}, {table.rows} filas x {table.cols} columnas")
        print(f"  Posición (bbox): {table.bbox}")

        if table.data:
            print("  Contenido:")
            for row in table.data[:5]:  # Primeras 5 filas
                print(f"    {row}")
            if len(table.data) > 5:
                print(f"    ... ({len(table.data) - 5} filas más)")
        print()


def explore_structure(extractor: ExtractorService, pdf_path: Path):
    """Muestra la estructura detectada."""
    print("\n[ESTRUCTURA]")
    print_separator("-")

    sections = extractor.extract_structure(pdf_path)

    if not sections:
        print("No se detectaron secciones.")
        return

    print(f"Total: {len(sections)} sección(es)\n")

    for i, section in enumerate(sections):
        print(f"Sección {i + 1}: [{section.type.upper()}]")
        print(f"  Página: {section.page}, Líneas: {section.line_start}-{section.line_end}")

        # Preview del contenido
        preview = section.content[:200].replace("\n", " ")
        print(f"  Contenido: {preview}")
        if len(section.content) > 200:
            print(f"  ... [{len(section.content) - 200} caracteres más]")
        print()


def explore_pdf(extractor: ExtractorService, pdf_path: Path, options: dict):
    """Explora un PDF completo."""
    print_separator("=")
    print(f"ARCHIVO: {pdf_path.name}")
    print_separator("=")

    show_all = not any([options.get("text"), options.get("tables"), options.get("structure")])

    if show_all or options.get("text"):
        explore_text(extractor, pdf_path)

    if show_all or options.get("tables"):
        explore_tables(extractor, pdf_path)

    if show_all or options.get("structure"):
        explore_structure(extractor, pdf_path)


def main():
    # Parsear argumentos
    args = sys.argv[1:]
    options = {
        "text": "--text" in args,
        "tables": "--tables" in args,
        "structure": "--structure" in args,
    }

    # Filtrar flags de los argumentos
    pdf_args = [a for a in args if not a.startswith("--")]

    data_dir = Path(__file__).parent.parent / "data"
    extractor = ExtractorService()

    if pdf_args:
        # Explorar PDF específico
        for pdf_name in pdf_args:
            pdf_path = Path(pdf_name)
            if not pdf_path.is_absolute():
                pdf_path = data_dir / pdf_name

            if not pdf_path.exists():
                print(f"Error: No se encontró {pdf_path}")
                continue

            explore_pdf(extractor, pdf_path, options)
    else:
        # Explorar todos los PDFs
        repo = LocalPDFRepository(data_dir)
        docs = repo.get_all()

        if not docs:
            print("No se encontraron PDFs en data/")
            return

        print(f"Encontrados {len(docs)} PDFs\n")

        for doc in docs:
            explore_pdf(extractor, doc.path, options)
            print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario.")
        sys.exit(0)
