"""
Registro e inventario de archivos PDF.

Proporciona funcionalidades para escanear, inventariar y
exportar información de los documentos PDF.
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from logger import setup_logger, setup_coordinator_logger

from pdf_analyzer.models import PDFDocument
from pdf_analyzer.repositories.base import BaseRepository

logger = setup_coordinator_logger(setup_logger, __name__)


class PDFRegistry:
    """
    Registro de documentos PDF.

    Permite escanear, inventariar y exportar información
    de los documentos en un repositorio.
    """

    def __init__(self, repository: BaseRepository):
        """
        Inicializa el registro con un repositorio.

        Args:
            repository: Repositorio de PDFs.
        """
        self._repository = repository
        self._last_scan: Optional[datetime] = None
        logger.debug(f"PDFRegistry inicializado")

    def scan(self, refresh: bool = True) -> list[PDFDocument]:
        """
        Escanea y retorna todos los documentos.

        Args:
            refresh: Si es True, actualiza la caché del repositorio primero.

        Returns:
            Lista de todos los PDFDocument.
        """
        if refresh:
            self._repository.refresh()

        documents = self._repository.get_all()
        self._last_scan = datetime.now()

        logger.info(f"Escaneados {len(documents)} documentos")
        return documents

    def summary(self) -> dict:
        """
        Genera un resumen estadístico del registro.

        Returns:
            Diccionario con estadísticas.
        """
        documents = self._repository.get_all()

        by_type: dict[str, int] = {}
        by_year: dict[int, int] = {}
        total_size = 0

        for doc in documents:
            # Contar por tipo
            tipo = doc.tipo or "OTROS"
            by_type[tipo] = by_type.get(tipo, 0) + 1

            # Contar por año
            year = doc.info.year or 0
            by_year[year] = by_year.get(year, 0) + 1

            # Sumar tamaño
            total_size += doc.file_size

        summary = {
            "total_documents": len(documents),
            "total_size": total_size,
            "total_size_human": self._format_size(total_size),
            "by_type": dict(sorted(by_type.items())),
            "by_year": dict(sorted(by_year.items())),
            "types": sorted(by_type.keys()),
            "years": sorted([y for y in by_year.keys() if y > 0]),
            "last_scan": self._last_scan.isoformat() if self._last_scan else None,
        }

        logger.info(f"Resumen: {summary['total_documents']} docs, {summary['total_size_human']}")
        return summary

    def to_json(
        self,
        output_path: Path | str,
        indent: int = 2,
    ) -> Path:
        """
        Exporta el registro a un archivo JSON.

        Args:
            output_path: Ruta del archivo de salida.
            indent: Indentación del JSON.

        Returns:
            Ruta del archivo creado.
        """
        output_path = Path(output_path)
        documents = self._repository.get_all()

        data = {
            "generated_at": datetime.now().isoformat(),
            "total_documents": len(documents),
            "documents": [doc.to_dict() for doc in documents],
            "summary": self.summary(),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)

        logger.info(f"Registro exportado a JSON: {output_path}")
        return output_path

    def to_csv(
        self,
        output_path: Path | str,
        include_metadata: bool = False,
    ) -> Path:
        """
        Exporta el registro a un archivo CSV.

        Args:
            output_path: Ruta del archivo de salida.
            include_metadata: Si incluir metadatos del PDF.

        Returns:
            Ruta del archivo creado.
        """
        output_path = Path(output_path)
        documents = self._repository.get_all()

        # Definir columnas
        fieldnames = [
            "filename",
            "tipo",
            "fecha",
            "year",
            "month",
            "num_pages",
            "is_encrypted",
            "file_size",
            "file_size_human",
            "path",
        ]

        if include_metadata:
            fieldnames.extend(["metadata"])

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for doc in documents:
                row = {
                    "filename": doc.filename,
                    "tipo": doc.tipo,
                    "fecha": doc.fecha,
                    "year": doc.info.year,
                    "month": doc.info.month,
                    "num_pages": doc.num_pages,
                    "is_encrypted": doc.is_encrypted,
                    "file_size": doc.file_size,
                    "file_size_human": self._format_size(doc.file_size),
                    "path": str(doc.path),
                }

                if include_metadata:
                    row["metadata"] = json.dumps(doc.metadata)

                writer.writerow(row)

        logger.info(f"Registro exportado a CSV: {output_path}")
        return output_path

    def to_markdown(self, output_path: Path | str) -> Path:
        """
        Exporta el registro a un archivo Markdown.

        Args:
            output_path: Ruta del archivo de salida.

        Returns:
            Ruta del archivo creado.
        """
        output_path = Path(output_path)
        documents = self._repository.get_all()
        summary = self.summary()

        lines = [
            "# Inventario de PDFs",
            "",
            f"*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "## Resumen",
            "",
            f"- **Total documentos:** {summary['total_documents']}",
            f"- **Tamaño total:** {summary['total_size_human']}",
            "",
            "### Por Tipo",
            "",
        ]

        for tipo, count in summary["by_type"].items():
            lines.append(f"- {tipo}: {count}")

        lines.extend([
            "",
            "### Por Año",
            "",
        ])

        for year, count in summary["by_year"].items():
            if year > 0:
                lines.append(f"- {year}: {count}")

        lines.extend([
            "",
            "## Documentos",
            "",
            "| Archivo | Tipo | Fecha | Tamaño |",
            "|---------|------|-------|--------|",
        ])

        for doc in documents:
            size = self._format_size(doc.file_size)
            lines.append(f"| {doc.filename} | {doc.tipo} | {doc.fecha} | {size} |")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info(f"Registro exportado a Markdown: {output_path}")
        return output_path

    def find_duplicates(self) -> dict[str, list[PDFDocument]]:
        """
        Encuentra posibles documentos duplicados.

        Busca archivos con el mismo tamaño que podrían ser duplicados.

        Returns:
            Diccionario con tamaño como clave y lista de documentos.
        """
        documents = self._repository.get_all()
        by_size: dict[int, list[PDFDocument]] = {}

        for doc in documents:
            if doc.file_size not in by_size:
                by_size[doc.file_size] = []
            by_size[doc.file_size].append(doc)

        # Filtrar solo los que tienen duplicados
        duplicates = {
            size: docs for size, docs in by_size.items()
            if len(docs) > 1
        }

        if duplicates:
            total = sum(len(docs) for docs in duplicates.values())
            logger.warning(f"Encontrados {total} posibles duplicados en {len(duplicates)} grupos")
        else:
            logger.info("No se encontraron duplicados")

        return duplicates

    def get_statistics(self) -> dict:
        """
        Obtiene estadísticas detalladas del registro.

        Returns:
            Diccionario con estadísticas detalladas.
        """
        documents = self._repository.get_all()

        if not documents:
            return {"error": "No hay documentos"}

        sizes = [doc.file_size for doc in documents]

        return {
            "count": len(documents),
            "size": {
                "total": sum(sizes),
                "average": sum(sizes) / len(sizes),
                "min": min(sizes),
                "max": max(sizes),
                "total_human": self._format_size(sum(sizes)),
                "average_human": self._format_size(int(sum(sizes) / len(sizes))),
            },
            "types": {
                "unique": len(set(doc.tipo for doc in documents if doc.tipo)),
                "list": sorted(set(doc.tipo for doc in documents if doc.tipo)),
            },
            "dates": {
                "years": sorted(set(doc.info.year for doc in documents if doc.info.year)),
                "range": {
                    "earliest": min(doc.fecha for doc in documents if doc.fecha),
                    "latest": max(doc.fecha for doc in documents if doc.fecha),
                },
            },
        }

    @staticmethod
    def _format_size(size: int) -> str:
        """Formatea un tamaño en bytes a formato legible."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
