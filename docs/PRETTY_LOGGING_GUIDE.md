# Pretty Logging - Guía de Uso

## Introducción

El sistema de **Pretty Logging** proporciona funciones helper para crear logs más legibles y estéticamente agradables, sin complicaciones innecesarias.

**Filosofía**: Mantener las cosas simples pero con buenas prácticas.

## Instalación

Ya está incluido en el proyecto. Solo importa las funciones que necesites:

```python
from logger import (
    setup_cli_logger,
    setup_logger,
    log_header,
    log_section,
    log_success,
    log_error,
    indent,
)
```

## Funciones Disponibles

### Formato Básico

#### `log_header(logger, text, icon="🎯")`
Encabezado principal con marco decorativo.

```python
log_header(logger, "MI APLICACIÓN", icon="🚀")
```
**Output**:
```
╔══════════════════════════════════════════════════════════╗
║ 🚀  MI APLICACIÓN                                       ║
╚══════════════════════════════════════════════════════════╝
```

---

#### `log_section(logger, text, icon="📋")`
Sección con icono.

```python
log_section(logger, "Procesando archivos", icon="📁")
```
**Output**:
```
📁 Procesando archivos
```

---

#### `log_subsection(logger, text, icon="▸")`
Subsección.

```python
log_subsection(logger, "Análisis de datos")
```
**Output**:
```
  ▸ Análisis de datos
```

---

#### `log_info(logger, text, prefix="ℹ️")`
Información general.

```python
log_info(logger, "Archivo procesado correctamente")
```
**Output**:
```
ℹ️  Archivo procesado correctamente
```

---

#### `log_success(logger, text)`
Mensaje de éxito.

```python
log_success(logger, "Consolidación completada")
```
**Output**:
```
✅ Consolidación completada
```

---

#### `log_error(logger, text)`
Mensaje de error.

```python
log_error(logger, "No se pudo abrir el archivo")
```
**Output**:
```
❌ No se pudo abrir el archivo
```

---

#### `log_warning(logger, text)`
Mensaje de advertencia.

```python
log_warning(logger, "El archivo está vacío")
```
**Output**:
```
⚠️  El archivo está vacío
```

---

### Items y Listas

#### `log_item(logger, key, value, bullet="├─")`
Item en formato árbol/lista.

```python
log_item(logger, "Archivos", 42)
log_item(logger, "Estado", "Completado", bullet="└─")
```
**Output**:
```
├─ Archivos: 42
└─ Estado: Completado
```

---

#### `log_list(logger, items, title=None, icon="•")`
Lista de items.

```python
log_list(logger, ["archivo1.xlsx", "archivo2.xlsx"], title="Archivos procesados")
```
**Output**:
```
📋 Archivos procesados
  • archivo1.xlsx
  • archivo2.xlsx
```

---

### Datos Estructurados

#### `log_dict(logger, data, title=None)`
Diccionario con formato de árbol.

```python
log_dict(logger, {
    "Nombre": "Juan",
    "Edad": 30,
    "Ciudad": "Madrid"
}, title="Usuario")
```
**Output**:
```
📋 Usuario
├─ Nombre: Juan
├─ Edad: 30
└─ Ciudad: Madrid
```

---

#### `log_stats(logger, stats, title="Estadísticas")`
Estadísticas con formato bonito.

```python
log_stats(logger, {
    "Archivos procesados": 42,
    "Errores": 0,
    "Tiempo": "2.5s"
})
```
**Output**:
```
📊 Estadísticas
├─ Archivos procesados: 42
├─ Errores: 0
└─ Tiempo: 2.5s
```

---

#### `log_table(logger, headers, rows, title=None)`
Tabla simple.

```python
headers = ["Nombre", "Edad", "Ciudad"]
rows = [
    ["Juan", 30, "Madrid"],
    ["Ana", 25, "Barcelona"]
]
log_table(logger, headers, rows, title="Usuarios")
```
**Output**:
```
📋 Usuarios
  Nombre │ Edad │ Ciudad
  ───────┼──────┼──────────
  Juan   │   30 │ Madrid
  Ana    │   25 │ Barcelona
```

---

### Context Helpers (Excel-specific)

#### `log_file_info(logger, filename, details=None)`
Información de archivo con formato consistente.

```python
log_file_info(logger, "datos.xlsx", {
    "Tamaño": "2.5 MB",
    "Hojas": 3,
    "Tipo": "XLSX"
})
```
**Output**:
```
📄 Archivo: datos.xlsx
├─ Tamaño: 2.5 MB
├─ Hojas: 3
└─ Tipo: XLSX
```

---

