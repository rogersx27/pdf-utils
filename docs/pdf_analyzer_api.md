# PDF Analyzer API

## Instalación

```python
from pdf_analyzer import (
    PDFDocument,
    LocalPDFRepository,
    ReaderService,
    AnalyzerService,
    SecurityService,
    FileOperations,
    PDFOrganizer,
    PDFRegistry,
)
```

## Modelos

### PDFDocument

```python
doc = PDFDocument.from_path("archivo.pdf")

doc.path          # Path del archivo
doc.info.tipo     # Tipo de documento (CTA_AHORROS, TARJETA_MASTERCARD, etc.)
doc.info.fecha    # Fecha del documento
doc.info.numero   # Número de cuenta/tarjeta
doc.info.year     # Año extraído
doc.info.month    # Mes extraído
doc.num_pages     # Número de páginas
doc.is_encrypted  # Si está encriptado
doc.to_dict()     # Convertir a diccionario
```

## Repositorio

### LocalPDFRepository

```python
repo = LocalPDFRepository("./data")

repo.get_all()                    # Lista todos los documentos
repo.get("archivo")               # Obtiene documento por nombre
repo.exists("archivo")            # Verifica si existe
repo.count()                      # Cantidad de documentos
repo.find(tipo="CTA_AHORROS")     # Filtra por tipo
repo.find(year=2024)              # Filtra por año
repo.find(predicate=lambda d: d.info.numero == "123")  # Filtro custom
repo.add(source_path)             # Agrega documento
repo.remove("archivo")            # Elimina documento
repo.get_types()                  # Lista tipos disponibles
repo.get_years()                  # Lista años disponibles
repo.summary()                    # Resumen del repositorio
```

## Servicios

### ReaderService

```python
reader = ReaderService(password="opcional")

reader.read_text(path)                    # Extrae texto completo
reader.read_text(path, page_number=0)     # Texto de página específica
reader.read_tables(path)                  # Extrae tablas
reader.read_metadata(path)                # Obtiene metadatos
reader.get_page_count(path)               # Número de páginas
reader.is_encrypted(path)                 # Verifica encriptación
reader.enrich_document(doc)               # Enriquece PDFDocument con metadata
```

### AnalyzerService

```python
analyzer = AnalyzerService(password="opcional")

analyzer.analyze(path)                    # Análisis completo (con caché)
analyzer.get_text(path)                   # Obtiene texto
analyzer.get_tables(path)                 # Obtiene tablas
analyzer.search(path, "término")          # Busca en documento
analyzer.search(path, "término", case_sensitive=False)
analyzer.search_all([paths], "término")   # Busca en múltiples documentos
analyzer.compare(path1, path2)            # Compara dos documentos
analyzer.clear_cache()                    # Limpia caché
```

**Resultado de `analyze()`:**
```python
{
    "filename": str,
    "num_pages": int,
    "text_length": int,
    "word_count": int,
    "num_tables": int,
    "is_encrypted": bool,
    "metadata": dict
}
```

### SecurityService

```python
security = SecurityService(password="opcional")

security.is_encrypted(path)               # Verifica encriptación
security.remove_password(path, output)    # Quita contraseña
security.add_password(path, output, user_password="pwd")
security.add_password(path, output, user_password="usr", owner_password="own")
security.change_password(path, new_password="new", output_path=output)
security.batch_remove_password([paths], output_dir)  # Batch
```

## File Manager

### FileOperations

```python
from pdf_analyzer.file_manager import (
    copy_pdf, move_pdf, rename_pdf, delete_pdf,
    create_folder, delete_folder, get_file_info
)

# Funciones directas
copy_pdf(source, dest)
copy_pdf(source, dest, overwrite=True)
move_pdf(source, dest)
rename_pdf(path, "nuevo_nombre.pdf")
delete_pdf(path)
create_folder(path)
delete_folder(path)
delete_folder(path, force=True)
get_file_info(path)  # dict con name, size, size_human, suffix, etc.

# Clase con directorio base
ops = FileOperations("./data")
ops.copy("archivo.pdf", "copia.pdf")
ops.move("archivo.pdf", "subdir/archivo.pdf")
ops.rename("archivo.pdf", "nuevo.pdf")
ops.delete("archivo.pdf")
ops.list_files("*.pdf")
ops.list_folders()
ops.get_info("archivo.pdf")
```

### PDFOrganizer

```python
organizer = PDFOrganizer(repo)

organizer.organize_by_type()              # Organiza por tipo de documento
organizer.organize_by_year()              # Organiza por año
organizer.organize_by_month()             # Organiza por año/mes
organizer.organize_by_type(dry_run=True)  # Preview sin mover
organizer.organize_by_custom(key_func=lambda doc: doc.info.numero)
organizer.flatten()                       # Aplana estructura a raíz
organizer.preview_organization(by="type") # by: "type", "year", "month"
```

### PDFRegistry

```python
registry = PDFRegistry(repo)

registry.scan()                           # Escanea y retorna documentos
registry.summary()                        # Resumen general
registry.to_json("inventory.json")        # Exporta a JSON
registry.to_csv("inventory.csv")          # Exporta a CSV
registry.to_csv("inventory.csv", include_metadata=True)
registry.to_markdown("inventory.md")      # Exporta a Markdown
registry.find_duplicates()                # Busca duplicados por tamaño
registry.get_statistics()                 # Estadísticas detalladas
```

## Configuración

### Variables de Entorno

```bash
PDF_PASSWORD=tu_contraseña    # Contraseña por defecto para PDFs
```

### Uso con .env

```python
from dotenv import load_dotenv
load_dotenv()

# Los servicios tomarán PDF_PASSWORD automáticamente
reader = ReaderService()
```

## Funciones de Conveniencia (utils)

Funciones para uso rápido sin instanciar servicios:

```python
from pdf_analyzer import (
    list_pdfs,
    extract_text,
    extract_tables,
    get_metadata,
    get_page_count,
    is_encrypted,
    remove_password,
    add_password,
    remove_password_batch,
    add_password_batch,
    analyze,
    search_in_pdf,
    compare_pdfs,
)

# Listar PDFs
pdfs = list_pdfs("./data")

# Extraer contenido
text = extract_text("doc.pdf", password="opcional")
tables = extract_tables("doc.pdf")
metadata = get_metadata("doc.pdf")
pages = get_page_count("doc.pdf")

# Análisis
info = analyze("doc.pdf")  # dict con num_pages, word_count, etc.
matches = search_in_pdf("doc.pdf", "término", case_sensitive=False)
diff = compare_pdfs("doc1.pdf", "doc2.pdf")

# Seguridad
encrypted = is_encrypted("doc.pdf")
remove_password("encrypted.pdf", "output.pdf", password="pwd")
add_password("doc.pdf", "locked.pdf", user_password="pwd")

# Operaciones batch
remove_password_batch("./encrypted", "./unlocked", password="pwd")
add_password_batch("./docs", "./protected", user_password="pwd")
```

## Utilidades Generales

```python
from pdf_analyzer import (
    get_data_path,
    get_project_root,
    ensure_directory,
    parse_filename,
)

data = get_data_path()           # Path a ./data
root = get_project_root()        # Path raíz del proyecto
ensure_directory("./output")     # Crea directorio si no existe
info = parse_filename("Extracto_123_202401_CTA_AHORROS_456.pdf")
# {"id": "123", "fecha": "202401", "tipo": "CTA_AHORROS", "numero": "456"}
```

## Aliases (Compatibilidad)

```python
PDFReader = ReaderService
PDFAnalyzer = AnalyzerService
PDFSecurity = SecurityService
```
