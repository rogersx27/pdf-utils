"""
Utilidades comunes para el paquete pdf_analyzer.

Este módulo proporciona funciones de conveniencia para operaciones
comunes con PDFs sin necesidad de instanciar servicios manualmente.
"""

from pathlib import Path
from typing import Optional

from logger import setup_logger, setup_utils_logger

# Configurar logger como utilidad (solo WARNING+, sin consola)
logger = setup_utils_logger(setup_logger, __name__)


def get_project_root() -> Path:
    """
    Obtiene la ruta raíz del proyecto.

    Returns:
        Ruta al directorio raíz del proyecto.
    """
    return Path(__file__).parent.parent.parent


def get_data_path() -> Path:
    """
    Obtiene la ruta a la carpeta de datos.

    Returns:
        Ruta al directorio 'data'.
    """
    data_path = get_project_root() / "data"
    if not data_path.exists():
        logger.warning(f"Carpeta de datos no existe: {data_path}")
    return data_path


def ensure_directory(path: str | Path) -> Path:
    """
    Asegura que un directorio exista, creándolo si es necesario.

    Args:
        path: Ruta al directorio.

    Returns:
        Objeto Path del directorio.
    """
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directorio creado: {path}")
    return path


def parse_filename(filename: str) -> dict:
    """
    Parsea el nombre de archivo de un extracto bancario.

    Formato esperado: Extracto_{id}_{fecha}_{tipo}_{numero}.pdf
    Ejemplo: Extracto_455000853_202309_CTA_AHORROS_4332.pdf

    Args:
        filename: Nombre del archivo PDF.

    Returns:
        Diccionario con los componentes del nombre.
    """
    name = Path(filename).stem
    parts = name.split("_")

    if len(parts) >= 4 and parts[0] == "Extracto":
        return {
            "id": parts[1],
            "fecha": parts[2],
            "tipo": "_".join(parts[3:-1]),
            "numero": parts[-1],
        }
    logger.warning(f"Formato de nombre no reconocido: {filename}")
    return {"raw": name}


# =============================================================================
# FUNCIONES DE CONVENIENCIA
# Permiten usar las funcionalidades principales sin instanciar servicios
# =============================================================================


def list_pdfs(directory: str | Path) -> list[Path]:
    """
    Lista todos los PDFs en un directorio.

    Args:
        directory: Ruta al directorio a escanear.

    Returns:
        Lista de paths a archivos PDF ordenados alfabéticamente.

    Example:
        >>> pdfs = list_pdfs("./data")
        >>> print(len(pdfs))
    """
    return sorted(Path(directory).glob("*.pdf"))


def extract_text(pdf_path: str | Path, password: Optional[str] = None) -> str:
    """
    Extrae todo el texto de un PDF.

    Args:
        pdf_path: Ruta al archivo PDF.
        password: Contraseña si el PDF está protegido.

    Returns:
        Texto extraído del documento.

    Example:
        >>> text = extract_text("documento.pdf")
        >>> print(text[:100])
    """
    from .services import ReaderService

    reader = ReaderService(password)
    return reader.read_text(pdf_path)


def extract_tables(pdf_path: str | Path, password: Optional[str] = None) -> list:
    """
    Extrae todas las tablas de un PDF.

    Args:
        pdf_path: Ruta al archivo PDF.
        password: Contraseña si el PDF está protegido.

    Returns:
        Lista de tablas, cada tabla es una lista de filas.

    Example:
        >>> tables = extract_tables("documento.pdf")
        >>> for table in tables:
        ...     print(table)
    """
    from .services import ReaderService

    reader = ReaderService(password)
    return reader.read_tables(pdf_path)


def get_metadata(pdf_path: str | Path, password: Optional[str] = None) -> dict:
    """
    Obtiene los metadatos de un PDF.

    Args:
        pdf_path: Ruta al archivo PDF.
        password: Contraseña si el PDF está protegido.

    Returns:
        Diccionario con metadatos (author, title, creator, etc.).

    Example:
        >>> meta = get_metadata("documento.pdf")
        >>> print(meta["author"])
    """
    from .services import ReaderService

    reader = ReaderService(password)
    return reader.read_metadata(pdf_path)


def get_page_count(pdf_path: str | Path, password: Optional[str] = None) -> int:
    """
    Obtiene el número de páginas de un PDF.

    Args:
        pdf_path: Ruta al archivo PDF.
        password: Contraseña si el PDF está protegido.

    Returns:
        Número de páginas.

    Example:
        >>> pages = get_page_count("documento.pdf")
        >>> print(f"El documento tiene {pages} páginas")
    """
    from .services import ReaderService

    reader = ReaderService(password)
    return reader.get_page_count(pdf_path)


def is_encrypted(pdf_path: str | Path) -> bool:
    """
    Verifica si un PDF está encriptado.

    Args:
        pdf_path: Ruta al archivo PDF.

    Returns:
        True si el PDF está encriptado.

    Example:
        >>> if is_encrypted("documento.pdf"):
        ...     print("El documento está protegido")
    """
    from .services import SecurityService

    security = SecurityService()
    return security.is_encrypted(pdf_path)


