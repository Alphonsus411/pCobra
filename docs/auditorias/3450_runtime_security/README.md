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
