# Cierre pre-merge del contrato de extensiones — 2026-08-25

## Identidad

- **Rama auditada:** `fix/contrato-extensiones-cobra` (checkout local `work`).
- **Fecha UTC de inicio del informe original:** `2026-08-25T12:37:02Z`.
- **SHA inicial:** `9d7f34f6447d23f114451564716ccf1ecb82ee41`.
- **SHA de `master` auditado:** `f684efc8a21d60eebcdce113cc8bfc21240ca37e`.
- **Ancestro común comprobado:** `8b1676cdf52f30147ce42584a98ca4c421756369`.
- **Merge de auditoría:** `5bc39e855` integra `f684efc8` sobre el informe documental sin conflictos.

## Corrección de la sincronización

La conclusión original de que los historiales no estaban relacionados era
incorrecta. El checkout era superficial y su fichero `.git/shallow` ocultaba la
ascendencia compartida. Después de configurar `origin` y ejecutar
`git fetch --unshallow origin`, las comprobaciones sobre los mismos SHA dieron:

```text
$ git merge-base 9d7f34f6 f684efc8
8b1676cdf52f30147ce42584a98ca4c421756369

$ git merge-tree --write-tree --messages 9d7f34f6 f684efc8
9d6ae7f5ce560d87fe8e1500ec6921dd482c320d
```

`git merge-tree` terminó con código 0 y sin mensajes de conflicto. A
continuación, `git merge --no-ff f684efc8` también terminó con código 0 mediante
la estrategia `ort`. El merge incorporó únicamente
`auditoria_contrato_extensiones_codigo.txt`; los 770 conflictos `add/add`
registrados antes fueron un artefacto del grafo local incompleto, no una
propiedad de los historiales del repositorio.

## Archivos modificados y commits creados

- El merge incorpora el archivo de evidencia
  `auditoria_contrato_extensiones_codigo.txt` procedente de `f684efc8`.
- Este seguimiento corrige únicamente el presente informe de auditoría.
- Lexer y Parser no se modificaron.

## Gates y pruebas posteriores al merge

| Gate | Estado | Evidencia |
|---|---|---|
| Descubrimiento de historia | **PASS** | El repositorio dejó de ser superficial; `merge-base` devolvió `8b1676cd`. |
| Integración | **PASS** | `merge-tree` y el merge real terminaron sin conflictos. |
| Compilación de `src` | **PASS** | `python -m compileall -q src`, código 0. |
| Runtime Contract | **PASS** | `python scripts/validate_runtime_contract.py`, código 0. |
| Syntax report | **PASS** | `python scripts/ci/validate_syntax_report_contract.py`, código 0. |
| Libro normativo | **PASS** | `python scripts/sync_libro_programacion.py --check`: `Sin drift documental.` |
| Runtime API / CodeQL pytest | **PASS** | 18 pruebas pasaron en los archivos focales de runtime y configuración CodeQL. |
| Contrato `usar` / Holobit | **FAIL** | 4 fallos y 85 pruebas pasadas; son discrepancias de mensajes de error en `usar`, no conflictos de integración. |
| Suite global | **FAIL / INCOMPLETA** | Se interrumpió al 26 % tras demostrar 35 fallos: 1268 pasadas y 23 omitidas. |

La suite dirigida que falla es:

```text
python -m pytest -q \
  tests/integration/test_usar_public_contract_regression.py \
  tests/integration/test_usar_core_contract_full.py \
  tests/integration/test_holobit_tiers.py

4 failed, 85 passed
```

Los cuatro fallos corresponden a expectativas sobre los diagnósticos
`usar_error[conflicto_simbolo]` y
`módulo externo no permitido en REPL estricto`. No se alteran en esta corrección
porque constituyen hallazgos funcionales independientes y la política del
repositorio exige tratarlos uno por uno.

## Clasificación corregida

- La historia compartida y la posibilidad de integrar quedaron **demostradas**.
- Los 770 conflictos `add/add` declarados en la versión anterior del informe no
  son fallos del repositorio y se retiran de la clasificación.
- La suite dirigida detectó cuatro fallos de diagnóstico de `usar`. La suite
  global también mostró otros fallos preexistentes antes de interrumpirse; el
  merge limpio de `f684efc8`, que sólo aporta evidencia documental, no los creó.
- CodeQL completo no se ejecutó localmente; sólo pasó su suite pytest focal, por
  lo que un análisis CodeQL integral queda **NOT DEMONSTRATED**.

## Recomendación final

La sincronización con `f684efc8` **no bloquea el merge**. La conclusión anterior
`NOT_READY_FOR_MERGE` por “historias sin relación” queda revocada. La decisión
global debe basarse en los gates funcionales pendientes descritos arriba, no en
conflictos de Git inexistentes.
