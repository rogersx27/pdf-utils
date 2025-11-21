"""
Script para copiar PDFs y quitarles la contraseña.

Paso 1: Copia los PDFs de data/ a password-less/
Paso 2: Quita la contraseña de cada copia

Uso:
    python remove_passwords.py
    python remove_passwords.py --password mi_contraseña
"""
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf_analyzer import LocalPDFRepository, SecurityService, copy_pdf, ensure_directory

def main():
    # Configuración
    password = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--password" else None

    data_dir = Path(__file__).parent / "data"
    output_dir = Path(__file__).parent / "password-less"

    # Crear carpeta de salida
    ensure_directory(output_dir)
    print(f"Carpeta de salida: {output_dir}")

    # Cargar repositorio
    repo = LocalPDFRepository(data_dir)
    docs = repo.get_all()

    if not docs:
        print("No se encontraron PDFs en data/")
        return

    print(f"Encontrados {len(docs)} PDFs")
    print("-" * 50)

    # Inicializar servicio de seguridad
    security = SecurityService(password=password)

    success_count = 0
    error_count = 0

    for doc in docs:
        print(f"\nProcesando: {doc.filename}")

        try:
            # Paso 1: Copiar a password-less/
            dest_path = output_dir / doc.filename
            copy_pdf(doc.path, dest_path, overwrite=True)
            print(f"  [1] Copiado a: {dest_path.name}")

            # Paso 2: Quitar contraseña (sobreescribir el mismo archivo)
            if security.is_encrypted(dest_path):
                # Crear archivo temporal sin contraseña
                temp_path = output_dir / f"_temp_{doc.filename}"
                security.remove_password(dest_path, temp_path, password)

                # Reemplazar original con el desbloqueado
                dest_path.unlink()
                temp_path.rename(dest_path)
                print("  [2] Contraseña removida")
            else:
                print("  [2] No está encriptado, saltando")

            success_count += 1

        except (OSError, IOError, PermissionError, ValueError, RuntimeError) as e:
            print(f"  ERROR: {e}")
            error_count += 1

    print("\n" + "=" * 50)
    print(f"Completado: {success_count} exitosos, {error_count} errores")
    print(f"Archivos en: {output_dir}")


if __name__ == "__main__":
    main()
