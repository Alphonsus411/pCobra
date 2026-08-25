# Reconciliación de refs y certificación pre-merge — 2026-08-25

## Identidad completa

| Dato | Valor demostrado |
|---|---|
| Repositorio | `https://github.com/Alphonsus411/pCobra.git` |
| Fecha UTC | `2026-08-25T18:27:45Z` |
| Ref de trabajo remota | `refs/heads/fix/contrato-extensiones-cobra` |
| Ref de integración remota | `refs/heads/master` |
| Refs locales de auditoría | `refs/remotes/audit-origin/fix/contrato-extensiones-cobra` y `refs/remotes/audit-origin/master` |
| Rama temporal | `audit/reconciliacion-refs-2026-08-25` |
| SHA inicial | `e6d1a087e92df40cd47cd7e926ff38c5ec3bb51a` |
| SHA remoto de `fix/contrato-extensiones-cobra` | `e6d1a087e92df40cd47cd7e926ff38c5ec3bb51a` |
| SHA remoto de `master` | `f684efc8a21d60eebcdce113cc8bfc21240ca37e` |
| Merge-base real tras completar el historial | `8b1676cdf52f30147ce42584a98ca4c421756369` |
| Ahead/behind (`fix...master`) | `323/1` |
| SHA de merge | `129fe063cbef1a507422da8f8658ae210db46c9c` |
| HEAD final auditado, antes de este informe documental | `129fe063cbef1a507422da8f8658ae210db46c9c` |

La consulta independiente de las dos refs remotas terminó con código `0` y dio
literalmente:

```text
e6d1a087e92df40cd47cd7e926ff38c5ec3bb51a refs/heads/fix/contrato-extensiones-cobra
f684efc8a21d60eebcdce113cc8bfc21240ca37e refs/heads/master
EXIT_CODE=0
```

El `fetch --unshallow` explícito de ambas refs terminó con código `0` y
`git rev-parse --is-shallow-repository` confirmó:

```text
false
EXIT_CODE=0
```

## Reconciliación del diagnóstico anterior

La auditoría anterior partió de `work` y de un entorno sin refs remotas
demostradas. El checkout era superficial: antes de reconciliarlo,
`git rev-parse --is-shallow-repository` devolvía `true` y `.git/shallow`
contenía nueve fronteras. Eso produjo el escenario local de historias
aparentemente no relacionadas. En aquel entorno se intentó
`--allow-unrelated-histories`, se observaron 770 conflictos y se abortó sin
cambios funcionales.

Ese diagnóstico fue **un resultado válido para aquel entorno local, pero no
representativo de la relación real de refs remotas**. No se modifica ni se
reescribe el informe anterior: esta auditoría añade la evidencia que faltaba.

Antes de completar el historial, la repetición controlada reprodujo el síntoma:

```text
COMMAND: git merge-base audit-origin/fix/contrato-extensiones-cobra audit-origin/master
EXIT_CODE=1
COMMAND: git rev-list --left-right --count audit-origin/fix/contrato-extensiones-cobra...audit-origin/master
199 238
EXIT_CODE=0
COMMAND: git merge --no-ff audit-origin/master -m "Merge audit-origin/master into audit/reconciliacion-refs-2026-08-25"
fatal: refusing to merge unrelated histories
EXIT_CODE=128
```

Esos números no se usan como identidad definitiva: procedían del grafo shallow.

## Relación real, grafo e integración

Después de `git fetch --unshallow`, los comandos definitivos dieron:

```text
COMMAND: git merge-base audit-origin/fix/contrato-extensiones-cobra audit-origin/master
8b1676cdf52f30147ce42584a98ca4c421756369
EXIT_CODE=0
COMMAND: git rev-list --left-right --count audit-origin/fix/contrato-extensiones-cobra...audit-origin/master
323 1
EXIT_CODE=0
```

Salida literal del grafo solicitado (limitado explícitamente a 20 entradas):

