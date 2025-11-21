"""
Tests para el módulo services de pdf_analyzer.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pdf_analyzer.services import ReaderService, AnalyzerService, SecurityService
from pdf_analyzer.models import PDFDocument


class TestReaderService:
    """Tests para ReaderService."""

    def test_init_with_password(self, env_password):
        """Test inicialización con contraseña."""
        service = ReaderService()
        assert service._password == "test_password"

    def test_init_custom_password(self):
        """Test inicialización con contraseña personalizada."""
        service = ReaderService(password="custom_pwd")
        assert service._password == "custom_pwd"

    def test_read_text(self, sample_pdf_path, mock_pdfplumber):
        """Test lectura de texto."""
        service = ReaderService()

        text = service.read_text(sample_pdf_path)

        assert "Texto de prueba" in text

    def test_read_text_specific_page(self, sample_pdf_path, mock_pdfplumber):
        """Test lectura de página específica."""
        service = ReaderService()

        text = service.read_text(sample_pdf_path, page_number=0)

        assert text is not None

    def test_read_text_invalid_page(self, sample_pdf_path, mock_pdfplumber):
        """Test lectura de página inválida."""
        service = ReaderService()

        with pytest.raises(IndexError):
            service.read_text(sample_pdf_path, page_number=999)

    def test_read_tables(self, sample_pdf_path, mock_pdfplumber):
        """Test lectura de tablas."""
        service = ReaderService()

        tables = service.read_tables(sample_pdf_path)

        assert len(tables) > 0
        assert tables[0][0] == ["col1", "col2"]

    def test_read_metadata(self, sample_pdf_path):
        """Test lectura de metadatos."""
        with patch("pdf_analyzer.services.reader_service.PdfReader") as mock_reader:
            mock_instance = MagicMock()
            mock_instance.is_encrypted = False
            mock_instance.metadata = MagicMock()
            mock_instance.metadata.author = "Test Author"
            mock_instance.metadata.creator = "Test Creator"
            mock_instance.metadata.producer = "Test Producer"
            mock_instance.metadata.subject = "Test Subject"
            mock_instance.metadata.title = "Test Title"
            mock_reader.return_value = mock_instance

            service = ReaderService()
            metadata = service.read_metadata(sample_pdf_path)

            assert metadata["author"] == "Test Author"
            assert metadata["title"] == "Test Title"

    def test_get_page_count(self, sample_pdf_path, mock_pdfplumber):
        """Test conteo de páginas."""
        service = ReaderService()

        count = service.get_page_count(sample_pdf_path)

        assert count == 1

    def test_is_encrypted(self, sample_pdf_path):
        """Test verificación de encriptación."""
        with patch("pdf_analyzer.services.reader_service.PdfReader") as mock_reader:
            mock_reader.return_value.is_encrypted = False

            service = ReaderService()
            result = service.is_encrypted(sample_pdf_path)

            assert result is False

    def test_enrich_document(self, sample_pdf_path, mock_pdfplumber):
        """Test enriquecimiento de documento."""
        with patch("pdf_analyzer.services.reader_service.PdfReader") as mock_reader:
            mock_reader.return_value.is_encrypted = False
            mock_reader.return_value.metadata = None

            service = ReaderService()
            doc = PDFDocument.from_path(sample_pdf_path)

            enriched = service.enrich_document(doc)

            assert enriched.num_pages == 1
            assert enriched.is_encrypted is False

    def test_resolve_path_with_document(self, sample_pdf_path):
        """Test resolución de path con PDFDocument."""
        doc = PDFDocument.from_path(sample_pdf_path)

        path = ReaderService._resolve_path(doc)

        assert path == sample_pdf_path

    def test_resolve_path_with_string(self):
        """Test resolución de path con string."""
        path = ReaderService._resolve_path("/some/path.pdf")

        assert isinstance(path, Path)


class TestAnalyzerService:
    """Tests para AnalyzerService."""

    def test_analyze(self, sample_pdf_path, mock_pdfplumber):
        """Test análisis completo."""
        with patch("pdf_analyzer.services.reader_service.PdfReader") as mock_reader:
            mock_reader.return_value.is_encrypted = False
            mock_reader.return_value.metadata = None

            service = AnalyzerService()
            result = service.analyze(sample_pdf_path)

            assert "filename" in result
            assert "num_pages" in result
            assert "text_length" in result
            assert "word_count" in result
            assert "num_tables" in result

    def test_analyze_caching(self, sample_pdf_path, mock_pdfplumber):
        """Test que análisis usa caché."""
        with patch("pdf_analyzer.services.reader_service.PdfReader") as mock_reader:
            mock_reader.return_value.is_encrypted = False
            mock_reader.return_value.metadata = None

            service = AnalyzerService()

            result1 = service.analyze(sample_pdf_path)
            result2 = service.analyze(sample_pdf_path)

            assert result1 == result2
            # El cache debe devolver el mismo resultado

    def test_get_text(self, sample_pdf_path, mock_pdfplumber):
        """Test obtener texto."""
        service = AnalyzerService()

        text = service.get_text(sample_pdf_path)

        assert "Texto de prueba" in text

    def test_get_tables(self, sample_pdf_path, mock_pdfplumber):
        """Test obtener tablas."""
        service = AnalyzerService()

        tables = service.get_tables(sample_pdf_path)

        assert len(tables) > 0

    def test_search_found(self, sample_pdf_path, mock_pdfplumber):
        """Test búsqueda con resultados."""
        service = AnalyzerService()

        results = service.search(sample_pdf_path, "prueba")

        assert len(results) > 0
        assert any("prueba" in r.lower() for r in results)

    def test_search_not_found(self, sample_pdf_path, mock_pdfplumber):
        """Test búsqueda sin resultados."""
        service = AnalyzerService()

        results = service.search(sample_pdf_path, "xyznotexist")

        assert len(results) == 0

    def test_search_case_sensitive(self, sample_pdf_path, mock_pdfplumber):
        """Test búsqueda case sensitive."""
        service = AnalyzerService()

        results_insensitive = service.search(sample_pdf_path, "TEXTO", case_sensitive=False)
        results_sensitive = service.search(sample_pdf_path, "TEXTO", case_sensitive=True)

        assert len(results_insensitive) >= len(results_sensitive)

    def test_search_all(self, sample_pdf_files, mock_pdfplumber):
        """Test búsqueda en múltiples documentos."""
        service = AnalyzerService()

        results = service.search_all(sample_pdf_files[:2], "prueba")

        assert isinstance(results, dict)

    def test_compare(self, sample_pdf_files, mock_pdfplumber):
        """Test comparación de documentos."""
        with patch("pdf_analyzer.services.reader_service.PdfReader") as mock_reader:
            mock_reader.return_value.is_encrypted = False
            mock_reader.return_value.metadata = None

            service = AnalyzerService()
            comparison = service.compare(sample_pdf_files[0], sample_pdf_files[1])

            assert "doc1" in comparison
            assert "doc2" in comparison
            assert "comparison" in comparison
            assert "pages" in comparison["comparison"]

    def test_clear_cache(self, sample_pdf_path, mock_pdfplumber):
        """Test limpiar caché."""
        with patch("pdf_analyzer.services.reader_service.PdfReader") as mock_reader:
            mock_reader.return_value.is_encrypted = False
            mock_reader.return_value.metadata = None

            service = AnalyzerService()
            service.analyze(sample_pdf_path)

            service.clear_cache()

            assert len(service._cache) == 0


class TestSecurityService:
    """Tests para SecurityService."""

    def test_init_with_env_password(self, env_password):
        """Test inicialización con password del entorno."""
        service = SecurityService()
        assert service._password == "test_password"

    def test_is_encrypted_false(self, sample_pdf_path):
        """Test verificación de no encriptado."""
        with patch("pdf_analyzer.services.security_service.PdfReader") as mock_reader:
            mock_reader.return_value.is_encrypted = False

            service = SecurityService()
            result = service.is_encrypted(sample_pdf_path)

            assert result is False

    def test_is_encrypted_true(self, sample_pdf_path):
        """Test verificación de encriptado."""
        with patch("pdf_analyzer.services.security_service.PdfReader") as mock_reader:
            mock_reader.return_value.is_encrypted = True

            service = SecurityService()
            result = service.is_encrypted(sample_pdf_path)

            assert result is True

    def test_remove_password_not_encrypted(self, sample_pdf_path):
        """Test quitar contraseña de archivo no encriptado."""
        with patch("pdf_analyzer.services.security_service.PdfReader") as mock_reader:
            mock_reader.return_value.is_encrypted = False

            service = SecurityService()

            with pytest.raises(ValueError, match="no está encriptado"):
                service.remove_password(sample_pdf_path)

    def test_remove_password_wrong_password(self, sample_pdf_path):
        """Test quitar contraseña con contraseña incorrecta."""
        with patch("pdf_analyzer.services.security_service.PdfReader") as mock_reader:
            mock_reader.return_value.is_encrypted = True
            mock_reader.return_value.decrypt.return_value = False

            service = SecurityService()

            with pytest.raises(ValueError, match="incorrecta"):
                service.remove_password(sample_pdf_path)

    def test_remove_password_success(self, sample_pdf_path, temp_dir):
        """Test quitar contraseña exitosamente."""
        with patch("pdf_analyzer.services.security_service.PdfReader") as mock_reader:
            mock_instance = MagicMock()
            mock_instance.is_encrypted = True
            mock_instance.decrypt.return_value = True
            mock_instance.pages = [MagicMock()]
            mock_instance.metadata = None
            mock_reader.return_value = mock_instance

            with patch("pdf_analyzer.services.security_service.PdfWriter") as mock_writer:
                mock_writer_instance = MagicMock()
                mock_writer.return_value = mock_writer_instance

                service = SecurityService()
                output = temp_dir / "unlocked.pdf"

                result = service.remove_password(sample_pdf_path, output)

                assert result == output

    def test_add_password_no_password(self):
        """Test agregar contraseña sin proporcionar contraseña."""
        with patch.dict("os.environ", {}, clear=True):
            service = SecurityService(password=None)
            service._password = None  # Forzar None

            with pytest.raises(ValueError, match="Se requiere"):
                service.add_password(Path("/fake.pdf"))

    def test_add_password_success(self, sample_pdf_path, temp_dir):
        """Test agregar contraseña exitosamente."""
        with patch("pdf_analyzer.services.security_service.PdfReader") as mock_reader:
            mock_reader.return_value.is_encrypted = False
            mock_reader.return_value.pages = [MagicMock()]
            mock_reader.return_value.metadata = None

            with patch("pdf_analyzer.services.security_service.PdfWriter") as mock_writer:
                mock_writer_instance = MagicMock()
                mock_writer.return_value = mock_writer_instance

                service = SecurityService()
                output = temp_dir / "locked.pdf"

                result = service.add_password(
                    sample_pdf_path,
                    output,
                    user_password="test123"
                )

                assert result == output
                mock_writer_instance.encrypt.assert_called_once()

    def test_change_password(self, sample_pdf_path, temp_dir):
        """Test cambiar contraseña."""
        with patch("pdf_analyzer.services.security_service.PdfReader") as mock_reader:
            mock_instance = MagicMock()
            mock_instance.is_encrypted = False
            mock_instance.pages = [MagicMock()]
            mock_instance.metadata = None
            mock_reader.return_value = mock_instance

            with patch("pdf_analyzer.services.security_service.PdfWriter") as mock_writer:
                mock_writer_instance = MagicMock()
                mock_writer.return_value = mock_writer_instance

                service = SecurityService()
                output = temp_dir / "newpwd.pdf"

                result = service.change_password(
                    sample_pdf_path,
                    new_password="new_password",
                    output_path=output
                )

                assert result == output

    def test_batch_remove_password(self, sample_pdf_files, temp_dir):
        """Test quitar contraseña en batch."""
        with patch.object(SecurityService, "remove_password") as mock_remove:
            mock_remove.return_value = Path("/output/file.pdf")

            service = SecurityService()
            results = service.batch_remove_password(
                sample_pdf_files[:2],
                temp_dir
            )

            assert len(results) == 2
            assert all("success" in r for r in results)

    def test_batch_remove_password_with_errors(self, sample_pdf_files, temp_dir):
        """Test batch con errores."""
        with patch.object(SecurityService, "remove_password") as mock_remove:
            mock_remove.side_effect = ValueError("Error de prueba")

            service = SecurityService()
            results = service.batch_remove_password(sample_pdf_files[:2], temp_dir)

            assert all(r["success"] is False for r in results)
            assert all("error" in r for r in results)
