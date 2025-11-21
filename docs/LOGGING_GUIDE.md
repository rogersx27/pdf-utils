# Guía del Sistema de Logging

Sistema de logging comprehensivo con archivos organizados por fecha y salida en consola con colores.

## Características

- ✅ **Archivos por fecha**: Un archivo nuevo cada día (formato: `YYYY-MM-DD.log`)
- ✅ **Colores en consola**: Diferentes colores para cada nivel de log
- ✅ **Múltiples niveles**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- ✅ **Fácil de usar**: Configuración simple con valores por defecto inteligentes
- ✅ **Flexible**: Configuración personalizada por módulo
- ✅ **Rotación automática**: Cambio de archivo a medianoche

## Instalación

Las dependencias ya están incluidas en `requirements.txt`:
```bash
pip install colorlog
```

## Uso Básico

### 1. Importar y configurar

```python
from logger import setup_logger

# Crear logger
logger = setup_logger(__name__)

# Usar el logger
logger.info("Aplicación iniciada")
logger.warning("Advertencia")
logger.error("Error encontrado")
```

### 2. Diferentes niveles de log

```python
logger.debug("Información de debugging")      # Solo en modo DEBUG
logger.info("Información general")            # Información normal
logger.warning("Advertencia")                 # Algo sospechoso
logger.error("Error")                         # Error que debe ser corregido
logger.critical("Error crítico")              # Error muy grave
```

## Configuración

### Logger con nivel DEBUG

```python
logger = setup_logger(__name__, level="DEBUG")
logger.debug("Este mensaje ahora es visible")
```

### Logger solo para archivo (sin consola)

```python
logger = setup_logger(
    __name__,
    console_output=False,
    file_output=True
)
logger.info("Solo en archivo, no en consola")
```

### Logger con directorio personalizado

```python
from pathlib import Path

logger = setup_logger(
    __name__,
    log_dir=Path("logs/custom")
)
```

### Logger solo para consola (sin archivo)

```python
logger = setup_logger(
    __name__,
    console_output=True,
    file_output=False
)
```

## Funciones Avanzadas

### Decorador para funciones

Loguea automáticamente las llamadas a funciones:

```python
from logger import setup_logger, log_function_call

logger = setup_logger(__name__, level="DEBUG")

@log_function_call(logger)
def procesar_datos(archivo):
    # Tu código aquí
    return resultado

# Se loguea automáticamente:
# - Entrada: argumentos de la función
# - Salida: resultado o error
resultado = procesar_datos("datos.xlsx")
```

### Logger por módulo

Crea loggers con diferentes configuraciones para diferentes módulos:

```python
from logger import create_module_logger

# Logger para base de datos (muy detallado)
db_logger = create_module_logger("database", level="DEBUG")

# Logger para API (normal)
api_logger = create_module_logger("api", level="INFO")

# Logger para seguridad (solo warnings)
security_logger = create_module_logger("security", level="WARNING")
```

### Configuración global

Configura logging para toda la aplicación de una vez:

```python
from logger import configure_root_logger

# Al inicio de tu aplicación
configure_root_logger(level="INFO")

# Ahora todos los loggers funcionarán automáticamente
import logging
logger = logging.getLogger(__name__)
logger.info("Mensaje")
```

### Obtener logger existente

```python
from logger import get_logger

# Obtiene el logger si existe, o crea uno nuevo
logger = get_logger(__name__)
```

## Logging de Excepciones

Para incluir el traceback completo en los logs:

```python
try:
    # código que puede fallar
    resultado = procesar_archivo()
except Exception as e:
    logger.error(f"Error procesando archivo: {e}", exc_info=True)
```

## Niveles de Log - Cuándo usar cada uno

| Nivel | Uso | Ejemplo |
|-------|-----|---------|
| `DEBUG` | Información detallada para debugging | `logger.debug("Variable x = 10")` |
| `INFO` | Confirmación de que todo funciona | `logger.info("Archivo procesado exitosamente")` |
| `WARNING` | Algo inesperado pero no crítico | `logger.warning("Memoria al 80%")` |
| `ERROR` | Error que impide una función específica | `logger.error("No se pudo leer archivo")` |
| `CRITICAL` | Error grave que puede detener el programa | `logger.critical("Base de datos no disponible")` |

