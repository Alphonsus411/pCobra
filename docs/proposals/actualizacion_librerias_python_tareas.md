# Tareas estructuradas para actualizar librerías Python del proyecto

## Objetivo

Este documento convierte la revisión de dependencias Python en un plan de
implementación paso a paso para actualizar el proyecto a versiones actuales de
sus librerías, manteniendo estable el lenguaje Cobra.

La actualización debe cubrir:

1. dependencias runtime declaradas en `pyproject.toml`;
2. extras opcionales (`excel`, `columnar`, `io-binary`, `lsp`, `ml`,
   `big-data`, `notebooks`, `docs`, `dev`);
3. archivos compilados con `pip-compile` (`requirements.txt`,
   `requirements-dev.txt`, `docs/requirements.txt`);
4. integración con GUI, IA, datos, documentación y herramientas de calidad;
5. validación automática suficiente para detectar regresiones.

> **Regla de alcance obligatoria**
>
> Esta iniciativa **no debe cambiar el Lexer, no debe cambiar el Parser y no
> debe inventar reglas de sintaxis Cobra**. Si una dependencia nueva provoca un
> fallo relacionado con sintaxis, el trabajo debe corregirse en capas de
> integración, tooling, configuración, mensajes o tests, no ampliando la
> gramática del lenguaje.

## Fuente de verdad inicial

Antes de implementar cualquier ticket, leer y respetar estos puntos:

- `pyproject.toml`: fuente canónica de dependencias directas, extras y
  configuración de herramientas.
- `requirements.txt`: lock runtime generado desde `pyproject.toml`.
- `requirements-dev.txt`: lock de desarrollo generado desde el extra `dev`.
- `docs/requirements.txt`: lock documental generado desde el extra `docs`.
- `scripts/sync_requirements.sh`: flujo existente para regenerar locks con
  `pip-compile`.
- `scripts/check_requirements_drift.sh`: comprobación de drift de locks.
- `src/pcobra/standard_library/datos.py`: integración de datos, Excel y
  formatos columnares.
- `src/pcobra/gui/`: integración GUI basada en Flet.
- `src/pcobra/ia/analizador_agix.py`: integración con AGIX.
- `src/pcobra/core/interpreter.py`: uso de `RestrictedPython`.
- `src/pcobra/core/pybind_bridge.py`: uso de `pybind11`.
- `src/pcobra/cobra/transpilers/reverse/`: integración con `tree-sitter` en
  transpilación inversa.

## Política operativa para toda la iniciativa

- Verificar en PyPI las versiones actuales justo antes de implementar. Las
  versiones “últimas” son temporales y no deben copiarse sin comprobación.
- Preferir rangos compatibles y razonados frente a pines exactos, salvo cuando
  la dependencia ya requiera pin por seguridad o compatibilidad.
- Mantener los extras opcionales como opcionales; no convertir dependencias
  pesadas en requisitos runtime si el módulo ya soporta degradación controlada.
- Regenerar locks con herramientas del repositorio, no editarlos a mano salvo
  para corregir metadatos claramente generados de forma incorrecta.
- Cada ticket debe terminar con evidencias: comando ejecutado, resultado y
  archivos afectados.
- Si un ticket descubre incompatibilidades mayores, documentar el bloqueo y
  abrir una subtarea explícita en vez de ocultar el problema relajando tests.

## Estado operativo global

- **Estado actual del programa**: pendiente de implementación.
- **Responsable sugerido**: equipo de mantenimiento Python/CI.
- **Dependencia macro**: decisión de matriz Python soportada antes de cerrar la
  actualización completa.
- **Criterio global de cierre**: dependencias directas y locks actualizados,
  pruebas críticas en verde, documentación sincronizada, sin cambios en Lexer,
  Parser ni sintaxis Cobra.

---

## Tickets de implementación

> Convención de estados sugerida por ticket:
>
> - `Pendiente`: sin cambios implementados aún.
> - `En curso`: existe diff parcial o investigación activa.
> - `Bloqueado`: falta decisión, compatibilidad upstream o dependencia previa.
> - `Cerrado`: criterio verificable cumplido con evidencias.