def remove_password(
    pdf_path: str | Path,
    output_path: Optional[str | Path] = None,
    password: Optional[str] = None,
) -> Path:
    """
    Quita la contraseña de un PDF protegido.

    Args:
        pdf_path: Ruta al PDF encriptado.
        output_path: Ruta de salida (opcional, genera nombre automático).
        password: Contraseña del PDF (usa PDF_PASSWORD si no se proporciona).

    Returns:
        Path al archivo sin contraseña.

    Example:
        >>> unlocked = remove_password("protegido.pdf", password="1234")
        >>> print(f"Archivo desbloqueado: {unlocked}")
    """
    from .services import SecurityService

    security = SecurityService(password)
    return security.remove_password(pdf_path, output_path)


def add_password(
    pdf_path: str | Path,
    output_path: Optional[str | Path] = None,
    user_password: Optional[str] = None,
    owner_password: Optional[str] = None,
) -> Path:
    """
    Agrega contraseña a un PDF.

    Args:
        pdf_path: Ruta al PDF sin protección.
        output_path: Ruta de salida (opcional).
        user_password: Contraseña para abrir el documento.
        owner_password: Contraseña de propietario (permisos).

    Returns:
        Path al archivo protegido.

    Example:
        >>> locked = add_password("documento.pdf", user_password="secreto")
        >>> print(f"Archivo protegido: {locked}")
    """
    from .services import SecurityService

    security = SecurityService()
    return security.add_password(pdf_path, output_path, user_password, owner_password)


def remove_password_batch(
    input_dir: str | Path,
    output_dir: Optional[str | Path] = None,
    password: Optional[str] = None,
) -> list[dict]:
    """
    Quita contraseña de múltiples PDFs en un directorio.

    Args:
        input_dir: Directorio con PDFs encriptados.
        output_dir: Directorio de salida (opcional).
        password: Contraseña de los PDFs.

    Returns:
        Lista de resultados con success, input, output/error por archivo.

    Example:
        >>> results = remove_password_batch("./encrypted", "./unlocked")
        >>> for r in results:
        ...     if r["success"]:
        ...         print(f"OK: {r['input']}")
    """
    from .services import SecurityService

    docs = list(Path(input_dir).glob("*.pdf"))
    security = SecurityService(password)
    return security.batch_remove_password(docs, output_dir)


def add_password_batch(
    input_dir: str | Path,
    output_dir: str | Path,
    user_password: str,
    owner_password: Optional[str] = None,
) -> list[dict]:
    """
    Agrega contraseña a múltiples PDFs en un directorio.

    Args:
        input_dir: Directorio con PDFs sin protección.
        output_dir: Directorio de salida.
        user_password: Contraseña para abrir los documentos.
        owner_password: Contraseña de propietario (opcional).

    Returns:
        Lista de resultados con success, input, output/error por archivo.

    Example:
        >>> results = add_password_batch("./docs", "./protected", "secreto")
        >>> success = sum(1 for r in results if r["success"])
        >>> print(f"Protegidos: {success}/{len(results)}")
    """
    from .services import SecurityService

    results = []
    docs = list(Path(input_dir).glob("*.pdf"))
    security = SecurityService()
    output_path = Path(output_dir)

    for doc in docs:
        try:
            out = output_path / doc.name
            result = security.add_password(doc, out, user_password, owner_password)
            results.append({"input": doc.name, "success": True, "output": str(result)})
        except Exception as e:
            results.append({"input": doc.name, "success": False, "error": str(e)})

    return results


def analyze(pdf_path: str | Path, password: Optional[str] = None) -> dict:
    """
    Realiza un análisis completo de un PDF.

    Args:
        pdf_path: Ruta al archivo PDF.
        password: Contraseña si el PDF está protegido.

    Returns:
        Diccionario con filename, num_pages, text_length, word_count,
        num_tables, is_encrypted, metadata.

    Example:
        >>> info = analyze("documento.pdf")
        >>> print(f"Páginas: {info['num_pages']}, Palabras: {info['word_count']}")
    """
    from .services import AnalyzerService

    analyzer = AnalyzerService(password)
    return analyzer.analyze(pdf_path)


def search_in_pdf(
    pdf_path: str | Path,
    term: str,
    password: Optional[str] = None,
    case_sensitive: bool = False,
) -> list[str]:
    """
    Busca un término en un PDF.

    Args:
        pdf_path: Ruta al archivo PDF.
        term: Término a buscar.
        password: Contraseña si el PDF está protegido.
        case_sensitive: Si la búsqueda distingue mayúsculas/minúsculas.

    Returns:
        Lista de líneas que contienen el término.

    Example:
        >>> matches = search_in_pdf("extracto.pdf", "saldo")
        >>> for line in matches:
        ...     print(line)
    """
    from .services import AnalyzerService

    analyzer = AnalyzerService(password)
    return analyzer.search(pdf_path, term, case_sensitive)


def compare_pdfs(
    pdf1: str | Path,
    pdf2: str | Path,
    password: Optional[str] = None,
) -> dict:
    """
    Compara dos documentos PDF.

    Args:
        pdf1: Ruta al primer PDF.
        pdf2: Ruta al segundo PDF.
        password: Contraseña si los PDFs están protegidos.

    Returns:
        Diccionario con información de ambos documentos y comparación.

    Example:
        >>> diff = compare_pdfs("doc1.pdf", "doc2.pdf")
        >>> print(f"Diferencia de páginas: {diff['comparison']['pages']}")
    """
    from .services import AnalyzerService

    analyzer = AnalyzerService(password)
    return analyzer.compare(pdf1, pdf2)
