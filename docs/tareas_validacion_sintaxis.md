# Validación de sintaxis y plan de implementación (Cobra)

Fecha de ejecución: 2026-04-01 (UTC)

## 1) Pruebas ejecutadas paso a paso

### Paso 1 — Suite general rápida
Comando ejecutado:

```bash
pytest -q
```

Resultado:
- Estado: **falló** con 5 tests en rojo antes del corte por `--maxfail`.
- Resumen observado: 5 failed, 22 passed, 3 skipped.

Principales causas detectadas:
1. Dependencias opcionales ausentes para transpilación inversa (`tree_sitter_languages`).
2. Error de recarga/import en `cache_cmd` (`module ... not in sys.modules`).
3. Inconsistencia en el texto de ayuda de CLI respecto a la cadena esperada por tests.
4. Binario `cobra` no disponible en PATH en este entorno de ejecución.

---

### Paso 2 — Núcleo de sintaxis (lexer/parser/transpiladores)
Comando ejecutado:

```bash
pytest -q tests/test_lexer.py tests/test_parser.py tests/test_transpilers.py
```

Resultado:
- Estado: **correcto**.
- Resumen observado: **11 passed**.

Interpretación:
- El núcleo de análisis léxico/sintáctico y cobertura base de transpilación funciona correctamente en este entorno.

---

### Paso 3 — Validación de ejemplos de entrada/salida
Comando ejecutado:

```bash
pytest -q tests/test_ejemplos_io.py
```

Resultado:
- Estado: **falló** con 5 tests en rojo (4 de ejecución + 1 de transpilación).
- Se observan errores de ejecución genérica en comando `ejecutar` y una recursión máxima excedida al transpilar el ejemplo `factorial_recursivo`.

Interpretación:
- Existen regresiones en flujo end-to-end sobre ejemplos concretos, pese a que lexer/parser unitarios pasan.

## 2) Diagnóstico consolidado

- **Sintaxis base**: validada con éxito en pruebas unitarias directas (lexer/parser).
- **Flujo CLI e integración**: hay fallos pendientes (entorno + posibles regresiones funcionales).
- **Objetivo inmediato**: estabilizar primero entorno/CLI, luego flujo de ejecución/transpilación end-to-end.

## 3) Tareas estructuradas para implementar

## Bloque A — Entorno y dependencias

### Tarea A1 — Dependencias opcionales de reverse transpilation
- Objetivo: habilitar `ReverseFromJava` y `ReverseFromJS` en CI/local.
- Implementación:
  1. Añadir extras de instalación (si no están) para `tree-sitter` y `tree-sitter-languages`.
  2. Documentar instalación en guía de contribución.
  3. Asegurar que los tests de reverse se marquen como `skip` explícito cuando no estén presentes.
- Criterio de aceptación:
  - `tests/integration/reverse/test_from_java.py` y `test_from_js.py` pasan o quedan en skip explícito y justificado.

### Tarea A2 — Exposición del comando `cobra` en entorno de pruebas
- Objetivo: evitar `FileNotFoundError: cobra`.
- Implementación:
  1. Ejecutar tests CLI vía `python -m pcobra.cli` o instalar editable (`pip install -e .`).
  2. Ajustar test de integración para no depender de PATH global no garantizado.
- Criterio de aceptación:
  - `tests/integration/test_cli_import.py::test_cli_import_help` pasa en entorno limpio.

## Bloque B — Robustez de CLI

### Tarea B1 — Corrección de recarga de módulos en `cache_cmd`
- Objetivo: resolver `ImportError` de `importlib.reload`.
- Implementación:
  1. Revisar estrategia de import/reload en `tests/integration/test_cli.py` y `cobra.cli.commands.cache_cmd`.
  2. Garantizar registro consistente del módulo en `sys.modules`.
- Criterio de aceptación:
  - `test_cache_command_clears_database` pasa sin hacks de entorno.

