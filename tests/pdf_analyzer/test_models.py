"""
Tests para el módulo models de pdf_analyzer.
"""

from pathlib import Path

import pytest

from pdf_analyzer.models import PDFDocument, PDFDocumentInfo


class TestPDFDocumentInfo:
    """Tests para la clase PDFDocumentInfo."""

    def test_from_filename_valid(self):
        """Test parseo de nombre de archivo válido."""
        info = PDFDocumentInfo.from_filename(
            "Extracto_455000853_202309_CTA_AHORROS_4332.pdf"
        )

        assert info.id == "455000853"
        assert info.fecha == "202309"
        assert info.tipo == "CTA_AHORROS"
        assert info.numero == "4332"
        assert info.raw is None

    def test_from_filename_tarjeta(self):
        """Test parseo de nombre de tarjeta."""
        info = PDFDocumentInfo.from_filename(
            "Extracto_123456789_202401_TARJETA_MASTERCARD_1234.pdf"
        )

        assert info.tipo == "TARJETA_MASTERCARD"
        assert info.fecha == "202401"

    def test_from_filename_invalid(self):
        """Test parseo de nombre inválido."""
        info = PDFDocumentInfo.from_filename("archivo_random.pdf")

        assert info.id == ""
        assert info.tipo == ""
        assert info.raw == "archivo_random"

    def test_year_property(self):
        """Test extracción de año."""
        info = PDFDocumentInfo.from_filename(
            "Extracto_123_202406_CTA_AHORROS_1234.pdf"
        )

        assert info.year == 2024

    def test_month_property(self):
        """Test extracción de mes."""
        info = PDFDocumentInfo.from_filename(
            "Extracto_123_202412_CTA_AHORROS_1234.pdf"
        )

        assert info.month == 12

    def test_year_invalid_fecha(self):
        """Test año con fecha inválida."""
        info = PDFDocumentInfo(id="1", fecha="abc", tipo="", numero="")

        assert info.year is None

    def test_month_short_fecha(self):
        """Test mes con fecha corta."""
        info = PDFDocumentInfo(id="1", fecha="2024", tipo="", numero="")

        assert info.month is None


class TestPDFDocument:
    """Tests para la clase PDFDocument."""

    def test_from_path(self, sample_pdf_path):
        """Test creación desde path."""
        doc = PDFDocument.from_path(sample_pdf_path)

        assert doc.path == sample_pdf_path
        assert doc.filename == sample_pdf_path.name
        assert doc.exists is True
        assert doc.file_size > 0

    def test_info_parsed_automatically(self, sample_pdf_path):
        """Test que info se parsea automáticamente."""
        doc = PDFDocument.from_path(sample_pdf_path)

        assert doc.tipo == "CTA_AHORROS"
        assert doc.fecha == "202401"
        assert doc.info.id == "123456789"

    def test_to_dict(self, sample_pdf_path):
        """Test conversión a diccionario."""
        doc = PDFDocument.from_path(sample_pdf_path)
        data = doc.to_dict()

        assert "path" in data
        assert "filename" in data
        assert "tipo" in data
        assert "fecha" in data
        assert data["filename"] == sample_pdf_path.name

    def test_str_representation(self, sample_pdf_path):
        """Test representación string."""
        doc = PDFDocument.from_path(sample_pdf_path)

        assert sample_pdf_path.name in str(doc)

    def test_stem_property(self, sample_pdf_path):
        """Test propiedad stem."""
        doc = PDFDocument.from_path(sample_pdf_path)

        assert doc.stem == sample_pdf_path.stem
        assert not doc.stem.endswith(".pdf")

    def test_exists_false_for_missing_file(self, temp_dir):
        """Test exists es False para archivo inexistente."""
        fake_path = temp_dir / "no_existe.pdf"
        doc = PDFDocument(path=fake_path)

        assert doc.exists is False

    def test_path_string_converted_to_path(self):
        """Test que string se convierte a Path."""
        doc = PDFDocument(path="/some/path/file.pdf")

        assert isinstance(doc.path, Path)


class TestPDFDocumentDefaults:
    """Tests para valores por defecto de PDFDocument."""

    def test_default_values(self):
        """Test valores por defecto."""
        doc = PDFDocument(path=Path("/test.pdf"))

        assert doc.num_pages == 0
        assert doc.is_encrypted is False
        assert doc.file_size == 0
        assert doc.metadata == {}
