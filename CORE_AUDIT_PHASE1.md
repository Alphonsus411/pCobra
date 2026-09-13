# Auditoría del core — Fase 1

# 1. Alcance y método

Esta fase fija una línea base reproducible del repositorio sin corregir
hallazgos. No se modificaron producción, Lexer, Parser, pruebas existentes,
ejemplos ni la documentación normativa. Las salidas completas se conservan en
`audit_evidence/phase1/`.

# 2. SHA auditado

- **SHA:** `21ff2307a1fa027156b2b4657c6baef7bfdc1a83`.
- **Rama y estado inicial:** `## work`, sin cambios listados por
  `git status --short --branch`.
- **Python:** `Python 3.12.13`.
- **Plataforma reportada por Python:**
  `Linux-6.18.44-x86_64-with-glibc2.39`.
- Estos datos se capturaron antes de modificar cualquier archivo.

# 3. Baseline

## 3.1 Comando oficial y variantes encontradas

El comando oficial anunciado por `Makefile` es `make test`. Su target ejecuta,
en este orden:

1. `python scripts/grammar_coverage.py --threshold=30` (el umbral se puede
   variar con `GRAMMAR_COV`).
2. `pytest --cov=src/pcobra tests --cov-report=term-missing --cov-fail-under=90`.

Variantes presentes en el repositorio:

- `make coverage`: `coverage run -m pytest` y después `coverage html`.
- `bash scripts/test.sh [argumentos]`: antepone `$PWD/src:$PWD` a
  `PYTHONPATH` y delega en `pytest`. El archivo no tiene permiso de ejecución
  en este checkout, por lo que la forma documentada `./scripts/test.sh` falla.
- `PYTHONPATH=$PWD/src pytest` y `PYTHONPATH=$PWD/src pytest --cov`, descritos
  en `CONTRIBUTING.md`.
- El `README.md` también conserva variantes directas con umbral de cobertura
  95 %, `PYTHONPATH=$PWD pytest`, `pytest --cov=pcobra tests/`, suites
  específicas y `python scripts/check.py` para el pipeline ampliado. Por tanto,
  esas referencias no son idénticas al target vigente de `Makefile`.

La configuración común de pytest en `pyproject.toml` limita la búsqueda a
`tests`, nombres `test_*.py`, clases `Test*` y funciones `test_*`; activa
marcadores estrictos, traceback corto, captura `fd`, toda la captura y las diez
pruebas más lentas.

## 3.2 Colección previa

Comando efectivo: `bash scripts/test.sh --collect-only`.

- **Collected:** 4977 items.
- **Passed / failed / xfailed / xpassed:** no aplican a `--collect-only` (no se
  ejecutaron casos).
- **Skipped durante colección:** 3.
- **Warnings:** 3.
- **Duración:** 14.90 s.
- **Errores de colección:** 0.
- **Código de salida:** 0.

Incidencia previa: el primer intento literal, `./scripts/test.sh
--collect-only`, terminó con código 126 y `Permission denied`; no llegó a
invocar pytest. La evidencia íntegra de la colección efectiva está en
`audit_evidence/phase1/pytest-collection.log`.

## 3.3 Suite oficial completa

`make test` **no llegó a ejecutar pytest**: el primer paso informó cobertura de
gramática **0.00 % (0/42)**, inferior al umbral **30.00 %**, y `make` terminó
con código 2. En consecuencia, para esa invocación oficial:

- **Passed / failed / skipped / xfailed / xpassed / warnings de pytest:** no
  disponibles, porque pytest no arrancó.
- **Errores de colección:** no aplican.
- **Duración de pytest:** no aplica.

La salida completa está en `audit_evidence/phase1/make-test.log`.

La segunda orden exacta del target se ejecutó aisladamente para diagnosticar el
bloqueo. Pytest terminó con código 4 antes de colección porque el entorno no
reconoce `--cov`, `--cov-report` ni `--cov-fail-under` (plugin `pytest-cov` no
disponible). Su salida se conserva en
`audit_evidence/phase1/pytest-official-command.log`.

Como observación adicional se lanzó la variante sin cobertura
`bash scripts/test.sh`. Recopiló 4977 items con 3 omisiones, alcanzó el 22 % y
quedó bloqueada al comenzar `tests/test_interactive_cmd_no_console.py`; se
interrumpió manualmente y terminó con código 1. Al no emitir resumen final,
**no es posible registrar cifras exactas** de passed, failed, skipped, xfailed,
xpassed, warnings o duración para esa ejecución, y no se infieren cifras a
partir de los puntos de progreso. La salida completa disponible está en
`audit_evidence/phase1/pytest-full-interrupted.log`.

Todos estos fallos se observaron sobre el SHA inicial, antes de crear este
informe; se registran expresamente como **fallos previos del baseline** y no
como regresiones introducidas por la auditoría.

# 4. Arquitectura relevante encontrada

- El proyecto usa layout `src`; el paquete principal es `src/pcobra` y las
  pruebas se concentran en `tests`.
- La entrada de consola `cobra` declarada en `pyproject.toml` apunta a
  `pcobra.cli:main`; esta fachada coordina la CLI pública.
- La implementación principal se organiza bajo `src/pcobra/cobra`, con capas
  separadas para CLI, pipeline de ejecución, core, backends, transpiladores,
  imports, configuración, GUI, QA y contratos de biblioteca estándar.
- También existen superficies en `src/pcobra/core`, `src/pcobra/corelibs` y
  `src/pcobra/standard_library`, además de integraciones GUI, LSP y Jupyter.
- Los Lexer y Parser canónicos inspeccionados están en
  `src/pcobra/cobra/core/lexer.py` y `src/pcobra/cobra/core/parser.py`. Quedan
  explícitamente fuera del alcance de modificación de esta fase.
- El contrato normativo de sintaxis y comportamiento continúa siendo
  `docs/LIBRO_PROGRAMACION_COBRA.md`.
- La validación oficial no es una única invocación de pytest: `make test`
  antepone un gate de cobertura gramatical, mientras que `make check` agrega
  smoke tests, lint, tipos y validación del contrato de runtime.

# 5. Hallazgos pendientes

Pendiente para fases posteriores; esta fase solo establece el baseline.

# 6. Cambios y exclusiones

Únicamente se añaden este informe y los registros de evidencia. No se modifica
código de producción, Lexer, Parser, pruebas, ejemplos ni documentación
normativa.