### Ticket A1 — Inventariar versiones actuales y matriz Python soportada

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo mantenimiento Python |
| Dependencias | Ninguna; bloquea decisiones de rangos |
| Archivos a revisar | `pyproject.toml`, `.github/workflows/test.yml`, `.github/workflows/pages.yml`, `.github/workflows/codeql.yml` |
| Validaciones reales | `python -m pip index versions <paquete>` o consulta equivalente a PyPI; `python - <<'PY' ...` para revisar metadatos `Requires-Python` |
| Criterio de cierre verificable | Existe una tabla de decisión con versión actual, `Requires-Python`, rango propuesto y motivo para cada dependencia directa y extra. |

**Trabajo esperado**

- Consultar PyPI para todas las dependencias directas y extras del proyecto.
- Registrar si cada versión actual mantiene soporte para Python 3.9, 3.10, 3.11
  y 3.12.
- Decidir si `requires-python = ">=3.9"` sigue siendo viable o si el proyecto
  debe elevar su mínimo soportado.
- Revisar los clasificadores Python de `pyproject.toml` y la matriz de CI.
- Separar dependencias de runtime, documentación, desarrollo, ML y notebooks.

**Notas de implementación**

- Esta tarea no actualiza todavía el código: produce la decisión técnica que
  desbloquea los rangos.
- Si una dependencia actual exige Python superior al mínimo vigente, no forzar
  instalación incompatible; documentar la decisión de subir mínimo o mantener
  una versión anterior.

### Ticket A2 — Actualizar rangos directos en `pyproject.toml`

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo mantenimiento Python |
| Dependencias | A1 |
| Archivos a modificar | `pyproject.toml` |
| Validaciones reales | `python -m pip install -e . --dry-run` si la versión de pip lo permite; `python -m pip check` tras instalar en entorno limpio |
| Criterio de cierre verificable | `pyproject.toml` refleja rangos actualizados y coherentes con la matriz Python decidida, sin cambios en sintaxis Cobra. |

**Trabajo esperado**

- Actualizar dependencias científicas: `numpy`, `scipy`, `matplotlib`,
  `pandas`, `sympy`.
- Actualizar dependencias de integración: `agix`, `holobit-sdk`,
  `smooth-criminal`, `tree-sitter`, `pybind11`, `RestrictedPython`.
- Actualizar dependencias de CLI/configuración/red: `tomli`, `PyYAML`,
  `jsonschema`, `python-dotenv`, `pexpect`, `requests`, `packaging`,
  `prompt_toolkit`, `Pygments`, `argcomplete`, `httpx`, `rich`, `chardet`.
- Actualizar `flet` con revisión especial por salto de API.
- Mantener comentarios o documentación interna si un rango queda limitado por
  compatibilidad comprobada.

**Notas de implementación**

- No cambiar módulos de Lexer ni Parser aunque fallen tests cercanos a sintaxis.
- Evitar pines exactos nuevos salvo justificación explícita.

### Ticket A3 — Actualizar extras opcionales

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo mantenimiento Python |
| Dependencias | A1, A2 |
| Archivos a modificar | `pyproject.toml`, documentación de instalación si aplica |
| Validaciones reales | Instalaciones por extra: `python -m pip install -e .[excel]`, `python -m pip install -e .[columnar]`, `python -m pip install -e .[docs]`, `python -m pip install -e .[dev]` |
| Criterio de cierre verificable | Todos los extras declaran rangos actuales compatibles y siguen siendo opcionales. |

**Trabajo esperado**

- Actualizar `openpyxl` para `excel`.
- Actualizar `pyarrow` para `columnar` e `io-binary`.
- Actualizar `python-lsp-server` para `lsp`.
- Revisar `tensorflow` y `DEAP` en `ml`, validando especialmente plataforma y
  versión Python.
- Actualizar `dask` en `big-data`.
- Revisar si `mutpy` sigue mantenido; si no hay versión nueva, documentar el
  pin y el riesgo.
- Actualizar `papermill`, `nbconvert` e `ipykernel` en `notebooks`.
- Actualizar `sphinx`, `sphinx-rtd-theme`, `myst-parser` y
  `sphinxcontrib-plantuml` en `docs`.
- Actualizar `hypothesis`, `pytest`, `pytest-cov`, `pytest-timeout`, `ruff`,
  `mypy` y `pip-tools` en `dev`.

