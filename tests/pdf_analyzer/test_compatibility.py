"""
Tests para funciones de compatibilidad hacia atrás.

Verifica que los aliases y funciones legacy sigan funcionando.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from pdf_analyzer import (
    # Aliases de clases
    PDFReader,
    PDFAnalyzer,
    PDFSecurity,
    # Funciones de compatibilidad
    list_pdfs,
    extract_text,
    is_encrypted,
    remove_password,
    add_password,
    remove_password_batch,
    add_password_batch,
    # Nuevas clases (para verificar que aliases apuntan correctamente)
    ReaderService,
    AnalyzerService,
    SecurityService,
)


class TestClassAliases:
    """Tests para aliases de clases."""

    def test_pdfreader_is_readerservice(self):
        """Test que PDFReader es alias de ReaderService."""
        assert PDFReader is ReaderService

    def test_pdfanalyzer_is_analyzerservice(self):
        """Test que PDFAnalyzer es alias de AnalyzerService."""
        assert PDFAnalyzer is AnalyzerService

    def test_pdfsecurity_is_securityservice(self):
        """Test que PDFSecurity es alias de SecurityService."""
        assert PDFSecurity is SecurityService


class TestListPdfs:
    """Tests para función list_pdfs."""

    def test_list_pdfs_returns_sorted_paths(self, temp_dir, sample_pdf_files):
        """Test que list_pdfs retorna paths ordenados."""
        result = list_pdfs(temp_dir)

        assert len(result) == 5
        assert all(isinstance(p, Path) for p in result)
        assert result == sorted(result)

    def test_list_pdfs_empty_dir(self, temp_dir):
        """Test list_pdfs en directorio vacío."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()

        result = list_pdfs(empty_dir)

        assert result == []


class TestExtractText:
    """Tests para función extract_text."""

    def test_extract_text(self, sample_pdf_path, mock_pdfplumber):
        """Test extracción de texto."""
        result = extract_text(sample_pdf_path)

        assert "Texto de prueba" in result

    def test_extract_text_with_password(self, sample_pdf_path, mock_pdfplumber):
        """Test extracción con contraseña."""
        result = extract_text(sample_pdf_path, password="test123")

        assert result is not None


class TestIsEncrypted:
    """Tests para función is_encrypted."""

    def test_is_encrypted_false(self, sample_pdf_path):
        """Test archivo no encriptado."""
        with patch("pdf_analyzer.services.security_service.PdfReader") as mock:
            mock.return_value.is_encrypted = False

            result = is_encrypted(sample_pdf_path)

            assert result is False

    def test_is_encrypted_true(self, sample_pdf_path):
        """Test archivo encriptado."""
        with patch("pdf_analyzer.services.security_service.PdfReader") as mock:
            mock.return_value.is_encrypted = True

            result = is_encrypted(sample_pdf_path)

            assert result is True


class TestRemovePassword:
    """Tests para función remove_password."""

    def test_remove_password_not_encrypted(self, sample_pdf_path, mock_pypdf_reader):
        """Test quitar contraseña de archivo no encriptado."""
        with pytest.raises(ValueError):
            remove_password(sample_pdf_path)

    def test_remove_password_success(self, sample_pdf_path, temp_dir):
        """Test quitar contraseña exitosamente."""
        with patch("pdf_analyzer.services.security_service.PdfReader") as mock_reader:
            mock_instance = MagicMock()
            mock_instance.is_encrypted = True
            mock_instance.decrypt.return_value = True
            mock_instance.pages = [MagicMock()]
            mock_instance.metadata = None
            mock_reader.return_value = mock_instance

            with patch("pdf_analyzer.services.security_service.PdfWriter"):
                output = temp_dir / "unlocked.pdf"
                result = remove_password(sample_pdf_path, output, password="test")

                assert result == output


class TestAddPassword:
    """Tests para función add_password."""

    def test_add_password(self, sample_pdf_path, temp_dir, mock_pypdf_reader):
        """Test agregar contraseña."""
        with patch("pdf_analyzer.services.security_service.PdfWriter"):
            output = temp_dir / "locked.pdf"

            result = add_password(
                sample_pdf_path,
                output,
                user_password="test123"
            )

            assert result == output


class TestBatchFunctions:
    """Tests para funciones batch."""

    def test_remove_password_batch(self, temp_dir, sample_pdf_files):
        """Test quitar contraseña en batch."""
        with patch("pdf_analyzer.SecurityService.batch_remove_password") as mock:
            mock.return_value = [{"success": True}]

            result = remove_password_batch(temp_dir)

            assert isinstance(result, list)

    def test_add_password_batch(self, temp_dir, sample_pdf_files):
        """Test agregar contraseña en batch."""
        with patch("pdf_analyzer.SecurityService.add_password") as mock:
            mock.return_value = Path("/output/file.pdf")
            output_dir = temp_dir / "locked"
            output_dir.mkdir()

            result = add_password_batch(
                temp_dir,
                output_dir,
                user_password="test123"
            )

            assert isinstance(result, list)
            assert len(result) == 5


class TestImportPaths:
    """Tests para verificar que imports funcionan."""

    def test_import_from_root(self):
        """Test imports desde raíz del paquete."""
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

        assert PDFDocument is not None
        assert LocalPDFRepository is not None

    def test_import_from_submodules(self):
        """Test imports desde submódulos."""
        from pdf_analyzer.models import PDFDocument
        from pdf_analyzer.repositories import LocalPDFRepository
        from pdf_analyzer.services import ReaderService
        from pdf_analyzer.file_manager import FileOperations

        assert PDFDocument is not None
        assert LocalPDFRepository is not None
        assert ReaderService is not None
        assert FileOperations is not None
