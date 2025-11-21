"""
Script principal para demostrar el uso del paquete pdf_analyzer.
"""

from pdf_analyzer import PDFAnalyzer, list_pdfs, get_data_path
from pdf_analyzer.utils import parse_filename


def main():
    """Función principal de demostración."""
    data_path = get_data_path()
    print(f"Directorio de datos: {data_path}")
    print("-" * 50)

    # Listar todos los PDFs disponibles
    pdfs = list_pdfs(data_path)
    print(f"PDFs encontrados: {len(pdfs)}\n")

    for pdf_path in pdfs:
        # Parsear información del nombre
        info = parse_filename(pdf_path.name)
        print(f"Archivo: {pdf_path.name}")
        print(f"  - Tipo: {info.get('tipo', 'N/A')}")
        print(f"  - Fecha: {info.get('fecha', 'N/A')}")
        print()

    # Ejemplo de análisis de un PDF específico
    if pdfs:
        print("-" * 50)
        print("Ejemplo de análisis del primer PDF:\n")

        analyzer = PDFAnalyzer(pdfs[0])
        summary = analyzer.get_summary()

        print(f"Archivo: {summary['filename']}")
        print(f"Páginas: {summary['num_pages']}")
        print(f"Tablas encontradas: {summary['num_tables']}")
        print(f"Caracteres de texto: {summary['text_length']}")


if __name__ == "__main__":
    main()