**Notas de implementación**

- Un extra no debe contaminar instalación base.
- Si un extra requiere Python más moderno que runtime, documentarlo con marker
  explícito.

### Ticket B1 — Regenerar locks con `pip-compile`

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo CI/release |
| Dependencias | A2, A3 |
| Archivos a modificar | `requirements.txt`, `requirements-dev.txt`, `docs/requirements.txt` |
| Scripts a usar | `scripts/sync_requirements.sh`, `scripts/check_requirements_drift.sh` |
| Validaciones reales | `./scripts/sync_requirements.sh --upgrade`; `./scripts/check_requirements_drift.sh` |
| Criterio de cierre verificable | Locks regenerados de forma reproducible y sin drift respecto a `pyproject.toml`. |

**Trabajo esperado**

- Ejecutar el script de sincronización con actualización completa.
- Revisar el diff de locks para detectar downgrades inesperados o paquetes
  transitorios conflictivos.
- Confirmar que los encabezados de `pip-compile` siguen apuntando al comando
  correcto.
- Ejecutar la comprobación de drift después de regenerar.

**Notas de implementación**

- No editar locks manualmente para “hacer pasar” drift.
- Si `pip-compile` falla por conflicto, volver a A2/A3 y ajustar rangos.

### Ticket B2 — Reproducibilidad de Binder y entornos auxiliares

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo documentación/infra |
| Dependencias | B1 |
| Archivos a revisar | `binder/requirements.txt`, scripts de instalación, workflows que instalan dependencias |
| Validaciones reales | `python -m pip install -r binder/requirements.txt --dry-run` si pip lo permite |
| Criterio de cierre verificable | Binder hereda locks actualizados y no introduce dependencias sin control cuando sea evitable. |

**Trabajo esperado**

- Evaluar si `jupyterlab` debe fijarse o acotarse en `binder/requirements.txt`.
- Revisar scripts de instalación que usen `requirements.txt` o
  `requirements-dev.txt`.
- Confirmar que la documentación de instalación no contradice los extras.

**Notas de implementación**

- Binder puede tener restricciones propias; si no se fija `jupyterlab`, dejar
  una justificación explícita.

### Ticket C1 — Compatibilidad de datos con NumPy, Pandas y PyArrow actuales

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo biblioteca estándar |
| Dependencias | A2, A3, B1 |
| Archivos a revisar | `src/pcobra/standard_library/datos.py`, `tests/unit/test_datos_public_contract.py`, tests de extras de datos |
| Validaciones reales | `python -m pytest tests/unit/test_datos_public_contract.py`; tests específicos de Excel/Parquet/Feather si existen o se añaden |
| Criterio de cierre verificable | La biblioteca de datos funciona con dependencias actuales y mantiene degradación controlada si extras no están instalados. |

**Trabajo esperado**

- Revisar compatibilidad de conversiones con NumPy 2 y Pandas 3.
- Validar que `pandas` no se vuelve obligatorio si el módulo promete operar sin
  esa dependencia.
- Probar lectura/escritura Excel con `openpyxl` actual.
- Probar lectura/escritura Parquet y Feather con `pyarrow` actual.
- Confirmar mensajes de error claros cuando faltan extras.

**Notas de implementación**

- Mantener la API pública de datos salvo incompatibilidad justificada.
- Añadir pruebas de contrato antes de refactorizar conversiones complejas.

### Ticket C2 — Migrar GUI a Flet actual

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo GUI/runtime |
| Dependencias | A2, B1 |
| Archivos a revisar | `src/pcobra/gui/runtime.py`, `src/pcobra/gui/app.py`, `src/pcobra/gui/idle.py`, `src/pcobra/standard_library/interfaz.py`, `tests/unit/test_gui_runtime.py` |
| Validaciones reales | `python -m pytest tests/unit/test_gui_runtime.py`; prueba manual o smoke test controlado de arranque Flet si el entorno lo permite |
| Criterio de cierre verificable | La GUI arranca o falla con mensaje explícito bajo Flet actual, sin romper importación de módulos headless. |

**Trabajo esperado**