#### `log_sheet_info(logger, sheet_name, info)`
Información de hoja Excel.

```python
log_sheet_info(logger, "Pendientes", {
    "Tipo": "COMPLEX",
    "Filas": 567,
    "Encabezados": 14
})
```
**Output**:
```
  📋 Hoja: Pendientes
     ├─ Tipo: COMPLEX
     ├─ Filas: 567
     └─ Encabezados: 14
```

---

### Indentación Automática

#### `indent()` (context manager)
Indenta automáticamente todo dentro del bloque.

```python
log_section(logger, "Procesando archivos")

with indent():
    log_info(logger, "Archivo 1")
    log_info(logger, "Archivo 2")

    with indent():
        log_info(logger, "Detalles del archivo 2")
```
**Output**:
```
📋 Procesando archivos
   ℹ️  Archivo 1
   ℹ️  Archivo 2
      ℹ️  Detalles del archivo 2
```

---

### Utilidades

#### `log_separator(logger, char="─", width=60)`
Separador visual.

```python
log_separator(logger)
```
**Output**:
```
────────────────────────────────────────────────────────────
```

---

#### `log_blank(logger, lines=1)`
Línea(s) en blanco.

```python
log_blank(logger)
log_blank(logger, lines=2)
```

---

### Formatters

#### `format_number(num)`
Formatea número con separadores.

```python
format_number(1234567)  # "1,234,567"
```

---

#### `format_bytes(bytes_size)`
Formatea bytes a formato legible.

```python
format_bytes(2621440)  # "2.5 MB"
```

---

#### `format_duration(seconds)`
Formatea duración.

```python
format_duration(45.2)   # "45.2s"
format_duration(125)    # "2m 5s"
format_duration(3665)   # "1h 1m"
```

---

## Ejemplos Completos

### Ejemplo 1: Script CLI Básico

```python
from logger import (
    setup_cli_logger,
    setup_logger,
    log_header,
    log_section,
    log_success,
    log_error,
    indent,
)

logger = setup_cli_logger(setup_logger, __name__)

def main():
    log_header(logger, "MI APLICACIÓN", icon="🚀")

    log_section(logger, "Iniciando procesamiento")

    with indent():
        log_info(logger, "Cargando configuración...")
        log_success(logger, "Configuración cargada")

        log_info(logger, "Procesando datos...")
        log_success(logger, "Datos procesados")

    log_blank(logger)
    log_success(logger, "Aplicación completada exitosamente")
```

---

### Ejemplo 2: Análisis de Archivo Excel

```python
from logger import (
    setup_cli_logger,
    setup_logger,
    log_header,
    log_file_info,
    log_sheet_info,
    log_blank,
    format_number,
)

logger = setup_cli_logger(setup_logger, __name__)

log_blank(logger)
log_header(logger, "ANÁLISIS DE EXCEL", icon="📊")

# Información del archivo
log_file_info(logger, "ventas.xlsx", {
    "Hojas": 3,
    "Tamaño": "1.2 MB"
})

# Información de hojas
log_blank(logger)
log_sheet_info(logger, "Enero", {
    "Tipo": "SIMPLE",
    "Filas": format_number(1250),
    "Columnas": 8
})

log_blank(logger)
log_sheet_info(logger, "Febrero", {
    "Tipo": "COMPLEX",
    "Filas": format_number(2340),
    "Columnas": 8
})
```

---

### Ejemplo 3: Procesamiento con Estadísticas

```python
from logger import (
    setup_cli_logger,
    setup_logger,
    log_header,
    log_section,
    log_stats,
    log_blank,
    indent,
    format_number,
    format_duration,
)

logger = setup_cli_logger(setup_logger, __name__)

log_blank(logger)
log_header(logger, "PROCESAMIENTO BATCH", icon="⚙️")

log_section(logger, "Procesando archivos...")

# Simular procesamiento...
time.sleep(2.5)

# Mostrar estadísticas
log_blank(logger)
log_stats(logger, {
    "Total archivos": 150,
    "Procesados": format_number(145),
    "Errores": 5,
    "Tiempo total": format_duration(152.3)
}, title="Resumen de Procesamiento")
```

---

### Ejemplo 4: Con Indentación Jerárquica

```python
from logger import (
    setup_cli_logger,
    setup_logger,
    log_section,
    log_file_info,
    log_success,
    indent,
)

logger = setup_cli_logger(setup_logger, __name__)

log_section(logger, "Directorio: data/", icon="📁")

with indent():
    log_file_info(logger, "archivo1.xlsx", {"Hojas": 2})

    with indent():
        log_success(logger, "Hoja 1 procesada")
        log_success(logger, "Hoja 2 procesada")

    log_file_info(logger, "archivo2.xlsx", {"Hojas": 1})

    with indent():
        log_success(logger, "Hoja 1 procesada")
```

