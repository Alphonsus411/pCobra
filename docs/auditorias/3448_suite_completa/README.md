# Auditoría diferencial de la suite completa — cierre posterior a #3448

## Alcance y entorno reproducible

Se auditó el HEAD inicial `6331ec3b` contra el baseline solicitado
`96d70b1ba00f07608b0fc2a780fca0e7d6b09257`. Ambos árboles se ejecutaron de
forma secuencial con el mismo intérprete (`Python 3.12.13`), ejecutable
(`/root/.pyenv/shims/python`), dependencias instaladas (`pytest 9.0.3`,
`pluggy 1.6.0`, `flet 0.86.1`, `anyio 4.13.0`), variables heredadas y comando.
No se usó `--maxfail`.

```bash
# current, desde /workspace/pCobra en 6331ec3b
python --version
python -m pytest --version
python -m pytest

# baseline solicitado
git worktree add --detach /tmp/pcobra-baseline-96d70b1b \
  96d70b1ba00f07608b0fc2a780fca0e7d6b09257
(cd /tmp/pcobra-baseline-96d70b1b && python -m pytest)

# normalización local (los archivos /tmp no se versionan)
awk '/^=+ short test summary info =+/{p=1;next} p && /^=/{exit} \
  p && /^(FAILED|ERROR) /{sub(/ - .*/,""); sub(/^(FAILED|ERROR) /,""); print}' \
  /tmp/pcobra-current-pytest.log | sort -u > /tmp/current-nodes.txt
comm -13 /tmp/baseline-nodes.txt /tmp/current-nodes.txt
comm -23 /tmp/baseline-nodes.txt /tmp/current-nodes.txt
```

La suite base terminó con `507 failed, 4372 passed, 54 skipped, 3 errors`
(510 node IDs no satisfactorios); current inicial terminó con `514 failed,
4365 passed, 54 skipped, 3 errors` (517). No hubo errores de colección en
ninguno de los dos árboles: los tres `ERROR` son errores de setup de la caché
SQLite, presentes en ambos. Tras corregir los seis snapshots dañados, current
normalizado queda en 511 node IDs: no se vuelve a presentar una suite completa
como verde ni se deduce ausencia de regresiones del total agregado.

## Comparaciones adicionales de la familia responsable

El cambio responsable de los daños nuevos es la familia de formateo
`92e3291d` (integrada por `728e3633`). Se seleccionó también su commit
inmediatamente anterior, `f92f5f5863ef51d9722cdaea7a1c42619135e9a8`, en
vez de usar `master` como sustituto del baseline. `master` queda únicamente
como comparación secundaria y no fue necesaria para decidir causalidad.

```bash
git worktree add --detach /tmp/pcobra-pre-format \
  f92f5f5863ef51d9722cdaea7a1c42619135e9a8
(cd /tmp/pcobra-pre-format && \
  python -m pytest -q tests/test_ejemplos_io.py::test_build_coincide_con_archivo)
python -m pytest -q tests/test_ejemplos_io.py::test_build_coincide_con_archivo
```

Los seis casos pasan en el commit anterior (6/6), fallan en el HEAD inicial
(0/6) y vuelven a pasar después de restaurar los snapshots (6/6).

## Resultados normalizados por causa raíz

La clasificación se realizó sobre node IDs únicos, no sobre el número de
líneas `F` ni sobre el agregado de pytest. “Current” refleja el estado después
de la única remediación permitida; por ello totaliza 511.

| Familia | Baseline | Current | Delta | Clasificación | Evidencia |
|---|---:|---:|---:|---|---|
| Colección/imports | 4 | 4 | 0 | Histórica | Mismos cuatro node IDs de importación; 0 errores de colección. Los 3 `ERROR` SQLite también coinciden exactamente. |
| Contratos deliberadamente endurecidos | 25 | 25 | 0 | Mixta: histórica, una mejora y una regresión bloqueada | Desaparece `test_snippets_generados_siguen_sincronizados_con_la_fuente_canonica` (mejora), pero aparece el guard de hash de Lexer/Parser. Los demás contratos son compartidos y se consideran históricos o pruebas obsoletas por contrato deliberado según sus mensajes de policy. |
| Dependencias/herramientas externas | 25 | 25 | 0 | Histórica | Mismos node IDs de Jupyter, AGIX, Qualia, Flet y bridges en ambos árboles. |
| Plataforma | 0 | 1 | +1 | Histórica/intermitente, no atribuible | `test_js_detecta_reemplazo_binario` alterna incluso en baseline (dos fallos y un pase en tres repeticiones); depende de una carrera al reemplazar el ejecutable falso. |
| Transpilers | 189 | 189 | 0 | Histórica | Conjunto normalizado compartido después de retirar los seis snapshots alterados accidentalmente. |
| Runtime/sandbox | 144 | 144 | 0 | Histórica o prueba obsoleta por contrato deliberado | Mismos node IDs de REPL, `usar`, intérprete, safe mode y límites en ambos árboles. |
| Packaging | 10 | 10 | 0 | Histórica | Mismos node IDs de wheel, installer y empaquetado. |
| Defectos funcionales | 113 | 113 | 0 | Histórica | Resto exacto del conjunto compartido, sin node IDs exclusivos. |
| **Total** | **510** | **511** | **+1** | **Una regresión bloqueada; seis regresiones corregidas** | La diferencia residual es el guard de integridad de Lexer/Parser; el caso JS es intermitente histórico aunque no apareciera en aquella ejecución completa del baseline. |

## Investigación exhaustiva de node IDs exclusivos de current inicial

| Node ID/familia | Investigación y clasificación | Decisión |
|---|---|---|
| `test_integridad_estatica_lexer_y_parser_sin_diff_inesperado` | El hash de `src/pcobra/cobra/core/lexer.py` cambió solo por formateo en `92e3291d`; `parser.py` también fue reformateado. Regresión real atribuible a la rama. | **Bloqueada**: la orden prohíbe modificar Lexer y Parser. No se cambia el guard ni sus hashes para ocultarla. |
| Los seis parámetros de `tests/test_ejemplos_io.py::test_build_coincide_con_archivo` | Black reformateó snapshots byte-a-byte, pero el transpilador sigue emitiendo el formato canónico anterior. El commit inmediatamente anterior pasa 6/6. Regresión real de artefactos de salida. | **Corregida** en un commit independiente restaurando exactamente los snapshots previos; no se cambia el código Cobra ni la prueba. |
| `tests/unit/test_security_sandbox.py::test_js_detecta_reemplazo_binario` | La misma prueba falla 2/3 y pasa 1/3 en baseline; en current falla 3/3. El diff de la familia solo reformatea el test y sandbox sin cambio semántico. | Histórica/intermitente de plataforma; no atribuible a la rama y no corregida en este cierre incremental. |

El único node ID exclusivo de baseline,
`test_snippets_generados_siguen_sincronizados_con_la_fuente_canonica`, pasa en
current gracias a la sincronización documental y se clasifica como **mejora**.

## Restricciones verificadas

No se modificaron Lexer, Parser, gramática, tokens, `constant_folder` ni
`src/pcobra/core/ast_nodes.py` durante esta remediación. En particular, la
regresión de hashes se deja documentada como bloqueo en lugar de infringir la
restricción. Los logs completos y las listas normalizadas permanecen solo en
`/tmp`; este artefacto contiene resultados, comandos y evidencia resumida, no
outputs temporales.
