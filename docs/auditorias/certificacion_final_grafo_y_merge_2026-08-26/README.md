# Certificación final del grafo y del merge — 2026-08-26

## Alcance y decisión

Esta ejecución auditó la integración de `origin/master` en
`fix/contrato-extensiones-cobra` sin fusionar la rama de corrección hacia
`master`. El árbol integrado quedó preparado localmente, pero **no se publicó**:
el primer `git push` ordinario fue rechazado porque este entorno no dispone de
credenciales GitHub. Por ello no se creó el segundo commit remoto, no existe CI
del HEAD local y la decisión es **NOT_READY_FOR_MERGE (PUBLICATION_BLOCKED)**,
no `READY_FOR_MERGE_WITH_KNOWN_BASELINE` ni `REMOTE_CI_PENDING`.

## Estado inicial y completitud del repositorio

| Dato | Resultado |
|---|---|
| Rama de checkout inicial | `work` |
| HEAD inicial | `6c3898fabfbe22951ca44870a89d10a358fff34b` |
| Árbol de trabajo inicial | limpio |
| `git rev-parse --is-shallow-repository` inicial | `true` |
| Remotos configurados inicialmente | ninguno |
| Promisor / partial clone inicial | no configurado; no existían claves `remote.*.promisor` ni `remote.*.partialclonefilter` |
| Merge-base esperado disponible localmente antes del fetch | sí; `git cat-file -e 8b1676cdf52f30147ce42584a98ca4c421756369^{commit}` devolvió 0 |

Se añadió `origin=https://github.com/Alphonsus411/pCobra.git` y se ejecutó
`git fetch --unshallow origin '+refs/heads/*:refs/remotes/origin/*' --tags`.
El repositorio pasó a `shallow=false`. No apareció configuración promisor ni
partial-clone tras el fetch. `git fsck --full --no-dangling` terminó con código
0 y sin salida: no detectó errores de conectividad o integridad.

## Referencias y grafo iniciales

Los SHAs se obtuvieron primero mediante `git ls-remote`, antes de configurar y
actualizar las referencias locales:

| Referencia remota | SHA inicial |
|---|---|
| `refs/heads/master` | `f684efc8a21d60eebcdce113cc8bfc21240ca37e` |
| `refs/heads/fix/contrato-extensiones-cobra` | `6c3898fabfbe22951ca44870a89d10a358fff34b` |

Con el historial completo:

- merge-base inicial: `8b1676cdf52f30147ce42584a98ca4c421756369`;
- divergencia `origin/master...origin/fix/contrato-extensiones-cobra`: `1 331`
  (master sólo / fix sólo);
- diferencia de `master` desde el merge-base: añade
  `auditoria_contrato_extensiones_codigo.txt`.

## Merge local

Se creó la rama temporal local `cert/grafo-merge-2026-08-26` y se ejecutó:

```console
git merge --no-ff origin/master -m 'Merge origin/master into fix/contrato-extensiones-cobra'
```

El merge terminó sin conflictos y produjo
`f2b0a87a975019f7cf5810ad5ba799ccc162f8c6`. `origin/master` es ancestro del
merge. La divergencia local post-merge fue `0 332`. Aunque el commit exclusivo
de `master` añadió históricamente `auditoria_contrato_extensiones_codigo.txt`,
`git diff --name-status HEAD^1..HEAD` quedó vacío: ese contenido ya estaba en el
árbol del primer padre y el merge no introdujo cambios materiales de archivos.

## Integridad de Lexer y Parser

Los hashes SHA-256 se tomaron antes y después del merge y fueron idénticos:

| Archivo | SHA-256 |
|---|---|
| `src/pcobra/cobra/core/lexer.py` | `537554f0cab9fb4ca456b2b99a43fca7b275241dcddfa5bb0fc3dcad78534e70` |
| `src/pcobra/cobra/core/parser.py` | `3017fa31e1707ca82358d548e71ba27d4b8e73342950ab6959b32c13dcc02505` |
| `src/pcobra/core/lexer.py` | `fbd130d88ec6255c1e966752730a7cb2e2311c50125d85df487fc67d55aaf61e` |
| `src/pcobra/core/parser.py` | `656d9c911ab0760435efc48502625b6016955f00d0429228a0ffced87e982a2b` |

No se modificaron Lexer, Parser, gramática, tokens ni sintaxis.

## Contratos y comprobaciones dirigidas post-merge

| Comando | Resultado |
|---|---|
| `python -m compileall -q src` | PASS |
| `python scripts/validate_runtime_contract.py` | PASS; runtime oficial y ejecutable: Python, JavaScript y Rust; compatibilidad SDK completa: Python |
| `python scripts/sync_libro_programacion.py --check` | PASS; `Sin drift documental.` |
| `python scripts/ci/validate_workflow_target_matrix.py` | PASS |
| `python -m pytest -q tests/unit/test_ci_workflow_extension_contract.py` | PASS; `2 passed` |

### Comparación de `usar`