```text
COMMAND: git log --graph --oneline --decorate --boundary --max-count=20 audit-origin/fix/contrato-extensiones-cobra...audit-origin/master
*   e6d1a087 (HEAD -> audit/reconciliacion-refs-2026-08-25, audit-origin/fix/contrato-extensiones-cobra, work) Merge pull request #3545 from Alphonsus411/codex/corregir-regresiones-tras-el-merge
|\
| * d88ed32d docs(auditoria): bloquear correcciones sin estado post-merge
|/
*   2e1643c1 Merge pull request #3544 from Alphonsus411/codex/extraer-node-ids-y-seleccion-contractual
|\
| * 94309793 docs: registrar reejecución nominal de pytest
|/
*   865ed4d0 Merge pull request #3543 from Alphonsus411/codex/verificar-hashes-sha-256-de-archivos-lexer-y-parser
|\
| * 818393b6 docs(auditoria): certificar integridad post-merge
|/
*   15ca90bd Merge pull request #3542 from Alphonsus411/codex/obtener-lista-de-commits-y-archivos-afectados
|\
| * 960560de docs(auditoria): conservar evidencia de diferencia pre-merge
|/
*   c756151e Merge pull request #3541 from Alphonsus411/codex/preparar-rama-para-fusion-con-master
|\
| * 228736d9 docs(auditoria): registrar bloqueo de sincronización pre-merge
|/
*   9d7f34f6 Merge pull request #3514 from Alphonsus411/codex/revisar-y-ajustar-pruebas-en-tests-unitarios-e-integracion
|\
| * c66bb6cb test: asegurar precedencia de diagnósticos usar
|/
*   2b1122aa Merge pull request #3513 from Alphonsus411/codex/modificar-tratamiento-de-nameerror-en-ejecutar_usar
|\
| * cb0e1989 Preserva colisiones estructuradas de usar
|/
*   82af452a Merge pull request #3512 from Alphonsus411/codex/revisar-manejo-de-errores-en-interpreter.py
|\
| * f6779e02 Corrige contrato de error para usar fuera de catálogo
|/
*   f74c9b81 Merge pull request #3511 from Alphonsus411/codex/confirmar-supervivencia-de-fallos-en-auditoria
|\
| * 693bf767 docs(auditoria): comparar fallos restantes por node ID
|/
*   d04276e8 Merge pull request #3510 from Alphonsus411/codex/ejecutar-suite-de-pruebas-y-verificar-resultados
|\
| * 18c53dcc docs: registrar resultado de suite ampliada
|/
o   c0de4cf0 Merge pull request #3509 from Alphonsus411/codex/ajustar-pruebas-del-grupo-e-en-test_usar_public_contract
|\
EXIT_CODE=0
```

La integración real no necesitó `--allow-unrelated-histories`:

```text
COMMAND: git merge --no-ff audit-origin/master -m "Merge audit-origin/master into audit/reconciliacion-refs-2026-08-25"
Merge made by the 'ort' strategy.
 auditoria_contrato_extensiones_codigo.txt | 8002 +++++++++++++++++++++++++++++
 1 file changed, 8002 insertions(+)
 create mode 100644 auditoria_contrato_extensiones_codigo.txt
EXIT_CODE=0
COMMAND: git rev-parse HEAD HEAD^1 HEAD^2
129fe063cbef1a507422da8f8658ae210db46c9c
e6d1a087e92df40cd47cd7e926ff38c5ec3bb51a
f684efc8a21d60eebcdce113cc8bfc21240ca37e
EXIT_CODE=0
```

## Hashes protegidos

`sha256sum` terminó con código `0` y produjo literalmente:

```text
537554f0cab9fb4ca456b2b99a43fca7b275241dcddfa5bb0fc3dcad78534e70  src/pcobra/cobra/core/lexer.py
3017fa31e1707ca82358d548e71ba27d4b8e73342950ab6959b32c13dcc02505  src/pcobra/cobra/core/parser.py
fbd130d88ec6255c1e966752730a7cb2e2311c50125d85df487fc67d55aaf61e  src/pcobra/core/lexer.py
656d9c911ab0760435efc48502625b6016955f00d0429228a0ffced87e982a2b  src/pcobra/core/parser.py
EXIT_CODE=0
```

`git diff --name-status e6d1a087...129fe063 --` limitado a esos cuatro
paths no produjo salida y terminó con código `0`: Lexer y Parser no cambiaron.

## Gates focales

Se conservan resultados literales, no estados inferidos:

