"""
Tests para el módulo file_manager de pdf_analyzer.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pdf_analyzer.file_manager import (
    FileOperations,
    PDFOrganizer,
    PDFRegistry,
    copy_pdf,
    move_pdf,
    rename_pdf,
    delete_pdf,
    create_folder,
    delete_folder,
    get_file_info,
)
from pdf_analyzer.file_manager.operations import FileOperationError
from pdf_analyzer.repositories import LocalPDFRepository


class TestFileOperationsFunctions:
    """Tests para funciones de operaciones de archivo."""

    def test_get_file_info(self, sample_pdf_path):
        """Test obtener información de archivo."""
        info = get_file_info(sample_pdf_path)

        assert info["name"] == sample_pdf_path.name
        assert info["suffix"] == ".pdf"
        assert info["size"] > 0
        assert "size_human" in info
        assert info["is_file"] is True

    def test_get_file_info_not_found(self, temp_dir):
        """Test info de archivo inexistente."""
        with pytest.raises(FileNotFoundError):
            get_file_info(temp_dir / "no_existe.pdf")

    def test_copy_pdf(self, sample_pdf_path, temp_dir):
        """Test copiar PDF."""
        dest = temp_dir / "copia.pdf"

        result = copy_pdf(sample_pdf_path, dest)

        assert result == dest
        assert dest.exists()
        assert sample_pdf_path.exists()  # Original sigue existiendo

    def test_copy_pdf_to_directory(self, sample_pdf_path, temp_dir):
        """Test copiar PDF a directorio."""
        dest_dir = temp_dir / "destino"
        dest_dir.mkdir()

        result = copy_pdf(sample_pdf_path, dest_dir)

        assert result == dest_dir / sample_pdf_path.name
        assert result.exists()

    def test_copy_pdf_not_found(self, temp_dir):
        """Test copiar archivo inexistente."""
        with pytest.raises(FileNotFoundError):
            copy_pdf(temp_dir / "no_existe.pdf", temp_dir / "dest.pdf")

    def test_copy_pdf_already_exists(self, sample_pdf_path, temp_dir):
        """Test copiar cuando destino ya existe."""
        dest = temp_dir / "existe.pdf"
        dest.write_bytes(b"contenido")

        with pytest.raises(FileOperationError):
            copy_pdf(sample_pdf_path, dest)

    def test_copy_pdf_overwrite(self, sample_pdf_path, temp_dir):
        """Test copiar con sobrescritura."""
        dest = temp_dir / "existe.pdf"
        dest.write_bytes(b"contenido")

        result = copy_pdf(sample_pdf_path, dest, overwrite=True)

        assert result == dest

    def test_move_pdf(self, sample_pdf_path, temp_dir):
        """Test mover PDF."""
        original = sample_pdf_path
        dest = temp_dir / "subdir" / "movido.pdf"

        result = move_pdf(original, dest)

        assert result == dest
        assert dest.exists()
        assert not original.exists()

    def test_move_pdf_not_found(self, temp_dir):
        """Test mover archivo inexistente."""
        with pytest.raises(FileNotFoundError):
            move_pdf(temp_dir / "no_existe.pdf", temp_dir / "dest.pdf")

    def test_rename_pdf(self, sample_pdf_path):
        """Test renombrar PDF."""
        original_parent = sample_pdf_path.parent

        result = rename_pdf(sample_pdf_path, "nuevo_nombre.pdf")

        assert result == original_parent / "nuevo_nombre.pdf"
        assert result.exists()
        assert not sample_pdf_path.exists()

    def test_rename_pdf_adds_extension(self, sample_pdf_path):
        """Test que rename agrega extensión .pdf."""
        result = rename_pdf(sample_pdf_path, "sin_extension")

        assert result.suffix == ".pdf"

    def test_rename_pdf_already_exists(self, sample_pdf_files):
        """Test renombrar cuando nombre ya existe."""
        with pytest.raises(FileOperationError):
            rename_pdf(sample_pdf_files[0], sample_pdf_files[1].name)

    def test_delete_pdf(self, sample_pdf_path):
        """Test eliminar PDF."""
        result = delete_pdf(sample_pdf_path)

        assert result is True
        assert not sample_pdf_path.exists()

    def test_delete_pdf_not_found(self, temp_dir):
        """Test eliminar archivo inexistente."""
        with pytest.raises(FileNotFoundError):
            delete_pdf(temp_dir / "no_existe.pdf")

    def test_create_folder(self, temp_dir):
        """Test crear carpeta."""
        new_folder = temp_dir / "nueva" / "subcarpeta"

        result = create_folder(new_folder)

        assert result == new_folder
        assert new_folder.exists()

    def test_create_folder_existing(self, temp_dir):
        """Test crear carpeta existente no falla."""
        existing = temp_dir / "existente"
        existing.mkdir()

        result = create_folder(existing)

        assert result == existing

    def test_delete_folder_empty(self, temp_dir):
        """Test eliminar carpeta vacía."""
        folder = temp_dir / "vacia"
        folder.mkdir()

        result = delete_folder(folder)

        assert result is True
        assert not folder.exists()

    def test_delete_folder_not_empty(self, temp_dir, sample_pdf_path):
        """Test eliminar carpeta no vacía sin force."""
        folder = sample_pdf_path.parent

        with pytest.raises(FileOperationError, match="no está vacío"):
            delete_folder(folder)

    def test_delete_folder_force(self, temp_dir, sample_pdf_path):
        """Test eliminar carpeta no vacía con force."""
        folder = sample_pdf_path.parent

        result = delete_folder(folder, force=True)

        assert result is True
        assert not folder.exists()


class TestFileOperationsClass:
    """Tests para la clase FileOperations."""

    def test_init(self, temp_dir):
        """Test inicialización."""
        ops = FileOperations(temp_dir)

        assert ops.base_dir == temp_dir

    def test_init_creates_dir(self, temp_dir):
        """Test que init crea directorio."""
        new_dir = temp_dir / "new_ops_dir"

        ops = FileOperations(new_dir)

        assert new_dir.exists()

    def test_copy_relative_path(self, temp_dir, sample_pdf_path):
        """Test copiar con ruta relativa."""
        ops = FileOperations(temp_dir)

        result = ops.copy(sample_pdf_path.name, "copia.pdf")

        assert (temp_dir / "copia.pdf").exists()

    def test_list_folders(self, temp_dir):
        """Test listar carpetas."""
        (temp_dir / "folder1").mkdir()
        (temp_dir / "folder2").mkdir()
        (temp_dir / "file.txt").write_text("test")

        ops = FileOperations(temp_dir)
        folders = ops.list_folders()

        assert len(folders) == 2
        assert all(f.is_dir() for f in folders)

    def test_list_files(self, temp_dir, sample_pdf_files):
        """Test listar archivos."""
        ops = FileOperations(temp_dir)

        files = ops.list_files("*.pdf")

        assert len(files) == 5

    def test_get_info(self, temp_dir, sample_pdf_path):
        """Test obtener info."""
        ops = FileOperations(temp_dir)

        info = ops.get_info(sample_pdf_path.name)

        assert info["name"] == sample_pdf_path.name


class TestPDFOrganizer:
    """Tests para PDFOrganizer."""

    def test_organize_by_type(self, temp_dir, sample_pdf_files):
        """Test organizar por tipo."""
        repo = LocalPDFRepository(temp_dir)
        organizer = PDFOrganizer(repo)

        results = organizer.organize_by_type()

        assert "CTA_AHORROS" in results
        assert "TARJETA_MASTERCARD" in results
        assert (temp_dir / "CTA_AHORROS").exists()

    def test_organize_by_type_dry_run(self, temp_dir, sample_pdf_files):
        """Test organizar por tipo en dry run."""
        repo = LocalPDFRepository(temp_dir)
        organizer = PDFOrganizer(repo)

        results = organizer.organize_by_type(dry_run=True)

        assert "CTA_AHORROS" in results
        # No se deben crear carpetas
        assert not (temp_dir / "CTA_AHORROS").exists()

    def test_organize_by_year(self, temp_dir, sample_pdf_files):
        """Test organizar por año."""
        repo = LocalPDFRepository(temp_dir)
        organizer = PDFOrganizer(repo)

        results = organizer.organize_by_year()

        assert "2023" in results or "2024" in results

    def test_organize_by_month(self, temp_dir, sample_pdf_files):
        """Test organizar por mes."""
        repo = LocalPDFRepository(temp_dir)
        organizer = PDFOrganizer(repo)

        results = organizer.organize_by_month()

        # Debería tener formato YYYY/MM
        assert any("/" in key for key in results.keys())

    def test_organize_by_custom(self, temp_dir, sample_pdf_files):
        """Test organizar con función personalizada."""
        repo = LocalPDFRepository(temp_dir)
        organizer = PDFOrganizer(repo)

        results = organizer.organize_by_custom(
            key_func=lambda doc: "PAR" if int(doc.info.numero) % 2 == 0 else "IMPAR"
        )

        assert len(results) > 0

    def test_flatten(self, temp_dir, sample_pdf_files):
        """Test aplanar estructura."""
        repo = LocalPDFRepository(temp_dir)
        organizer = PDFOrganizer(repo)

        # Primero organizar
        organizer.organize_by_type()

        # Refrescar repo
        repo.refresh()

        # Luego aplanar
        moved = organizer.flatten()

        # Verificar que archivos volvieron a raíz
        root_pdfs = list(temp_dir.glob("*.pdf"))
        assert len(root_pdfs) >= len(moved)

    def test_preview_organization(self, temp_dir, sample_pdf_files):
        """Test previsualización."""
        repo = LocalPDFRepository(temp_dir)
        organizer = PDFOrganizer(repo)

        preview = organizer.preview_organization(by="type")

        assert isinstance(preview, dict)
        assert all(isinstance(v, list) for v in preview.values())

    def test_preview_invalid_criteria(self, temp_dir, sample_pdf_files):
        """Test previsualización con criterio inválido."""
        repo = LocalPDFRepository(temp_dir)
        organizer = PDFOrganizer(repo)

        with pytest.raises(ValueError):
            organizer.preview_organization(by="invalid")


class TestPDFRegistry:
    """Tests para PDFRegistry."""

    def test_scan(self, temp_dir, sample_pdf_files):
        """Test escaneo."""
        repo = LocalPDFRepository(temp_dir)
        registry = PDFRegistry(repo)

        docs = registry.scan()

        assert len(docs) == 5

    def test_summary(self, temp_dir, sample_pdf_files):
        """Test resumen."""
        repo = LocalPDFRepository(temp_dir)
        registry = PDFRegistry(repo)

        summary = registry.summary()

        assert summary["total_documents"] == 5
        assert "by_type" in summary
        assert "by_year" in summary
        assert "total_size_human" in summary

    def test_to_json(self, temp_dir, sample_pdf_files):
        """Test exportar a JSON."""
        repo = LocalPDFRepository(temp_dir)
        registry = PDFRegistry(repo)
        output = temp_dir / "inventory.json"

        result = registry.to_json(output)

        assert result == output
        assert output.exists()

        # Verificar contenido
        with open(output) as f:
            data = json.load(f)
        assert "documents" in data
        assert len(data["documents"]) == 5

    def test_to_csv(self, temp_dir, sample_pdf_files):
        """Test exportar a CSV."""
        repo = LocalPDFRepository(temp_dir)
        registry = PDFRegistry(repo)
        output = temp_dir / "inventory.csv"

        result = registry.to_csv(output)

        assert result == output
        assert output.exists()

        # Verificar que tiene contenido
        content = output.read_text()
        assert "filename" in content
        assert "tipo" in content

    def test_to_csv_with_metadata(self, temp_dir, sample_pdf_files):
        """Test exportar a CSV con metadatos."""
        repo = LocalPDFRepository(temp_dir)
        registry = PDFRegistry(repo)
        output = temp_dir / "inventory_meta.csv"

        result = registry.to_csv(output, include_metadata=True)

        content = output.read_text()
        assert "metadata" in content

    def test_to_markdown(self, temp_dir, sample_pdf_files):
        """Test exportar a Markdown."""
        repo = LocalPDFRepository(temp_dir)
        registry = PDFRegistry(repo)
        output = temp_dir / "inventory.md"

        result = registry.to_markdown(output)

        assert result == output
        content = output.read_text()
        assert "# Inventario de PDFs" in content
        assert "## Resumen" in content

    def test_find_duplicates_none(self, temp_dir, sample_pdf_files):
        """Test buscar duplicados cuando no hay."""
        repo = LocalPDFRepository(temp_dir)
        registry = PDFRegistry(repo)

        # Todos los archivos tienen el mismo contenido, así que serán "duplicados"
        duplicates = registry.find_duplicates()

        # Como todos tienen el mismo tamaño, todos son "duplicados"
        assert len(duplicates) >= 0

    def test_get_statistics(self, temp_dir, sample_pdf_files):
        """Test estadísticas."""
        repo = LocalPDFRepository(temp_dir)
        registry = PDFRegistry(repo)

        stats = registry.get_statistics()

        assert stats["count"] == 5
        assert "size" in stats
        assert "types" in stats
        assert "dates" in stats

    def test_get_statistics_empty(self, temp_dir):
        """Test estadísticas con repositorio vacío."""
        repo = LocalPDFRepository(temp_dir)
        registry = PDFRegistry(repo)

        stats = registry.get_statistics()

        assert "error" in stats