La batería focal post-merge terminó con `2 failed, 143 passed, 2 warnings`.
Los dos node IDs son los mismos reproducidos en la auditoría inmediata anterior
sobre el primer padre:

- `tests/integration/test_usar_public_contract_regression.py::test_conflicto_no_overwrite_silencioso_reporta_error_estructurado`;
- `tests/integration/test_usar_public_contract_regression.py::test_conflictos_abortan_inyeccion_sin_overwrite_silencioso`.

En ambos estados la aserción espera `usar_error[conflicto_simbolo]`, mientras el
mensaje real comienza por `No se puede usar 'datos': hay conflicto de símbolos`.
Clasificación: `HISTORICAL_BASELINE`; no hay regresión nueva de `usar`.

## Suite global y conjuntos de fallos

| Estado | Resultado |
|---|---|
| Baseline inmediato `6c3898fa` | `514 failed, 4408 passed, 54 skipped, 31 warnings, 3 errors` en 579.53 s |
| Merge local `f2b0a87a` | `514 failed, 4408 passed, 54 skipped, 30 warnings, 3 errors` en 563.41 s |

Los XML JUnit contienen 517 casos no satisfactorios en cada ejecución (514
fallos y 3 errores). La comparación exacta por `(classname, name)` produjo:

- `HISTORICOS_QUE_SIGUEN`: 517;
- `HISTORICOS_QUE_DESAPARECEN`: 0;
- `FALLOS_NUEVOS`: 0;
- intersección baseline/post-merge: 517.

La única diferencia agregada es un warning menos; el conjunto de tests fallidos
y con error es exactamente el mismo.

## Calidad estática y CodeQL local

| Herramienta | Resultado |
|---|---|
| `git ls-files '*.py' -z \| xargs -0 python -m ruff check` | FAIL baseline: 9 `F821` preexistentes |
| `python -m black --check .` | FAIL baseline: 2 archivos serían reformateados (`tests/unit/test_holobit_graficar_contract.py`, `tests/unit/test_usar_symbol_policy.py`) |
| `python -m mypy src` | FAIL baseline: 1754 errores en 273 archivos (475 comprobados) |
| CodeQL CLI local | no disponible en el entorno (`codeql` no instalado); el análisis remoto tampoco pudo dispararse para el merge no publicado |

Una primera invocación no canónica de `ruff check .` atravesó `.git` tras el
fetch de todas las refs y produjo ruido sobre metadatos Git; el resultado
reportado arriba es la repetición limitada a Python versionado.

## Publicación, HEAD remoto final y divergencia final

Antes del primer push se repitió
`git fetch origin master fix/contrato-extensiones-cobra` y se comprobó que la
rama remota seguía exactamente en el SHA inicial `6c3898fa`. El push ordinario,
sin `--force`, de `f2b0a87a` fue rechazado con:

```text
fatal: could not read Username for 'https://github.com': No such device or address
```

`gh auth status` confirmó que no existe una sesión autenticada. Una consulta
posterior con `git ls-remote` confirmó como **HEAD remoto final real**
`6c3898fabfbe22951ca44870a89d10a358fff34b`. Por tanto:

- merge publicado por esta ejecución: ninguno;
- commit documental publicado: ninguno;
- segundo push fast-forward: no ejecutado, porque el primer push no se publicó;
- force push: no utilizado;
- divergencia remota final `origin/master...origin/fix/...`: `1 331`;
- `master` no es ancestro del HEAD remoto final;
- rama remota detrás de `master`: 1 commit.

## Checks del HEAD remoto final

Se consultó individualmente la API pública de check-runs para el HEAD remoto
real `6c3898fa`. Había dos checks asociados; no había checks con los otros
nombres requeridos:

| Check requerido | Estado individual en `6c3898fa` |
|---|---|
| Tests | `NOT_REPORTED` |
| Lint | `completed / failure` |
| Black | `NOT_REPORTED` (la comprobación local también falla) |
| Runtime Contract | `NOT_REPORTED` (contrato local PASS) |
| CodeQL | job `analyze`: `completed / failure` |
| Workflow validation | `NOT_REPORTED` |

No hay checks pendientes, así que `REMOTE_CI_PENDING` no describe el estado
observado. El CI requerido tampoco finalizó correctamente: faltan cuatro checks
y fallan Lint y CodeQL.

## Riesgos residuales y veredicto

Persisten 514 fallos y 3 errores históricos en la suite, 9 errores Ruff, 2
archivos fuera de formato Black, 1754 errores mypy, ausencia de CodeQL local y
un CI remoto incompleto/fallido. Además, el merge certificado sólo existe
localmente por falta de autenticación y la rama remota continúa un commit detrás
de `master`.

Aunque no aparecieron fallos nuevos, los contratos runtime/documental están
verdes y Lexer/Parser permanecen intactos, no se cumplen publicación, ancestry,
divergencia cero ni CI exitoso. Veredicto final:
**NOT_READY_FOR_MERGE (PUBLICATION_BLOCKED)**.
