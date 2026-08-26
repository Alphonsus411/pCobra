# Auditoría de publicación final de `fix/contrato-extensiones-cobra` — 2026-08-26

## Resultado ejecutivo

La publicación solicitada no pudo realizarse desde este entorno. El push
ordinario fue rechazado porque no hay credenciales de GitHub disponibles. Este
informe registra el estado remoto observado, sin presentar como publicado un
commit que no llegó al servidor.

**Resultado global:** `PUBLICATION_BLOCKED_NO_CREDENTIALS`

**NEW_FAILURES:** `0` en la comparación focal/global histórica disponible

**Veredicto:** `NOT_READY_FOR_MERGE (PUBLICATION_BLOCKED)`

## Grafo y referencias

| Campo | Resultado |
|---|---|
| `MASTER_SHA` | `f684efc8a21d60eebcdce113cc8bfc21240ca37e` |
| `FIX_SHA_INICIAL` | `6c3898fabfbe22951ca44870a89d10a358fff34b` |
| `MERGE_BASE` inicial | `8b1676cdf52f30147ce42584a98ca4c421756369` |
| Divergencia inicial (`master` / `fix`) | `1 / 331` |
| `MERGE_SHA` local no publicado | `f2b0a87a975019f7cf5810ad5ba799ccc162f8c6` |
| Conflictos del merge local | ninguno |
| `FIX_SHA_FINAL` remoto observado | `8b7d125cd65a8c35c17d1b632b13d53c5886d818` |
| Divergencia final observada (`master` / `fix`) | `1 / 333` |
| `master` es ancestro del `FIX_SHA_FINAL` | no |

El `MERGE_SHA` certificado fue creado localmente en una ejecución anterior,
pero no fue publicado. El HEAD remoto avanzó posteriormente mediante commits
documentales y continuó sin contener a `master`; por ello no se confunde el
merge local con el estado efectivo de la rama remota.

## Gates focales y suite global

Los resultados certificados sobre el merge local no publicado fueron:

| Gate | Resultado |
|---|---|
| `python -m compileall -q src` | PASS |
| `python scripts/validate_runtime_contract.py` | PASS |
| `python scripts/sync_libro_programacion.py --check` | PASS; sin drift documental |
| `python scripts/ci/validate_workflow_target_matrix.py` | PASS |
| `python -m pytest -q tests/unit/test_ci_workflow_extension_contract.py` | PASS; `2 passed` |
| Suite focal de `usar` | FAIL histórico; `2 failed, 143 passed, 2 warnings` |
| Suite global | FAIL histórico; `514 failed, 4408 passed, 54 skipped, 3 errors` |

Los node IDs históricos de `usar` fueron:

- `tests/integration/test_usar_public_contract_regression.py::test_conflicto_no_overwrite_silencioso_reporta_error_estructurado`;
- `tests/integration/test_usar_public_contract_regression.py::test_conflictos_abortan_inyeccion_sin_overwrite_silencioso`.

La comparación JUnit histórica produjo 517 casos no satisfactorios antes y
después del merge local: 517 persistieron, ninguno desapareció y no apareció
ninguno nuevo. Clasificación: `HISTORICAL_BASELINE`; `NEW_FAILURES=0`.

## Lexer y Parser

El diff del HEAD remoto observado respecto de su primer padre no contiene
archivos Lexer ni Parser. No se modificaron tokens, gramática ni sintaxis en
esta auditoría. Estado: **INTACTOS**.

## Push ordinario

Se ejecutó, sin `--force`:

```console
git push origin HEAD:refs/heads/fix/contrato-extensiones-cobra
```

Resultado:

```text
fatal: could not read Username for 'https://github.com': No such device or address
```

No se realizó force push. El resultado operativo es
`PUBLICATION_BLOCKED_NO_CREDENTIALS`.

## CI del HEAD remoto definitivo observado

La API pública de GitHub fue consultada para
`8b7d125cd65a8c35c17d1b632b13d53c5886d818`. Estado individual de los seis
grupos requeridos:

| Grupo | Estado |
|---|---|
| Tests | `NOT_REPORTED` |
| Lint | `completed / failure` (check-run `98162832201`) |
| Black | `NOT_REPORTED` |
| Runtime Contract | `NOT_REPORTED` |
| CodeQL | `analyze: completed / failure` (check-run `98162833327`) |
| Workflow validation | `NOT_REPORTED` |

No hay checks pendientes en los resultados publicados, pero cuatro grupos no
fueron reportados y dos finalizaron con fallo. Los fallos observados se
clasifican como históricos respecto de la evidencia previa; esta auditoría no
atribuye fallos nuevos a un commit documental no publicado.

## Veredicto

Aunque los gates contractuales focales quedaron verdes y no se identificaron
fallos nuevos, no se cumplieron la publicación, la comprobación de ancestro, la
divergencia cero ni un CI remoto completo y exitoso. Veredicto final:
**NOT_READY_FOR_MERGE (PUBLICATION_BLOCKED)**.
