# Configuración de Logging - Sistema Dinámico

## Resumen

El proyecto utiliza un **sistema de logging estratificado y configurable** que permite ajustar los niveles de logging sin modificar código, usando variables de entorno.

## Características

✅ **Configuración por categorías** - 4 niveles según la función del módulo
✅ **Variables de entorno** - Cambia niveles sin tocar código
✅ **Consola limpia** - Solo información relevante para el usuario
✅ **Logs completos** - Todo se registra en archivo para debugging
✅ **Flexibilidad** - Fácil cambio entre desarrollo y producción

## Arquitectura de 4 Niveles

### Nivel 1: Scripts CLI
**Módulos**: `process_excel_directory.py`, `consolidate_excel.py`, `batch_consolidate_excel.py`

**Función**: Interfaz directa con el usuario

**Configuración Default**:
- Level: INFO
- Consola: ✅ Activada
- Archivo: ✅ Activado

**Variable de entorno**: `LOG_LEVEL_CLI`

**Uso en código**:
```python
from logger import setup_logger, setup_cli_logger

logger = setup_cli_logger(setup_logger, __name__)
```

---

### Nivel 2: Coordinadores
**Módulos**:
- `src/excel_consolidator/consolidator.py`
- `src/excel_consolidator/batch.py`
- `src/find_excel_and_extract_sheets/core.py`
- `src/excel_extractor/extractor.py`

**Función**: Orquestación de operaciones y flujos de trabajo

**Configuración Default**:
- Level: INFO
- Consola: ✅ Activada (muestra progreso)
- Archivo: ✅ Activado

**Variable de entorno**: `LOG_LEVEL_COORDINATORS`

**Uso en código**:
```python
from logger import setup_logger, setup_coordinator_logger

logger = setup_coordinator_logger(setup_logger, __name__)
```

---

### Nivel 3: Procesadores
**Módulos**:
- `src/excel_consolidator/detector.py`
- `src/excel_consolidator/extractor.py`
- `src/excel_handler/handler.py`
- `src/excel_handler/quick.py`

**Función**: Procesamiento específico de datos

**Configuración Default**:
- Level: INFO
- Consola: ❌ Desactivada (evita saturación)
- Archivo: ✅ Activado

**Variable de entorno**: `LOG_LEVEL_PROCESSORS`

**Uso en código**:
```python
from logger import setup_logger, setup_processor_logger

logger = setup_processor_logger(setup_logger, __name__)
```

---

### Nivel 4: Utilidades
**Módulos**:
- `src/excel_consolidator/utils.py`
- `src/excel_handler/utils.py`

**Función**: Funciones auxiliares de bajo nivel

**Configuración Default**:
- Level: WARNING (solo problemas)
- Consola: ❌ Desactivada
- Archivo: ✅ Activado

**Variable de entorno**: `LOG_LEVEL_UTILS`

**Uso en código**:
```python
from logger import setup_logger, setup_utils_logger

logger = setup_utils_logger(setup_logger, __name__)
```

---

## Configuración por Variables de Entorno

### Archivo `.env`

Crea un archivo `.env` en la raíz del proyecto (o copia desde `.env.example`):

```bash
# Configuración por defecto (balanceada)
LOG_LEVEL_CLI=INFO
LOG_LEVEL_COORDINATORS=INFO
LOG_LEVEL_PROCESSORS=INFO
LOG_LEVEL_UTILS=WARNING
```

### Modo Desarrollo (Debugging)

Para debugging completo con máximo detalle:

```bash
LOG_LEVEL_CLI=DEBUG
LOG_LEVEL_COORDINATORS=DEBUG
LOG_LEVEL_PROCESSORS=DEBUG
LOG_LEVEL_UTILS=DEBUG
```

### Modo Producción (Mínimo Ruido)

Para producción con logging mínimo:

```bash
LOG_LEVEL_CLI=WARNING
LOG_LEVEL_COORDINATORS=WARNING
LOG_LEVEL_PROCESSORS=WARNING
LOG_LEVEL_UTILS=ERROR
```

### Debugging Selectivo

Puedes depurar solo un nivel específico:

```bash
# Solo debugging de procesadores
LOG_LEVEL_CLI=INFO
LOG_LEVEL_COORDINATORS=INFO
LOG_LEVEL_PROCESSORS=DEBUG  # Solo este en DEBUG
LOG_LEVEL_UTILS=WARNING
```

---

## Niveles de Logging Disponibles

| Nivel | Uso | Cuándo usar |
|-------|-----|-------------|
| DEBUG | Información detallada para debugging | Desarrollo, troubleshooting |
| INFO | Confirmación de operaciones normales | Default, producción normal |
| WARNING | Advertencias, situaciones inesperadas | Producción, monitoreo |
| ERROR | Errores que requieren atención | Siempre |
| CRITICAL | Errores críticos que detienen la app | Siempre |

---

## Ejemplo de Uso Completo

### 1. Crear Nuevo Módulo Coordinador

