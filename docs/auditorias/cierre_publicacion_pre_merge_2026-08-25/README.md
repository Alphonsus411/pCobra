# Cierre y publicación pre-merge — 2026-08-25

## Refs e integración verificadas

- Rama de trabajo: `audit/pre-merge-fix-contrato-extensiones`.
- `origin/master`: `f684efc8a21d60eebcdce113cc8bfc21240ca37e`.
- HEAD anterior a la integración: `d1440be169193ffdaacb50f9ab684e4fc646b7f0`.
- Merge commit: `2550d652c67850a5e5146ec97f91eeeb03ea2af7`.
- Padres del merge: `d1440be169193ffdaacb50f9ab684e4fc646b7f0` y
  `f684efc8a21d60eebcdce113cc8bfc21240ca37e`.
- Merge-base final con `origin/master`:
  `f684efc8a21d60eebcdce113cc8bfc21240ca37e`.

La integración se realizó con `git merge --no-ff origin/master` y la estrategia
`ort`, sin conflictos. El merge es vacío respecto de su primer padre porque el
contenido de `origin/master` ya estaba presente en el árbol, pero conserva la
relación de procedencia requerida. `git merge-base --is-ancestor origin/master
HEAD` terminó con código `0`: `origin/master` es ancestro de HEAD.

## Resultado y baseline diferencial

El diferencial `origin/master...HEAD` contiene el trabajo acumulado de la rama:
**907 archivos cambiados, 25.754 inserciones y 8.305 eliminaciones** antes de
añadir este informe. No se modificó ninguna auditoría histórica en este cierre.

`git diff --check origin/master...HEAD` detectó seis espacios finales heredados
en dos informes históricos:

- dos en `docs/auditorias/pytest_contrato_extensiones_2026-08-10.md`;
- cuatro en `docs/resultado_suite_ampliada_2026-08-20.md`.

Se preservan deliberadamente porque el encargo prohíbe modificar auditorías
históricas. `git diff --check` sobre los cambios nuevos del cierre no produjo
salida.

Los gates dirigidos repetidos sobre el merge dieron:

| Comando | Resultado |
|---|---|
| `python scripts/validate_runtime_contract.py` | código 0, `Runtime contract validation: OK` |
| `python scripts/sync_libro_programacion.py --check` | código 0, `Sin drift documental.` |
| `python -m pytest -q tests/unit/test_usar_public_contract.py tests/integration/test_usar_public_contract_regression.py tests/integration/test_repl_usar_entrypoints_contract.py` | código 1, `2 failed, 143 passed, 2 warnings` |

Los dos fallos siguen siendo los node IDs históricos de colisión estructurada
que esperan `usar_error[conflicto_simbolo]`; no apareció una causa nueva.

## Integridad de Lexer y Parser

El diff limitado a los cuatro archivos protegidos entre `origin/master` y HEAD
fue vacío. Sus hashes SHA-256 permanecen:

| Archivo | SHA-256 |
|---|---|
| `src/pcobra/cobra/core/lexer.py` | `537554f0cab9fb4ca456b2b99a43fca7b275241dcddfa5bb0fc3dcad78534e70` |
| `src/pcobra/cobra/core/parser.py` | `3017fa31e1707ca82358d548e71ba27d4b8e73342950ab6959b32c13dcc02505` |
| `src/pcobra/core/lexer.py` | `fbd130d88ec6255c1e966752730a7cb2e2311c50125d85df487fc67d55aaf61e` |
| `src/pcobra/core/parser.py` | `656d9c911ab0760435efc48502625b6016955f00d0429228a0ffced87e982a2b` |

Por tanto, este cierre no cambia Lexer ni Parser.

## CI remoto y veredicto

En el momento de crear este informe todavía no existía la rama remota ni una
pull request para este HEAD. En consecuencia, el CI remoto del nuevo ref estaba
**PENDIENTE DE PUBLICACIÓN / NO DEMOSTRADO** y no se presenta como verde. Debe
revisarse en la pull request sin fusionarla.

Aunque la reconciliación de refs y la integridad de Lexer/Parser quedan
demostradas, el gate dirigido de `usar` continúa rojo y el CI remoto aún no tiene
resultado verificable. Veredicto: **NOT_READY_FOR_MERGE**.
