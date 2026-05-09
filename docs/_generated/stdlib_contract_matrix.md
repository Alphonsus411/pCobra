# Matriz única de stdlib Cobra (autogenerado)

Este documento se genera desde `src/pcobra/cobra/stdlib_contract/*.py`.

## Tabla de garantías por módulo

| Módulo | API pública | Backend primario | Fallback | Límites |
|---|---|---|---|---|
| `cobra.core` | 4 | `python` | `rust, javascript` | es_finito:rust, es_finito:javascript, es_infinito:rust, es_infinito:javascript, copiar_signo:rust, copiar_signo:javascript, signo:rust, signo:javascript |
| `cobra.datos` | 4 | `python` | `javascript` | filtrar:javascript, seleccionar_columnas:javascript, a_listas:javascript, de_listas:javascript |
| `cobra.web` | 4 | `javascript` | `python` | obtener_url:javascript, enviar_post:javascript, descargar_archivo:javascript, obtener_url_texto:javascript |
| `cobra.system` | 11 | `python` | `rust, javascript` | leer:rust, leer:javascript, escribir:rust, escribir:javascript, adjuntar:rust, adjuntar:javascript, existe:rust, existe:javascript, ejecutar:rust, ejecutar:javascript, ejecutar_comando_async:rust, ejecutar_comando_async:javascript, obtener_env:rust, obtener_env:javascript, listar_dir:rust, listar_dir:javascript, ahora:rust, ahora:javascript, formatear:rust, formatear:javascript, dormir:rust, dormir:javascript |

## `cobra.core`

- **Backend primario:** `python`
- **Fallback permitido:** `rust, javascript`
- **Mapeo `standard_library`:** `src/pcobra/standard_library/numero.py`
- **Mapeo `corelibs`:** `src/pcobra/corelibs/numero.py`
- **Mapeo `core/nativos`:** `src/pcobra/core/nativos/numero.js`

### API pública

- `cobra.core.es_finito`
- `cobra.core.es_infinito`
- `cobra.core.copiar_signo`
- `cobra.core.signo`

### Exportaciones públicas (alias Cobra estables)

| Alias Cobra | Módulo runtime trazable |
|---|---|
| `cobra.core.es_finito` | `src/pcobra/standard_library/numero.py` |
| `cobra.core.es_infinito` | `src/pcobra/standard_library/numero.py` |
| `cobra.core.copiar_signo` | `src/pcobra/standard_library/numero.py` |
| `cobra.core.signo` | `src/pcobra/standard_library/numero.py` |

### Cobertura por función

| Función | Backend | Nivel |
|---|---|---|
| `cobra.core.es_finito` | `python` | `full` |
| `cobra.core.es_finito` | `rust` | `partial` |
| `cobra.core.es_finito` | `javascript` | `partial` |
| `cobra.core.es_infinito` | `python` | `full` |
| `cobra.core.es_infinito` | `rust` | `partial` |
| `cobra.core.es_infinito` | `javascript` | `partial` |
| `cobra.core.copiar_signo` | `python` | `full` |
| `cobra.core.copiar_signo` | `rust` | `partial` |
| `cobra.core.copiar_signo` | `javascript` | `partial` |
| `cobra.core.signo` | `python` | `full` |
| `cobra.core.signo` | `rust` | `partial` |
| `cobra.core.signo` | `javascript` | `partial` |

## `cobra.datos`

- **Backend primario:** `python`
- **Fallback permitido:** `javascript`
- **Mapeo `standard_library`:** `src/pcobra/standard_library/datos.py`
- **Mapeo `corelibs`:** `src/pcobra/corelibs/coleccion.py`
- **Mapeo `core/nativos`:** `src/pcobra/core/nativos/datos.js`

### API pública

- `cobra.datos.filtrar`
- `cobra.datos.seleccionar_columnas`
- `cobra.datos.a_listas`
- `cobra.datos.de_listas`

### Exportaciones públicas (alias Cobra estables)

| Alias Cobra | Módulo runtime trazable |
|---|---|
| `cobra.datos.filtrar` | `src/pcobra/standard_library/datos.py` |
| `cobra.datos.seleccionar_columnas` | `src/pcobra/standard_library/datos.py` |
| `cobra.datos.a_listas` | `src/pcobra/standard_library/datos.py` |
| `cobra.datos.de_listas` | `src/pcobra/standard_library/datos.py` |

### Cobertura por función

| Función | Backend | Nivel |
|---|---|---|
| `cobra.datos.filtrar` | `python` | `full` |
| `cobra.datos.filtrar` | `javascript` | `partial` |
| `cobra.datos.seleccionar_columnas` | `python` | `full` |
| `cobra.datos.seleccionar_columnas` | `javascript` | `partial` |
| `cobra.datos.a_listas` | `python` | `full` |
| `cobra.datos.a_listas` | `javascript` | `partial` |
| `cobra.datos.de_listas` | `python` | `full` |
| `cobra.datos.de_listas` | `javascript` | `partial` |

## `cobra.web`

- **Backend primario:** `javascript`
- **Fallback permitido:** `python`
- **Mapeo `standard_library`:** -
- **Mapeo `corelibs`:** `src/pcobra/corelibs/red.py`
- **Mapeo `core/nativos`:** `src/pcobra/core/nativos/red.js`

### API pública