```python
"""Mi nuevo módulo coordinador."""
from logger import setup_logger, setup_coordinator_logger

# Configuración dinámica desde .env
logger = setup_coordinator_logger(setup_logger, __name__)


class MiCoordinador:
    def procesar(self):
        logger.info("Iniciando procesamiento...")
        # ...
        logger.info("Procesamiento completado")
```

### 2. Crear Nuevo Módulo de Utilidades

```python
"""Mi módulo de utilidades."""
from logger import setup_logger, setup_utils_logger

# Solo reportará WARNING y superior
logger = setup_utils_logger(setup_logger, __name__)


def mi_utilidad():
    # Este log NO aparecerá (es INFO, nivel es WARNING)
    logger.info("Procesando...")

    # Este SÍ aparecerá
    logger.warning("Cuidado con esto")
```

### 3. Cambiar Nivel Temporalmente

Si necesitas más detalle en un módulo específico, puedes sobrescribir temporalmente:

```python
from logger import setup_logger

# Override temporal para debugging
logger = setup_logger(
    __name__,
    level="DEBUG",
    console_output=True,
    file_output=True
)
```

---

## Estructura de Archivos de Log

Los logs se guardan en `logs/` con rotación diaria:

```
logs/
├── 2025-01-15.log
├── 2025-01-16.log
└── 2025-01-17.log
```

**Formato de log**:
```
2025-01-16 10:30:45 - src.excel_consolidator.consolidator - INFO - Consolidando archivo: datos.xlsx
```

---

## Beneficios del Sistema

### 1. Mantenibilidad
- No modificas código para cambiar niveles
- Configuración centralizada en `.env`
- Consistencia en todo el proyecto

### 2. Flexibilidad
- Cambio rápido entre desarrollo y producción
- Debugging selectivo por categoría
- Fácil troubleshooting

### 3. Rendimiento
- Reduce ruido en consola
- Logs de utilidades solo cuando hay problemas
- Mejor experiencia de usuario

### 4. Debugging Eficiente
- Todos los detalles en archivo
- Consola limpia y enfocada
- Trazabilidad completa

---

## Troubleshooting

### No veo logs en consola

**Problema**: Módulo procesador o utilidad no muestra en consola

**Solución**: Es intencional. Estos módulos solo escriben a archivo. Si necesitas ver en consola:

```python
# Temporal para debugging
from logger import setup_logger
logger = setup_logger(__name__, level="DEBUG", console_output=True)
```

### Demasiado ruido en consola

**Problema**: Muchos logs irrelevantes

**Solución**: Ajusta niveles en `.env`:

```bash
# Reduce ruido
LOG_LEVEL_CLI=WARNING
LOG_LEVEL_COORDINATORS=WARNING
```

### No se crean archivos de log

**Problema**: No aparecen archivos en `logs/`

**Verificar**:
1. El directorio `logs/` existe (se crea automáticamente)
2. Permisos de escritura
3. La variable `file_output=True` en la configuración

### Quiero ver TODO en modo debug

**Solución**: Actualiza `.env`:

```bash
LOG_LEVEL_CLI=DEBUG
LOG_LEVEL_COORDINATORS=DEBUG
LOG_LEVEL_PROCESSORS=DEBUG
LOG_LEVEL_UTILS=DEBUG
```

---

## Migración de Código Antiguo

Si tienes código con configuración antigua:

### Antes
```python
from logger import setup_logger

logger = setup_logger(
    __name__,
    level="INFO",
    console_output=True,
    file_output=True
)
```

### Después
```python
from logger import setup_logger, setup_coordinator_logger

# Automático, lee desde .env
logger = setup_coordinator_logger(setup_logger, __name__)
```

---

## Mejores Prácticas

### ✅ Hacer

- Usar las funciones helper apropiadas para cada categoría
- Configurar niveles en `.env`, no en código
- Mantener logs de archivo activados siempre
- Usar DEBUG solo temporalmente

### ❌ No Hacer

- Hardcodear niveles en código de producción
- Desactivar logs de archivo
- Usar DEBUG en producción permanentemente
- Modificar el paquete `logger/` directamente

---

## Referencias

- **Propuesta completa**: `docs/LOGGER_CONFIGURATION_PROPOSAL.md`
- **Sistema de logging**: `src/logger/logging_config.py`
- **Config helpers**: `src/logger/config_helper.py`
- **Variables de entorno**: `src/config.py`
- **Ejemplo .env**: `.env.example`

---

## Resumen de Comandos

```bash
# Ver archivo .env.example
cat .env.example

# Copiar y configurar .env
cp .env.example .env
nano .env  # Editar variables

# Ejecutar con configuración por defecto
python process_excel_directory.py "directorio/"

# Ver logs del día
cat logs/$(date +%Y-%m-%d).log

# Ver solo errores del día
grep ERROR logs/$(date +%Y-%m-%d).log
```

---

## Actualización del Sistema

**Versión**: 1.1.0
**Última actualización**: 2025-01-16
**Compatibilidad**: Retrocompatible con configuración anterior
