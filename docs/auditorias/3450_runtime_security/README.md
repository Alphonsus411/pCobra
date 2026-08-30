# Auditoría focal de runtime, seguridad y distribución

## Referencias y colección

Se comparó el árbol actual `4fc8489a` con el baseline inmutable
`96d70b1ba00f07608b0fc2a780fca0e7d6b09257`, usando Python 3.12.13 y pytest
9.0.3. La colección global se enumeró con:

```console
python -m pytest --collect-only -q
```

Resultado: **4933 tests collected**. Los paths obtenidos se clasificaron por
nombre y por los marcadores mostrados por pytest en estas familias:

- filesystem/sandbox: `test_remediacion_runtime_contracts.py`,
  `test_sandbox*.py`, `test_security_sandbox.py`, `test_safe_mode*.py`;
- `usar`, REPL y paridad script: `test_usar*.py`,
  `test_repl*.py`, `test_run_repl_equivalence.py` y
  `test_parity_contract_run_vs_repl.py`;
- capacidades, procesos, red y descargas: `test_usar_symbol_policy.py`,
  `test_usar_{proceso,red}_capabilities.py`, `test*_proceso.py`, `test_red.py`
  y `test_red_descargar_archivo.py`;
- identidad AST y compatibilidad: `test_ast*.py`,
  `test_*compatibility*.py` y `test_runtime_imports_contract.py`;
- packaging: `test_packaging*.py`, `test_cobra_packaging.py`,
  `test_distribution_package_config.py` y `test_idle_packaging.py`;
- targets y documentación: `test_*target*.py`, `test_target*.py`,
  `test_public_docs_scope.py`, `test_official_targets_consistency.py` y
  `test_ci_audit_targets_contract.py`.

No hay marcadores temáticos propios para estas familias: los marcadores
recogidos son principalmente `integration`, `asyncio`, `timeout` y
`parametrize`; por ello la selección reproducible se hizo por node path.

## Baseline filesystem/REPL

El conjunto histórico equivalente al baseline descrito como «aproximadamente
116» es:

```console
python -m pytest --collect-only -q \
  tests/cli/test_repl_script_parity_contract.py \
  tests/integration/test_repl_usar_entrypoints_contract.py
python -m pytest -q \
  tests/cli/test_repl_script_parity_contract.py \
  tests/integration/test_repl_usar_entrypoints_contract.py
```

La colección exacta es **114**, tanto en current como en `96d70b1b`, y ambos
terminan con **114 passed, 2 warnings**. No existe variación entre árboles: la
diferencia de dos respecto de la cifra aproximada aportada es solo redondeo de
la descripción, no tests añadidos, retirados, saltados ni deseleccionados.

## Grupos focales separados

| Grupo | Selección | Current | Baseline | Diferencial |
|---|---|---:|---:|---|
| seguridad/capacidades | remediación runtime, policy por símbolo, capacidades proceso/red, sandbox y safe-mode imports | 164 passed, 2 failed | 164 passed, 2 failed | ninguno |
| procesos/red | corelibs proceso, aliases/capacidades, red y descarga | 63 passed, 2 failed | 63 passed, 2 failed | ninguno |
| AST identity/compatibility | identidad/imports AST, contratos AST, matrices de compatibilidad e imports runtime | 36 passed | 36 passed | ninguno |
| packaging | smoke, IDLE, metadata, manifest y configuración de distribución | 52 passed, 5 failed, 1 skipped | igual | ninguno |
| políticas/generación documental | policy/validación de targets, consistencia oficial, scope y snapshots documentales | 65 passed, 6 failed, 1 skipped | 64 passed, 7 failed, 1 skipped | una mejora |

Los dos fallos de safe-mode imports, los dos de proceso, los cinco de packaging
y seis fallos actuales de targets son exactamente los mismos node IDs que en
baseline. El único test que falla en baseline y pasa en current es
`test_snippets_generados_siguen_sincronizados_con_la_fuente_canonica`; no hay
ningún test que pase en baseline y falle en current.

`tests/unit/test_safe_mode.py` se comprobó además como path descubierto, pero
su ejecución aislada tiene un error histórico de colección al importar
`CliApplication` desde el shim raíz. Se separó del grupo ejecutable para no
ocultar ese error ni impedir que pytest ejecutara los demás casos. No se añadió
`skip`/`xfail` ni se modificó ninguna prueba.

## Controles de seguridad confirmados

- `TranspiladorPython` declara `safe_mode=True`, normaliza ese valor en la
  instancia y el test focal de generación verifica los valores predeterminado,
  explícitamente seguro y explícitamente inseguro. La inspección dinámica de
  la firma y de `TranspiladorPython().safe_mode` devolvió `True`; los seis casos
  focales pasaron.
- La matriz filesystem conserva capacidades por `(módulo, símbolo)` y exige
  decisión `allow` únicamente para wrappers confinados. Los casos prueban E/S
  dentro de `COBRA_IO_BASE_DIR`, traversal/objetivos externos y limpieza no
  confinada. No se observó permiso global ni escape nuevo.