| Gate y comando exacto | Código | Resultado literal / estado |
|---|---:|---|
| `python scripts/validate_runtime_contract.py` | 0 | `✅ Runtime contract validation: OK`; runtimes oficiales y ejecutables: Python, JavaScript y Rust; Holobit mantenido en los tres; compatibilidad SDK completa en Python. **PASS**. |
| `python -m pytest -q tests/unit/test_cli_validar_sintaxis_report_schema.py tests/unit/cli/commands/test_validar_sintaxis_cmd.py tests/integration/test_cli_validar_sintaxis.py tests/unit/test_syntax_fixture_guard.py` | 1 | `1 failed, 8 passed in 1.30s`; el guard esperaba 9 fixtures y encontró 18. **FAIL**. |
| `python scripts/sync_libro_programacion.py --check` | 0 | `Sin drift documental.` **PASS**. |
| `python -m pytest -q tests/unit/test_usar_public_contract.py tests/integration/test_usar_public_contract_regression.py tests/integration/test_repl_usar_entrypoints_contract.py` | 1 | `2 failed, 143 passed, 2 warnings in 5.77s`; fallan los dos node IDs de colisión estructurada porque no aparece `usar_error[conflicto_simbolo]`. **FAIL**. |
| `python -m pytest -q tests/unit/test_holobit_backend_contract_matrix.py tests/unit/test_holobit_sdk_compatibility_report.py tests/integration/test_holobit_tiers.py` | 0 | `103 passed in 1.75s`. **PASS**. |
| `python -m pytest -q tests/unit/test_runtime_api_matrix_contract.py tests/cli/test_runtime_imports_contract.py` | 0 | `9 passed in 1.45s`. **PASS**. |
| `python -m pytest -q tests/test_codeql_config.py tests/test_workflows_yaml.py` | 0 | `31 passed in 0.19s`. Sólo contrato textual: **PASS**. |
| `command -v codeql` | 1 | Salida vacía. El CLI/harness real queda **NO EJECUTADO / NO DEMOSTRADO**, no PASS. |
| `ruff check src/pcobra` | 0 | `All checks passed!` **PASS**. |
| `mypy src/pcobra` | 1 | `Found 1750 errors in 270 files (checked 461 source files)`. **FAIL**. |
| `python scripts/smoke_syntax.py` | 0 | `🎉 Smoke de sintaxis completado correctamente.` **PASS**. |
| `python scripts/smoke_transpilers_syntax.py` | 0 | Python, JavaScript y Rust: `ok=3 fail=0 skipped=0`; `🎉 Smoke de transpiladores completado sin fallos obligatorios.` **PASS**. |
| `pyright` | sin código final | La ejecución no entregó salida ni código terminal verificable. **CANCELADO / NO DEMOSTRADO**. |
| `black --check .` | sin código final | La ejecución no entregó código terminal verificable. **CANCELADO / NO DEMOSTRADO**. |

Los checks cancelados y el harness omitido no se presentan como verdes. Los 54
tests `skipped` de cada suite global tampoco se contabilizan como PASS.

## Suites globales y baseline diferencial

En el HEAD de merge:

```text
COMMAND: python -m pytest -q
514 failed, 4408 passed, 54 skipped, 31 warnings, 3 errors in 699.88s (0:11:39)
EXIT_CODE=1
```

En un worktree detached del SHA remoto inicial:

```text
COMMAND: (cd /tmp/pcobra-baseline-20260825 && python -m pytest -q)
515 failed, 4407 passed, 54 skipped, 31 warnings, 3 errors in 578.90s (0:09:38)
EXIT_CODE=1
```

La comparación literal se hizo con los node IDs únicos de las líneas `FAILED`
y `ERROR`:

```text
MERGE_NODE_IDS=550
BASELINE_NODE_IDS=551
COMMAND: comm -23 /tmp/merge.nodes /tmp/baseline.nodes
EXIT_CODE=0
COMMAND: comm -13 /tmp/merge.nodes /tmp/baseline.nodes
tests/unit/test_security_sandbox.py::test_js_detecta_reemplazo_binario
EXIT_CODE=0
```

Por tanto, no apareció ningún node ID fallido nuevo en el merge; un node ID del
baseline no falló en la segunda ejecución. No se eleva esa desaparición a una
corrección funcional: el diferencial de archivos entre los dos árboles fue
literalmente:

```text
A auditoria_contrato_extensiones_codigo.txt
EXIT_CODE=0
```

La variación de un test, pese a árboles ejecutables idénticos, demuestra que el
conteo global tiene variabilidad de ejecución. La clasificación diferencial es:

- `FALLOS_NUEVOS`: **0 node IDs demostrados**;
- `HISTORICOS_QUE_SIGUEN`: **550 node IDs**;
- `HISTORICOS_QUE_DESAPARECEN`: **1 node ID observado**, no atribuible al merge
  documental;
- checks skipped, cancelados o no ejecutados: **no clasificados como PASS**.

## Riesgos residuales demostrados

Únicamente se conservan riesgos respaldados por las ejecuciones anteriores:

1. La suite global permanece roja en ambos árboles y conserva 550 node IDs con
   fallo/error en el merge, incluidos tres errores SQLite de `test_token_cache.py`.
2. El gate focal de sintaxis falla por el desacuerdo demostrado `18 != 9` en el
   inventario de fixtures.
3. El gate focal de `usar` conserva dos fallos de su contrato de error público.
4. Mypy conserva 1.750 errores en 270 archivos.
5. El harness real de CodeQL no pudo ejecutarse porque el binario no está
   disponible; Pyright y Black carecen de resultado terminal verificable.
6. El baseline global demostró variabilidad en un node ID aun sin diferencias de
   código o tests entre los árboles comparados.

No se atribuye ninguno de esos riesgos a `master`: su integración añadió sólo un
archivo de auditoría y la comparación no mostró fallos nuevos.

## Veredicto

La reconciliación de refs y la integración están demostradas y no introducen
fallos nuevos por node ID. Sin embargo, los criterios de certificación no permiten
declarar verde una rama con gates focales y suite global en rojo, ni con checks no
ejecutados, cancelados o skipped.

**NOT_READY_FOR_MERGE**
