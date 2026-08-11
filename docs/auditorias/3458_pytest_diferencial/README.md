# Auditoría diferencial de `pytest -q` — rama posterior a #3458

## Baseline, entorno y orden de ejecución

Se comparó el HEAD inicial de la rama, `896525303f74c7b7d3c8cffb9eb8ec00eb848885`,
con `96d70b1ba00f07608b0fc2a780fca0e7d6b09257`, el baseline inmutable ya
elegido para la auditoría de Pylint y usado por la auditoría diferencial
anterior. El baseline se montó como worktree detached. Las dos ejecuciones
usaron secuencialmente `/root/.pyenv/versions/3.12.13/bin/python`, Python
3.12.13, pytest 9.0.3, las mismas dependencias instaladas y las mismas
variables heredadas; las únicas diferencias de `env` fueron `PWD` y `OLDPWD`
por estar en worktrees diferentes.

Primero se ejecutó la familia focalizada de la política de targets y después
la suite completa, sin `--maxfail`, nuevos skips ni nuevos xfails:

```bash
python -m pytest -q tests/unit/test_validate_targets_policy_script.py
python -m pytest -q
git worktree add --detach /tmp/pcobra-baseline \
  96d70b1ba00f07608b0fc2a780fca0e7d6b09257
(cd /tmp/pcobra-baseline && python -m pytest -q)
```

Se aplicó un límite externo de 3600 segundos a cada suite completa solamente
para poder registrar un timeout. Ninguna ejecución agotó el límite: la rama
terminó en 699.24 s y el baseline en 705.31 s.

## Contadores completos

`collected` se obtiene sumando todos los resultados terminales de pytest. No
apareció la categoría `xfailed`, por lo que se registra explícitamente como
cero.

| Árbol | collected | passed | failed | skipped | xfailed | errors | warnings | timeout |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Baseline `96d70b1b` | 4936 | 4368 | 511 | 54 | 0 | 3 | 31 | ninguno (705.31 s) |
| Rama `89652530` | 4940 | 4373 | 510 | 54 | 0 | 3 | 31 | ninguno (699.24 s) |

La prueba focalizada terminó en la rama con `1 failed, 15 passed, 2 warnings`
y en baseline con `1 failed, 13 passed, 2 warnings`. El fallo compartido fue
`test_ci_validate_targets_guardrail_permite_exclusiones_de_packaging`, con el
mensaje exacto: `fuga de histórico retirado en rutas de packaging
(archive/retired_targets)`.

## Comparación normalizada por nodeid

Se extrajeron las líneas `FAILED` y `ERROR` del resumen corto, se conservaron
por separado ambos estados y se ordenaron de forma única antes de aplicar
`comm`. Hay 508 pares estado/nodeid no satisfactorios compartidos. La rama
tiene uno exclusivo y el baseline dos. Los tres errores de setup son los
mismos nodeids en ambos árboles:

`tests/unit/test_token_cache.py::{test_obtener_tokens_reutiliza,
test_tokens_persistidos,test_fragmentos_limpiar}`. Su mensaje exacto es
`sqlite3.OperationalError: no such table: ast_fragments`; por tanto son un
problema común del entorno/estado de la caché y no una regresión de la rama.

| Test/familia | baseline | rama | clasificación |
|---|---|---|---|
| 508 pares estado/nodeid compartidos | mismo `FAILED`/`ERROR` | mismo `FAILED`/`ERROR` | Fallos históricos compartidos; delta cero por nodeid. |
| `test_integridad_estatica_lexer_y_parser_sin_diff_inesperado` | no recolectado con ese nodeid | `FAILED` | **Regresión atribuible/bloqueante detectada por un guard nuevo**. Mensaje exacto: `AssertionError: Hash inesperado en src/pcobra/cobra/core/lexer.py`; hash esperado `537554f0…`, obtenido `7cf70380…`. La rama no está lista. |
| `test_snippets_generados_siguen_sincronizados_con_la_fuente_canonica` | `FAILED` | pasa | Mejora: los snippets generados ya están sincronizados. El baseline mostraba `AssertionError: assert before == after`. |
| `test_js_detecta_reemplazo_binario` | `FAILED` | pasa en esta ejecución | Intermitente histórico de plataforma, ya reproducido alternando pase/fallo en el baseline por la auditoría anterior. Mensaje exacto del baseline: `Failed: DID NOT RAISE <class 'sandbox.SecurityError'>`. No se atribuye a la rama. |
| Dependencia opcional de notebooks | warning/skip equivalente | warning/skip equivalente | Entorno compartido. Mensaje exacto: `ImportError("cannot import name 'Draft4Validator' from 'jsonschema' (unknown location)")`. |
| **Total de pares estado/nodeid únicos** | **510** | **509** | **1 exclusivo de rama, 2 exclusivos de baseline; ninguna transición de pasa-en-baseline a falla-en-rama para un nodeid recolectado en ambos. La regresión de integridad sigue siendo bloqueante por causalidad y por la política del repositorio.** |

La diferencia de los totales de ejecuciones frente a los nodeids únicos se
debe a nodeids repetidos durante la colección; la decisión se tomó sobre la
identidad normalizada, no sobre el número agregado de letras `F`.

## Decisión y tarea independiente

**No se declara la rama lista.** El guard atribuye el único hallazgo nuevo a
un cambio previo de Lexer/Parser. Las instrucciones del repositorio prohíben
modificar esos archivos sin autorización explícita, así que esta auditoría no
los corrige ni actualiza el hash esperado para ocultar el fallo. La causa se
abre de forma aislada en
`docs/issues/15_restaurar_integridad_lexer_parser.md`; no se mezcla ninguna
remediación con este registro.