- Revisar API de `ft.app`, `Page`, `TextField`, `Text`, `Dropdown`, opciones,
  `Switch`, botones y actualización de página.
- Mantener imports de Flet diferidos para no romper entornos sin GUI.
- Actualizar stubs o mocks de tests si cambian nombres de componentes.
- Documentar cualquier limitación de ejecución gráfica en CI.

**Notas de implementación**

- Si hay cambios visuales perceptibles en una app runnable, capturar evidencia
  visual cuando el entorno lo permita.

### Ticket C3 — Validar integraciones AGIX, Holobit y Smooth Criminal

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo IA/runtime |
| Dependencias | A2, B1 |
| Archivos a revisar | `src/pcobra/ia/analizador_agix.py`, `src/pcobra/core/performance.py`, documentación relacionada |
| Validaciones reales | Tests unitarios de IA/performance existentes; smoke tests de importación de módulos afectados |
| Criterio de cierre verificable | Las integraciones importan correctamente o degradan de forma explícita cuando la dependencia opcional no está disponible. |

**Trabajo esperado**

- Revisar rutas públicas de AGIX actuales frente a imports existentes.
- Validar llamadas y tipos usados por `analizador_agix.py`.
- Revisar API actual de `smooth-criminal` usada por `performance.py`.
- Confirmar mensajes de error si la dependencia no está instalada.

**Notas de implementación**

- No ocultar incompatibilidades con `except Exception` genéricos.
- No añadir try/catch alrededor de imports de forma innecesaria; seguir el
  patrón existente del proyecto y la guía de estilo.

### Ticket C4 — Validar RestrictedPython, pybind11 y tree-sitter

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo core/transpilación inversa |
| Dependencias | A2, B1 |
| Archivos a revisar | `src/pcobra/core/interpreter.py`, `src/pcobra/core/pybind_bridge.py`, `src/pcobra/cobra/transpilers/reverse/tree_sitter_base.py`, `src/pcobra/cobra/transpilers/reverse/from_js.py`, `src/pcobra/cobra/transpilers/reverse/from_java.py` |
| Validaciones reales | `python -m pytest tests/unit/test_restricted_exec.py`; tests de sandbox; tests de transpilación inversa relacionados |
| Criterio de cierre verificable | Sandbox, bridge nativo y transpilación inversa siguen funcionando con APIs actuales sin modificar sintaxis Cobra. |

**Trabajo esperado**

- Revisar imports y guards de `RestrictedPython`.
- Confirmar que la política de sandbox conserva restricciones existentes.
- Validar compatibilidad de `pybind11.setup_helpers` con la versión actual.
- Revisar API de `tree_sitter.Node`, `Tree` y carga de lenguajes.
- Ajustar únicamente adaptadores de integración; no tocar Lexer ni Parser.

**Notas de implementación**

- Cualquier cambio de seguridad requiere prueba negativa y positiva.
- Los cambios en tree-sitter pertenecen a reverse transpilers, no a la gramática
  principal de Cobra.

### Ticket D1 — Actualizar tooling de calidad y typing

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo QA/CI |
| Dependencias | A3, B1 |
| Archivos a revisar | `pyproject.toml`, `scripts/check.py`, `scripts/test.sh`, `.github/actions/install/action.yml`, `.github/workflows/test.yml` |
| Validaciones reales | `python -m ruff check src`; `python -m mypy src`; `python -m pytest -q` o subconjunto acordado |
| Criterio de cierre verificable | Ruff, mypy y pytest actuales ejecutan con configuración explícita y sin relajar cobertura crítica. |

**Trabajo esperado**

- Revisar cambios de configuración entre versiones actuales de Ruff y Mypy.
- Ajustar `target-version`, `exclude`, reglas o invocaciones solo si la versión
  nueva lo exige.
- Revisar cambios de Pytest 9 y plugins (`pytest-cov`, `pytest-timeout`).
- Mantener scripts de QA coherentes con workflows.

**Notas de implementación**

- No silenciar errores masivamente.
- Si aparecen errores antiguos por checks más estrictos, agrupar correcciones
  por módulo y documentar el motivo.