- `cobra.web.obtener_url`
- `cobra.web.enviar_post`
- `cobra.web.descargar_archivo`
- `cobra.web.obtener_url_texto`

### Exportaciones públicas (alias Cobra estables)

| Alias Cobra | Módulo runtime trazable |
|---|---|
| `cobra.web.obtener_url` | `src/pcobra/corelibs/red.py` |
| `cobra.web.enviar_post` | `src/pcobra/corelibs/red.py` |
| `cobra.web.descargar_archivo` | `src/pcobra/corelibs/red.py` |
| `cobra.web.obtener_url_texto` | `src/pcobra/corelibs/red.py` |

### Cobertura por función

| Función | Backend | Nivel |
|---|---|---|
| `cobra.web.obtener_url` | `javascript` | `partial` |
| `cobra.web.obtener_url` | `python` | `full` |
| `cobra.web.enviar_post` | `javascript` | `partial` |
| `cobra.web.enviar_post` | `python` | `full` |
| `cobra.web.descargar_archivo` | `javascript` | `partial` |
| `cobra.web.descargar_archivo` | `python` | `full` |
| `cobra.web.obtener_url_texto` | `javascript` | `partial` |
| `cobra.web.obtener_url_texto` | `python` | `full` |

## `cobra.system`

- **Backend primario:** `python`
- **Fallback permitido:** `rust, javascript`
- **Mapeo `standard_library`:** `src/pcobra/standard_library/archivo.py`
- **Mapeo `corelibs`:** `src/pcobra/corelibs/sistema.py`, `src/pcobra/corelibs/tiempo.py`
- **Mapeo `core/nativos`:** `src/pcobra/core/nativos/sistema.js`

### API pública

- `cobra.system.leer`
- `cobra.system.escribir`
- `cobra.system.adjuntar`
- `cobra.system.existe`
- `cobra.system.ejecutar`
- `cobra.system.ejecutar_comando_async`
- `cobra.system.obtener_env`
- `cobra.system.listar_dir`
- `cobra.system.ahora`
- `cobra.system.formatear`
- `cobra.system.dormir`

### Exportaciones públicas (alias Cobra estables)

| Alias Cobra | Módulo runtime trazable |
|---|---|
| `cobra.system.leer` | `src/pcobra/standard_library/archivo.py` |
| `cobra.system.escribir` | `src/pcobra/standard_library/archivo.py` |
| `cobra.system.adjuntar` | `src/pcobra/standard_library/archivo.py` |
| `cobra.system.existe` | `src/pcobra/standard_library/archivo.py` |
| `cobra.system.ejecutar` | `src/pcobra/corelibs/sistema.py` |
| `cobra.system.ejecutar_comando_async` | `src/pcobra/corelibs/sistema.py` |
| `cobra.system.obtener_env` | `src/pcobra/corelibs/sistema.py` |
| `cobra.system.listar_dir` | `src/pcobra/corelibs/sistema.py` |
| `cobra.system.ahora` | `src/pcobra/corelibs/tiempo.py` |
| `cobra.system.formatear` | `src/pcobra/corelibs/tiempo.py` |
| `cobra.system.dormir` | `src/pcobra/corelibs/tiempo.py` |

### Cobertura por función

| Función | Backend | Nivel |
|---|---|---|
| `cobra.system.leer` | `python` | `full` |
| `cobra.system.leer` | `rust` | `partial` |
| `cobra.system.leer` | `javascript` | `partial` |
| `cobra.system.escribir` | `python` | `full` |
| `cobra.system.escribir` | `rust` | `partial` |
| `cobra.system.escribir` | `javascript` | `partial` |
| `cobra.system.adjuntar` | `python` | `full` |
| `cobra.system.adjuntar` | `rust` | `partial` |
| `cobra.system.adjuntar` | `javascript` | `partial` |
| `cobra.system.existe` | `python` | `full` |
| `cobra.system.existe` | `rust` | `partial` |
| `cobra.system.existe` | `javascript` | `partial` |
| `cobra.system.ejecutar` | `python` | `full` |
| `cobra.system.ejecutar` | `rust` | `partial` |
| `cobra.system.ejecutar` | `javascript` | `partial` |
| `cobra.system.ejecutar_comando_async` | `python` | `full` |
| `cobra.system.ejecutar_comando_async` | `rust` | `partial` |
| `cobra.system.ejecutar_comando_async` | `javascript` | `partial` |
| `cobra.system.obtener_env` | `python` | `full` |
| `cobra.system.obtener_env` | `rust` | `partial` |
| `cobra.system.obtener_env` | `javascript` | `partial` |
| `cobra.system.listar_dir` | `python` | `full` |
| `cobra.system.listar_dir` | `rust` | `partial` |
| `cobra.system.listar_dir` | `javascript` | `partial` |
| `cobra.system.ahora` | `python` | `full` |
| `cobra.system.ahora` | `rust` | `partial` |
| `cobra.system.ahora` | `javascript` | `partial` |
| `cobra.system.formatear` | `python` | `full` |
| `cobra.system.formatear` | `rust` | `partial` |
| `cobra.system.formatear` | `javascript` | `partial` |
| `cobra.system.dormir` | `python` | `full` |
| `cobra.system.dormir` | `rust` | `partial` |
| `cobra.system.dormir` | `javascript` | `partial` |