**Output**:
```
📁 Directorio: data/
   📄 Archivo: archivo1.xlsx
   ├─ Hojas: 2
      ✅ Hoja 1 procesada
      ✅ Hoja 2 procesada
   📄 Archivo: archivo2.xlsx
   ├─ Hojas: 1
      ✅ Hoja 1 procesada
```

---

## Guía de Estilo

### ✅ Buenas Prácticas

1. **Usa log_blank() para separar secciones**
   ```python
   log_section(logger, "Sección 1")
   # ... contenido
   log_blank(logger)
   log_section(logger, "Sección 2")
   ```

2. **Usa indent() para jerarquías**
   ```python
   log_section(logger, "Principal")
   with indent():
       log_info(logger, "Detalle")
   ```

3. **Usa formatters para números grandes**
   ```python
   log_item(logger, "Filas", format_number(1234567))
   ```

4. **Usa iconos consistentes**
   - 📄 Archivos
   - 📁 Directorios
   - 📋 Hojas/Listas
   - 📊 Estadísticas
   - ✅ Éxito
   - ❌ Error
   - ⚠️ Advertencia
   - 🚀 Inicio
   - ⏱️ Tiempo

---

### ❌ Anti-Patrones

1. **No mezcles formatos**
   ```python
   # ❌ Malo
   logger.info("Archivo: datos.xlsx")
   log_file_info(logger, "otro.xlsx")

   # ✅ Bueno
   log_file_info(logger, "datos.xlsx")
   log_file_info(logger, "otro.xlsx")
   ```

2. **No anides demasiado**
   ```python
   # ❌ Malo (4+ niveles)
   with indent():
       with indent():
           with indent():
               with indent():
                   log_info(logger, "Muy anidado")

   # ✅ Bueno (2-3 niveles máximo)
   with indent():
       with indent():
           log_info(logger, "Bien")
   ```

3. **No abuses de separadores**
   ```python
   # ❌ Malo
   log_separator(logger)
   log_info(logger, "Info")
   log_separator(logger)

   # ✅ Bueno
   log_blank(logger)
   log_info(logger, "Info")
   log_blank(logger)
   ```

---

## Migración desde Logging Tradicional

### Antes (logging tradicional)
```python
logger.info("="*60)
logger.info("CONSOLIDADOR DE EXCEL")
logger.info("="*60)
logger.info("")

logger.info(f"Archivo: {filename}")
logger.info(f"   Hojas: {num_sheets}")
logger.info(f"   Tipo: {file_type}")

logger.info("")
logger.info("✅ CONSOLIDACIÓN EXITOSA")
logger.info(f"   Filas: {rows}")
logger.info(f"   Tiempo: {time:.2f}s")
```

### Después (pretty logging)
```python
log_blank(logger)
log_header(logger, "CONSOLIDADOR DE EXCEL", icon="🚀")

log_file_info(logger, filename, {
    "Hojas": num_sheets,
    "Tipo": file_type
})

log_blank(logger)
log_stats(logger, {
    "Estado": "✅ Exitoso",
    "Filas": format_number(rows),
    "Tiempo": f"{time:.2f}s"
}, title="Resultado")
```

**Beneficios**:
- 12 líneas → 8 líneas
- Más legible
- Formato consistente
- Indentación automática
- Mejor mantenimiento

---

## Referencia Rápida

| Función | Uso | Icono Default |
|---------|-----|---------------|
| `log_header` | Encabezado principal | 🎯 |
| `log_section` | Sección | 📋 |
| `log_subsection` | Subsección | ▸ |
| `log_info` | Información | ℹ️ |
| `log_success` | Éxito | ✅ |
| `log_error` | Error | ❌ |
| `log_warning` | Advertencia | ⚠️ |
| `log_file_info` | Info archivo | 📄 |
| `log_sheet_info` | Info hoja | 📋 |
| `log_stats` | Estadísticas | 📊 |

---

## Notas Técnicas

- **Indentación**: 3 espacios por nivel
- **Ancho por defecto**: 60 caracteres para headers
- **Thread-safe**: No (usa variable global simple para indentación)
- **Overhead**: Mínimo, solo formateo de strings
- **Compatibilidad**: Python 3.8+

---

## Soporte

Para más información consulta:
- Código fuente: `src/logger/pretty.py`
- Ejemplo completo: `consolidate_excel.py`
- Sistema de logging: `docs/LOGGING_CONFIGURATION.md`