- Los aliases `capturar`, `ejecutar_async` y `ejecutar_stream` heredan
  `process.spawn`; `shell=True` requiere autorización explícita incluso fuera
  de safe mode y se deniega en safe mode.
- Red y descargas conservan controles de capacidad, HTTPS/host, validación de
  cada redirección, límite de tamaño, escritura atómica y confinamiento del
  destino frente a rutas absolutas, traversal y symlinks salientes.
- Los destinos externos de filesystem y las operaciones de proceso/red se
  bloquean antes de operar en safe mode. Las pruebas focales no detectan
  relajación respecto del baseline.

## Integridad y restricciones

Esta auditoría no modifica runtime, Lexer, Parser, gramática, tokens ni tests.
Solo incorpora este registro reproducible. Se revisaron el diff final y
`git diff --check` para evitar cambios accidentales.

## Revalidación de la rama `fb1fe100` (2026-08-11)

Se reutilizaron las selecciones por paths descritas arriba, sin marcadores
temáticos. La comparación se repitió contra el mismo baseline inmutable
`96d70b1ba00f07608b0fc2a780fca0e7d6b09257` en un worktree separado. La pareja
REPL/script conservó exactamente **114 tests collected** y **114 passed, 2
warnings**:

```console
python -m pytest --collect-only -q tests/cli/test_repl_script_parity_contract.py tests/integration/test_repl_usar_entrypoints_contract.py
python -m pytest -q tests/cli/test_repl_script_parity_contract.py tests/integration/test_repl_usar_entrypoints_contract.py
```

Las familias se ejecutaron por separado expandiendo exclusivamente los paths
documentados. Los resultados actuales y sus nodeids se contrastaron con la
misma selección en baseline:

| Familia | Current | Baseline | Comparación por nodeid |
|---|---:|---:|---|
| seguridad/capacidades | 169 passed, 7 failed, 13 skipped | 168 passed, 8 failed, 13 skipped | ningún fallo nuevo; pasa ahora `test_js_detecta_reemplazo_binario` |
| filesystem/sandbox/safe mode focal | 106 passed, 2 failed | los dos nodeids ya fallan en baseline | sin regresión |
| procesos/red | 63 passed, 2 failed | 63 passed, 2 failed | mismos nodeids |
| AST identity/compatibility/runtime imports | 77 passed, 1 failed | 77 passed, 1 failed | mismo nodeid |
| packaging | 52 passed, 5 failed, 1 skipped | igual | mismos nodeids |
| políticas/documentación | 174 passed, 15 failed, 3 skipped | 171 passed, 16 failed, 3 skipped | ningún fallo nuevo; pasa ahora `test_snippets_generados_siguen_sincronizados_con_la_fuente_canonica`; el aumento neto de dos casos corresponde a pruebas añadidas |

Los fallos compartidos no se consideran verdes ni se atribuyen a esta rama.
En particular siguen compartidos los dos contratos históricos de imports en
safe mode, los dos de proceso, el contrato de copia de `NodoTipo`, los cinco de
packaging y los quince nodeids actuales de policy. Los cuatro fallos JavaScript
por ausencia de `vm2` también aparecen en baseline; el fallo compartido del
contrato de namespace de sandbox completa los siete actuales del grupo amplio.

La verificación explícita se ejecutó con el import canónico y devolvió
`TranspiladorPython().safe_mode = True`:

```console
python - <<'PY'
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython
value = TranspiladorPython().safe_mode
print(f"TranspiladorPython().safe_mode = {value!r}")
assert value is True
PY
```

Los casos aprobados de `test_remediacion_runtime_contracts.py`,
`test_usar_symbol_policy.py`, `test_sandbox_paths.py` y
`test_sandbox_restrictions.py` vuelven a confirmar la policy filesystem por
`(módulo, símbolo)`, el confinamiento mediante `COBRA_IO_BASE_DIR` y el rechazo
de traversal y symlinks externos. Los casos aprobados de proceso/red confirman
`process.spawn`, `capturar`, `ejecutar_async`, `ejecutar_stream`, la exigencia
de autorización de shell, HTTPS/host, validación de redirects, tamaño máximo,
destino confinado y escritura atómica. No hubo evidencia directa que
justificase modificar runtime o seguridad.

### Mecanismos reales de CI

Se ejecutaron individualmente los comandos usados por los workflows, y se
registraron también sus fallos actuales:

| Comando | Resultado |
|---|---|
| `python scripts/ci/validate_targets.py` | **pass**; policy oficial `python, javascript, rust` |
| `python scripts/validate_targets_policy.py` | **pass**; documentación pública de targets alineada |
| `python scripts/ci/check_manual_ref_generated.py` | **fail**; `docs/MANUAL_COBRA.rst` está desincronizado con su fuente (el archivo generado durante el check se restauró) |
| `python scripts/ci/validate_public_docs_version.py` | **fail**; no encuentra versión pública en `docs/guia_basica.md` |
| `python scripts/ci/validate_syntax_report_contract.py` | **fail**; falta `tests/data/snapshots/validar_sintaxis_report_schema_v1.json` |

No se alteraron Lexer, Parser, runtime, seguridad ni pruebas durante esta
revalidación.
