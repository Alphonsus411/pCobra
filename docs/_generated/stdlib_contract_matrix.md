# Contrato de stdlib Cobra (autogenerado)

Este documento se genera desde `src/pcobra/cobra/stdlib_contract/*.py`.

## `cobra.core`

- **Backend primario:** `python`
- **Fallback permitido:** `rust, javascript`
- **Mapeo `standard_library`:** `src/pcobra/standard_library/util.py`
- **Mapeo `corelibs`:** `src/pcobra/corelibs/numero.py`
- **Mapeo `core/nativos`:** `src/pcobra/core/nativos/numero.js`

### API pública

- `cobra.core.lex`
- `cobra.core.parse`
- `cobra.core.ast`

### Cobertura por función

| Función | Backend | Nivel |
|---|---|---|
| `cobra.core.lex` | `python` | `full` |
| `cobra.core.lex` | `rust` | `partial` |
| `cobra.core.lex` | `javascript` | `full` |
| `cobra.core.parse` | `python` | `full` |
| `cobra.core.parse` | `rust` | `partial` |
| `cobra.core.parse` | `javascript` | `partial` |
| `cobra.core.ast` | `python` | `full` |
| `cobra.core.ast` | `rust` | `partial` |
| `cobra.core.ast` | `javascript` | `partial` |

## `cobra.datos`

- **Backend primario:** `python`
- **Fallback permitido:** `javascript`
- **Mapeo `standard_library`:** `src/pcobra/standard_library/datos.py`
- **Mapeo `corelibs`:** `src/pcobra/corelibs/coleccion.py`
- **Mapeo `core/nativos`:** `src/pcobra/core/nativos/datos.js`

### API pública

- `cobra.datos.tabla`
- `cobra.datos.csv`
- `cobra.datos.json`

### Cobertura por función

| Función | Backend | Nivel |
|---|---|---|
| `cobra.datos.tabla` | `python` | `full` |
| `cobra.datos.tabla` | `javascript` | `partial` |
| `cobra.datos.csv` | `python` | `full` |
| `cobra.datos.csv` | `javascript` | `partial` |
| `cobra.datos.json` | `python` | `full` |
| `cobra.datos.json` | `javascript` | `full` |

## `cobra.web`

- **Backend primario:** `javascript`
- **Fallback permitido:** `python`
- **Mapeo `standard_library`:** `src/pcobra/standard_library/interfaz.py`
- **Mapeo `corelibs`:** `src/pcobra/corelibs/red.py`
- **Mapeo `core/nativos`:** `src/pcobra/core/nativos/red.js`

### API pública

- `cobra.web.http`
- `cobra.web.router`
- `cobra.web.sse`

### Cobertura por función

| Función | Backend | Nivel |
|---|---|---|
| `cobra.web.http` | `javascript` | `full` |
| `cobra.web.http` | `python` | `partial` |
| `cobra.web.router` | `javascript` | `full` |
| `cobra.web.router` | `python` | `partial` |
| `cobra.web.sse` | `javascript` | `full` |
| `cobra.web.sse` | `python` | `partial` |

## `cobra.system`

- **Backend primario:** `rust`
- **Fallback permitido:** `python`
- **Mapeo `standard_library`:** `src/pcobra/standard_library/archivo.py`
- **Mapeo `corelibs`:** `src/pcobra/corelibs/sistema.py`
- **Mapeo `core/nativos`:** `src/pcobra/core/nativos/sistema.js`

### API pública

- `cobra.system.fs`
- `cobra.system.proc`
- `cobra.system.env`

### Cobertura por función

| Función | Backend | Nivel |
|---|---|---|
| `cobra.system.fs` | `rust` | `full` |
| `cobra.system.fs` | `python` | `full` |
| `cobra.system.proc` | `rust` | `full` |
| `cobra.system.proc` | `python` | `partial` |
| `cobra.system.env` | `rust` | `full` |
| `cobra.system.env` | `python` | `full` |