## Estructura de Archivos de Log

```
logs/
├── 2025-01-15.log    # Logs del 15 de enero
├── 2025-01-16.log    # Logs del 16 de enero
└── 2025-01-17.log    # Logs del 17 de enero (hoy)
```

Cada archivo contiene todos los logs de ese día, de todos los módulos.

## Formato de Log

### En archivo:
```
2025-01-17 14:30:45 - module_name - INFO - Mensaje de log
2025-01-17 14:30:46 - module_name - ERROR - Error encontrado
```

### En consola (con colores):
- **DEBUG**: Cyan
- **INFO**: Verde
- **WARNING**: Amarillo
- **ERROR**: Rojo
- **CRITICAL**: Rojo con fondo blanco

## Ejemplos Completos

### Ejemplo 1: Aplicación simple

```python
from logger import setup_logger

def main():
    logger = setup_logger(__name__)

    logger.info("Iniciando aplicación")

    try:
        procesar_datos()
        logger.info("Procesamiento completado")
    except Exception as e:
        logger.error(f"Error en procesamiento: {e}", exc_info=True)

if __name__ == "__main__":
    main()
```

### Ejemplo 2: Múltiples módulos

```python
# archivo: database.py
from logger import create_module_logger

logger = create_module_logger("database", level="DEBUG")

def conectar():
    logger.debug("Intentando conectar a DB...")
    logger.info("Conexión establecida")
```

```python
# archivo: api.py
from logger import create_module_logger

logger = create_module_logger("api", level="INFO")

def procesar_request(request):
    logger.info(f"Request recibido: {request.method} {request.path}")
    # proceso...
    logger.info("Response enviado")
```

### Ejemplo 3: Con contexto rico

```python
from logger import setup_logger

logger = setup_logger(__name__)

def procesar_excel(archivo):
    logger.info(f"Procesando archivo: {archivo}")

    # Leer archivo
    filas = 1500
    columnas = 25
    logger.info(f"Archivo cargado: {filas} filas, {columnas} columnas")

    # Procesar
    for i in range(100):
        if i % 20 == 0:
            logger.debug(f"Progreso: {i}%")

    logger.info(f"✓ {archivo} procesado exitosamente")
```

## Ejecución de Ejemplos

Para ver todos los ejemplos en acción:

```bash
python examples/logging_example.py
```

Esto ejecutará 10 ejemplos diferentes que demuestran todas las funcionalidades.

## Consejos

1. **Usa __name__ como nombre del logger**: Esto permite identificar fácilmente el módulo que generó el log
   ```python
   logger = setup_logger(__name__)
   ```

2. **No hagas logging en bucles intensivos**: Puede ralentizar tu aplicación
   ```python
   # ❌ Mal
   for i in range(1000000):
       logger.debug(f"Iteración {i}")

   # ✅ Bien
   for i in range(1000000):
       if i % 10000 == 0:
           logger.debug(f"Progreso: {i}")
   ```

3. **Usa niveles apropiados**: DEBUG para desarrollo, INFO para producción

4. **Incluye contexto útil**: No solo "Error", sino "Error procesando archivo X: mensaje"

5. **Usa exc_info=True para excepciones**: Incluye el traceback completo

## Solución de Problemas

### Los logs DEBUG no aparecen

```python
# Asegúrate de configurar el nivel a DEBUG
logger = setup_logger(__name__, level="DEBUG")
```

### Los logs no se guardan en archivo

```python
# Verifica que file_output=True (es el default)
logger = setup_logger(__name__, file_output=True)
```

### No veo colores en la consola

```python
# Verifica que colorlog esté instalado
pip install colorlog

# Y que console_output=True (es el default)
logger = setup_logger(__name__, console_output=True)
```