### Ticket D2 — Actualizar documentación con Sphinx y MyST actuales

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo documentación |
| Dependencias | A3, B1 |
| Archivos a revisar | `docs/conf.py`, `docs/frontend/conf.py`, `docs/requirements.txt`, `.github/workflows/pages.yml` |
| Validaciones reales | `python -m sphinx -b html docs docs/_build`; `python -m sphinx -b html docs/frontend docs/build/html` |
| Criterio de cierre verificable | La documentación compila con dependencias actuales sin warnings críticos nuevos. |

**Trabajo esperado**

- Revisar extensiones configuradas de Sphinx.
- Validar compatibilidad del tema `sphinx-rtd-theme` actual.
- Revisar cambios de `myst-parser` y warnings de sintaxis documental.
- Actualizar workflow de Pages si cambian comandos o dependencias.

**Notas de implementación**

- Los cambios de documentación no deben alterar reglas del lenguaje Cobra.
- Si hay warnings históricos no relacionados, separarlos de regresiones nuevas.

### Ticket E1 — Smoke tests de instalación y empaquetado

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo release |
| Dependencias | B1, C1-C4, D1-D2 |
| Archivos a revisar | `pyproject.toml`, `MANIFEST.in`, workflows de build, scripts de release |
| Validaciones reales | `python -m build`; `python -m pip install dist/*.whl`; `python -m pip check`; smoke de `cobra --help` |
| Criterio de cierre verificable | El paquete se construye, instala y expone la CLI con dependencias actualizadas. |

**Trabajo esperado**

- Construir wheel y sdist en entorno limpio.
- Instalar el wheel generado y ejecutar comprobaciones básicas de CLI.
- Verificar que extras siguen resolviendo.
- Confirmar que no se incluyen entornos virtuales, caches o artefactos locales.

**Notas de implementación**

- Ejecutar esta tarea al final, no antes de estabilizar locks y tests.

### Ticket E2 — Validación de no modificación de Lexer/Parser/sintaxis

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Revisor de release |
| Dependencias | Todos los tickets con cambios de código |
| Archivos a revisar | Diff completo del PR; módulos `lexer`, `parser`, gramáticas y tests de sintaxis |
| Validaciones reales | `git diff --name-only main...HEAD`; `python -m pytest tests/unit/test_lexer.py tests/unit/test_parser.py` si existen y son aplicables |
| Criterio de cierre verificable | El PR no modifica Lexer, Parser ni reglas de sintaxis; las pruebas de contrato existentes siguen pasando. |

**Trabajo esperado**

- Revisar que el diff no toca archivos de Lexer/Parser.
- Si se tocan tests de Parser/Lexer por compatibilidad externa, justificarlo y
  confirmar que no cambian reglas de lenguaje.
- Ejecutar suites mínimas de regresión de sintaxis para evidenciar estabilidad.
- Documentar explícitamente en el PR que la sintaxis Cobra no cambió.

**Notas de implementación**

- Este ticket es obligatorio antes de mergear la actualización completa.
- Si un cambio funcional necesita modificar Parser/Lexer, queda fuera de esta
  iniciativa y debe abrirse como propuesta separada.

---

## Orden recomendado de ejecución

1. A1 — Inventario y matriz Python.
2. A2/A3 — Actualización de rangos en `pyproject.toml`.
3. B1 — Regeneración de locks.
4. C1-C4 — Adaptaciones por dominio: datos, GUI, IA/core y reverse tooling.
5. D1-D2 — QA, typing y documentación.
6. B2 — Binder y entornos auxiliares, una vez estabilizados los locks.
7. E1 — Build, instalación y smoke tests.
8. E2 — Auditoría final de no modificación de Lexer/Parser/sintaxis.

## Evidencias mínimas para cerrar el programa

- `./scripts/sync_requirements.sh --upgrade`
- `./scripts/check_requirements_drift.sh`
- `python -m pytest tests/unit/test_datos_public_contract.py`
- `python -m pytest tests/unit/test_gui_runtime.py`
- `python -m pytest tests/unit/test_restricted_exec.py`
- `python -m ruff check src`
- `python -m mypy src`
- `python -m sphinx -b html docs docs/_build`
- `python -m build`
- `python -m pip check`
- Revisión manual del diff confirmando que no se modificaron Lexer, Parser ni
  reglas de sintaxis Cobra.