### Tarea B2 — Alinear help de `compilar` con contrato de texto
- Objetivo: normalizar cadena esperada de tiers (`Tier 1... Tier 2...`).
- Implementación:
  1. Revisar formateo actual del `--help`.
  2. Decidir si se actualiza mensaje CLI o expectativa del test para evitar fragilidad por cambios menores de estilo.
- Criterio de aceptación:
  - `test_cobra_compilar_help_muestra_exactamente_8_targets_canonicos_por_tier` pasa de forma estable.

## Bloque C — Ejecución y transpilación end-to-end

### Tarea C1 — Debug del comando `ejecutar` en ejemplos
- Objetivo: corregir errores genéricos al ejecutar `.co`/`.cobra`.
- Implementación:
  1. Trazar excepción real detrás de `Error ejecutando el script:`.
  2. Añadir logging controlado o propagación de excepción en modo test.
  3. Corregir nodo/visitor/fase donde falla runtime.
- Criterio de aceptación:
  - `test_ejecutar_ejemplos[...]` en verde para casos `ejemplo`, `factorial_recursivo`, `suma`, `suma_matrices`.

### Tarea C2 — Recursión infinita en transpilación de factorial
- Objetivo: eliminar `maximum recursion depth exceeded`.
- Implementación:
  1. Reproducir con fixture mínima.
  2. Inspeccionar visitor/AST transform pipeline para llamadas recursivas.
  3. Añadir prueba de no-regresión.
- Criterio de aceptación:
  - `test_transpilar_muestra_fragmentos[factorial_recursivo]` en verde.

## Bloque D — Gobernanza de calidad

### Tarea D1 — Pipeline por capas
- Objetivo: feedback más rápido en CI.
- Implementación:
  1. Etapa 1: unit sintaxis (`lexer/parser/transpilers`), obligatoria.
  2. Etapa 2: integración CLI.
  3. Etapa 3: ejemplos e2e.
- Criterio de aceptación:
  - reporte CI separa claramente fallos de sintaxis base vs fallos e2e.

### Tarea D2 — Matriz de soporte de entorno de tests
- Objetivo: eliminar falsos negativos por entorno incompleto.
- Implementación:
  1. Definir variables/requisitos mínimos por suite (`SQLITE_DB_KEY`, extras opcionales, PATH CLI).
  2. Publicar guía corta en docs para reproducibilidad local.
- Criterio de aceptación:
  - contribuidor nuevo puede reproducir >95% de suites sin fricción.

## 4) Orden recomendado de ejecución

1. **A2** (CLI en PATH / estrategia de invocación)
2. **A1** (dependencias reverse)
3. **B1** y **B2** (estabilidad CLI)
4. **C1** y **C2** (regresiones funcionales e2e)
5. **D1** y **D2** (endurecimiento continuo)

## 5) Definición de “sintaxis validada” para este ciclo

Se considerará que la sintaxis está validada para este ciclo cuando:

- `tests/test_lexer.py` y `tests/test_parser.py` estén en verde.
- Los tests de transpilación base estén en verde.
- No existan fallos de CLI atribuibles a entorno en el pipeline principal.

## 6) Perfiles operativos de validación (CLI + pipelines)

Para separar pipelines rápidos y completos, `validar-sintaxis` y `scripts/check.py`
quedan alineados en tres perfiles:

- `solo-cobra`: validación rápida (Python + parse Cobra).
- `transpiladores`: valida exclusivamente sintaxis de backends.
- `completo`: ejecuta todo.

Ejemplos recomendados:

```bash
# Perfil rápido para PRs tempranos
cobra validar-sintaxis --perfil solo-cobra
python scripts/check.py --perfil rapido

# Perfil dedicado a backends/transpiladores
cobra validar-sintaxis --perfil transpiladores --targets=python,javascript,rust
python scripts/check.py --perfil transpiladores

# Perfil completo para release o merge final
cobra validar-sintaxis --perfil completo --strict --report-json reporte_sintaxis.json
python scripts/check.py --perfil completo
```

Compatibilidad:
- `--solo-cobra` se mantiene como alias deprecado de `--perfil solo-cobra`.
