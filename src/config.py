"""Configuración del proyecto."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Rutas base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Configuración general
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configuración de Logging por Categoría
# Permite ajustar niveles de logging sin modificar código
LOG_LEVEL_CLI = os.getenv("LOG_LEVEL_CLI", "INFO")
LOG_LEVEL_COORDINATORS = os.getenv("LOG_LEVEL_COORDINATORS", "INFO")
LOG_LEVEL_PROCESSORS = os.getenv("LOG_LEVEL_PROCESSORS", "INFO")
LOG_LEVEL_UTILS = os.getenv("LOG_LEVEL_UTILS", "WARNING")

# Crear directorios si no existen
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
