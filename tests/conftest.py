"""
Configuración y fixtures compartidos para los tests.
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def temp_dir():
    """Crea un directorio temporal para tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def sample_pdf_path(temp_dir):
    """Crea un archivo PDF de prueba (mock)."""
    pdf_path = temp_dir / "Extracto_123456789_202401_CTA_AHORROS_1234.pdf"
    # Crear un archivo PDF mínimo válido
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n199\n%%EOF"
    pdf_path.write_bytes(pdf_content)
    return pdf_path


@pytest.fixture
def sample_pdf_files(temp_dir):
    """Crea múltiples archivos PDF de prueba."""
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n199\n%%EOF"

    files = [
        "Extracto_111111111_202301_CTA_AHORROS_1111.pdf",
        "Extracto_222222222_202306_CTA_AHORROS_2222.pdf",
        "Extracto_333333333_202312_TARJETA_MASTERCARD_3333.pdf",
        "Extracto_444444444_202401_TARJETA_MASTERCARD_4444.pdf",
        "Extracto_555555555_202406_COMISIONES_CONSOLIDADAS_5555.pdf",
    ]

    paths = []
    for filename in files:
        pdf_path = temp_dir / filename
        pdf_path.write_bytes(pdf_content)
        paths.append(pdf_path)

    return paths


@pytest.fixture
def mock_pdfplumber():
    """Mock para pdfplumber."""
    with patch("pdfplumber.open") as mock_open:
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Texto de prueba del PDF\nLínea 2\nLínea 3"
        mock_page.extract_tables.return_value = [[["col1", "col2"], ["val1", "val2"]]]
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_pdf
        yield mock_open


@pytest.fixture
def mock_pypdf_reader():
    """Mock para PdfReader de pypdf."""
    with patch("pypdf.PdfReader") as mock_reader_class:
        mock_reader = MagicMock()
        mock_reader.is_encrypted = False
        mock_reader.metadata = MagicMock()
        mock_reader.metadata.author = "Test Author"
        mock_reader.metadata.creator = "Test Creator"
        mock_reader.metadata.producer = "Test Producer"
        mock_reader.metadata.subject = "Test Subject"
        mock_reader.metadata.title = "Test Title"
        mock_reader.pages = [MagicMock()]
        mock_reader_class.return_value = mock_reader
        yield mock_reader_class


@pytest.fixture
def env_password():
    """Configura la variable de entorno PDF_PASSWORD para tests."""
    original = os.environ.get("PDF_PASSWORD")
    os.environ["PDF_PASSWORD"] = "test_password"
    yield "test_password"
    if original:
        os.environ["PDF_PASSWORD"] = original
    else:
        os.environ.pop("PDF_PASSWORD", None)
