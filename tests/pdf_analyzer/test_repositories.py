"""
Tests para el módulo repositories de pdf_analyzer.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from pdf_analyzer.repositories import BaseRepository, LocalPDFRepository
from pdf_analyzer.models import PDFDocument


class TestBaseRepository:
    """Tests para la clase abstracta BaseRepository."""

    def test_cannot_instantiate_abstract(self):
        """Test que no se puede instanciar directamente."""
        with pytest.raises(TypeError):
            BaseRepository()

    def test_subclass_must_implement_methods(self):
        """Test que subclase debe implementar métodos abstractos."""

        class IncompleteRepo(BaseRepository):
            pass

        with pytest.raises(TypeError):
            IncompleteRepo()


class TestLocalPDFRepository:
    """Tests para LocalPDFRepository."""

    def test_init_creates_directory(self, temp_dir):
        """Test que el constructor crea el directorio si no existe."""
        new_dir = temp_dir / "new_repo"
        assert not new_dir.exists()

        repo = LocalPDFRepository(new_dir)

        assert new_dir.exists()
        assert repo.base_dir == new_dir

    def test_get_all_empty(self, temp_dir):
        """Test get_all en repositorio vacío."""
        repo = LocalPDFRepository(temp_dir)

        docs = repo.get_all()

        assert docs == []
        assert repo.count() == 0

    def test_get_all_with_files(self, temp_dir, sample_pdf_files):
        """Test get_all con archivos."""
        repo = LocalPDFRepository(temp_dir)

        docs = repo.get_all()

        assert len(docs) == 5
        assert all(isinstance(d, PDFDocument) for d in docs)

    def test_get_existing(self, temp_dir, sample_pdf_path):
        """Test obtener documento existente."""
        repo = LocalPDFRepository(temp_dir)

        doc = repo.get(sample_pdf_path.name)

        assert doc is not None
        assert doc.filename == sample_pdf_path.name

    def test_get_nonexistent(self, temp_dir):
        """Test obtener documento inexistente."""
        repo = LocalPDFRepository(temp_dir)

        doc = repo.get("no_existe.pdf")

        assert doc is None

    def test_get_adds_pdf_extension(self, temp_dir, sample_pdf_path):
        """Test que get agrega extensión .pdf si falta."""
        repo = LocalPDFRepository(temp_dir)

        doc = repo.get(sample_pdf_path.stem)  # Sin .pdf

        assert doc is not None

    def test_exists_true(self, temp_dir, sample_pdf_path):
        """Test exists para archivo existente."""
        repo = LocalPDFRepository(temp_dir)

        assert repo.exists(sample_pdf_path.name) is True

    def test_exists_false(self, temp_dir):
        """Test exists para archivo inexistente."""
        repo = LocalPDFRepository(temp_dir)

        assert repo.exists("no_existe.pdf") is False

    def test_count(self, temp_dir, sample_pdf_files):
        """Test conteo de documentos."""
        repo = LocalPDFRepository(temp_dir)

        assert repo.count() == 5

    def test_find_by_tipo(self, temp_dir, sample_pdf_files):
        """Test búsqueda por tipo."""
        repo = LocalPDFRepository(temp_dir)

        docs = repo.find(tipo="CTA_AHORROS")

        assert len(docs) == 2
        assert all(d.tipo == "CTA_AHORROS" for d in docs)

    def test_find_by_year(self, temp_dir, sample_pdf_files):
        """Test búsqueda por año."""
        repo = LocalPDFRepository(temp_dir)

        docs = repo.find(year=2024)

        assert len(docs) == 2

    def test_find_by_fecha(self, temp_dir, sample_pdf_files):
        """Test búsqueda por fecha exacta."""
        repo = LocalPDFRepository(temp_dir)

        docs = repo.find(fecha="202301")

        assert len(docs) == 1

    def test_find_with_predicate(self, temp_dir, sample_pdf_files):
        """Test búsqueda con función personalizada."""
        repo = LocalPDFRepository(temp_dir)

        docs = repo.find(predicate=lambda d: "TARJETA" in d.tipo)

        assert len(docs) == 2

    def test_find_combined_filters(self, temp_dir, sample_pdf_files):
        """Test búsqueda con múltiples filtros."""
        repo = LocalPDFRepository(temp_dir)

        docs = repo.find(tipo="CTA_AHORROS", year=2023)

        assert len(docs) == 2

    def test_add_document(self, temp_dir, sample_pdf_path):
        """Test agregar documento."""
        source_dir = sample_pdf_path.parent
        target_dir = temp_dir / "target"
        target_dir.mkdir()

        repo = LocalPDFRepository(target_dir)
        doc = repo.add(sample_pdf_path)

        assert doc.filename == sample_pdf_path.name
        assert (target_dir / sample_pdf_path.name).exists()
        assert repo.count() == 1

    def test_add_document_custom_name(self, temp_dir, sample_pdf_path):
        """Test agregar documento con nombre personalizado."""
        target_dir = temp_dir / "target"
        target_dir.mkdir()

        repo = LocalPDFRepository(target_dir)
        doc = repo.add(sample_pdf_path, dest_name="nuevo_nombre.pdf")

        assert doc.filename == "nuevo_nombre.pdf"

    def test_add_nonexistent_raises(self, temp_dir):
        """Test que agregar archivo inexistente lanza error."""
        repo = LocalPDFRepository(temp_dir)

        with pytest.raises(FileNotFoundError):
            repo.add(Path("/no/existe.pdf"))

    def test_add_duplicate_raises(self, temp_dir, sample_pdf_path):
        """Test que agregar duplicado lanza error."""
        repo = LocalPDFRepository(temp_dir)

        with pytest.raises(ValueError):
            repo.add(sample_pdf_path)  # Ya existe

    def test_remove_document(self, temp_dir, sample_pdf_path):
        """Test eliminar documento."""
        repo = LocalPDFRepository(temp_dir)
        initial_count = repo.count()

        result = repo.remove(sample_pdf_path.name)

        assert result is True
        assert repo.count() == initial_count - 1
        assert not sample_pdf_path.exists()

    def test_remove_nonexistent(self, temp_dir):
        """Test eliminar documento inexistente."""
        repo = LocalPDFRepository(temp_dir)

        result = repo.remove("no_existe.pdf")

        assert result is False

    def test_refresh(self, temp_dir, sample_pdf_path):
        """Test actualizar caché."""
        repo = LocalPDFRepository(temp_dir)
        initial_count = repo.count()

        # Crear nuevo archivo externamente
        new_file = temp_dir / "nuevo.pdf"
        new_file.write_bytes(sample_pdf_path.read_bytes())

        # Antes de refresh
        assert repo.count() == initial_count

        # Después de refresh
        repo.refresh()
        assert repo.count() == initial_count + 1

    def test_get_types(self, temp_dir, sample_pdf_files):
        """Test obtener tipos únicos."""
        repo = LocalPDFRepository(temp_dir)

        types = repo.get_types()

        assert "CTA_AHORROS" in types
        assert "TARJETA_MASTERCARD" in types
        assert "COMISIONES_CONSOLIDADAS" in types

    def test_get_years(self, temp_dir, sample_pdf_files):
        """Test obtener años únicos."""
        repo = LocalPDFRepository(temp_dir)

        years = repo.get_years()

        assert 2023 in years
        assert 2024 in years

    def test_get_by_type(self, temp_dir, sample_pdf_files):
        """Test agrupar por tipo."""
        repo = LocalPDFRepository(temp_dir)

        by_type = repo.get_by_type()

        assert len(by_type["CTA_AHORROS"]) == 2
        assert len(by_type["TARJETA_MASTERCARD"]) == 2

    def test_get_by_year(self, temp_dir, sample_pdf_files):
        """Test agrupar por año."""
        repo = LocalPDFRepository(temp_dir)

        by_year = repo.get_by_year()

        assert 2023 in by_year
        assert 2024 in by_year

    def test_summary(self, temp_dir, sample_pdf_files):
        """Test resumen del repositorio."""
        repo = LocalPDFRepository(temp_dir)

        summary = repo.summary()

        assert summary["total"] == 5
        assert "by_type" in summary
        assert "by_year" in summary
        assert "types" in summary
        assert "years" in summary
        assert summary["total_size"] > 0
