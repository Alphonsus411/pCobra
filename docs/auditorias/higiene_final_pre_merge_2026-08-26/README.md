# Higiene final previa al merge — 2026-08-26

## Alcance y método

Esta ejecución es exclusivamente documental. El checkout inicial fue la rama
local `work`, en `2dc2dea53be7f77fa16a38057f91ec6cb6dbc2e4`, con el índice y los
archivos versionados limpios. No se ejecutó merge, rebase, reset, push ni se
cambió de rama. Tampoco se modificaron código productivo, dependencias,
pruebas, ejemplos, auditorías anteriores, Lexer, Parser, tokens, gramática ni
sintaxis.

El clon no tenía remotos y era superficial. Se restauró
`origin=https://github.com/Alphonsus411/pCobra.git`, se obtuvieron las ramas y
tags y se completó el historial con `git fetch --unshallow origin --tags
--prune`. Después de ello `git rev-parse --is-shallow-repository` devolvió
`false`; las relaciones que siguen se calcularon sólo sobre el grafo completo.

## SHA y relaciones remotas después de restaurar `origin`

```text
$ git rev-parse HEAD
2dc2dea53be7f77fa16a38057f91ec6cb6dbc2e4
$ git rev-parse origin/master
f684efc8a21d60eebcdce113cc8bfc21240ca37e
$ git rev-parse origin/fix/contrato-extensiones-cobra
2dc2dea53be7f77fa16a38057f91ec6cb6dbc2e4
$ git merge-base origin/master origin/fix/contrato-extensiones-cobra
8b1676cdf52f30147ce42584a98ca4c421756369
$ git rev-list --left-right --count origin/master...origin/fix/contrato-extensiones-cobra
1       339
$ git merge-base --is-ancestor origin/master origin/fix/contrato-extensiones-cobra
[código 1]
$ git merge-base --is-ancestor origin/fix/contrato-extensiones-cobra origin/master
[código 1]
```

`HEAD` y `origin/fix/contrato-extensiones-cobra` coinciden. Hay un commit
exclusivo de `origin/master` y 339 exclusivos de la rama de corrección. Ninguna
de las dos puntas es ancestro de la otra: la relación es **divergente**, no
fast-forward en ninguna dirección.

## Clasificación de ramas

| Referencia | Clasificación | Evidencia |
|---|---|---|
| `work` | checkout local de auditoría, sin upstream | único `refs/heads/*`; apunta a `2dc2dea5` |
| `origin/fix/contrato-extensiones-cobra` | punta remota auditada / rama candidata | coincide exactamente con `HEAD`; 339 commits exclusivos respecto de `master` |
| `origin/master` | base remota normativa, pendiente de integrar | un commit exclusivo; no es ancestro de la candidata |
| demás `refs/remotes/origin/*` | ramas remotas ajenas al alcance | se inventariaron 3.549 referencias remotas en total; no se auditaron ni modificaron |

Por tanto, `work` es sólo un alias local sin seguimiento, la rama candidata es
la punta remota efectiva y `origin/master` no está incorporada en ella.

## Inventario y clasificación de artefactos

### Árbol de trabajo

Antes de las comprobaciones no había cambios versionados ni no versionados. El
único artefacto ignorado preexistente era
`extensions/vscode/node_modules/`, clasificado como **dependencias locales
ignoradas, fuera del commit**. `compileall` creó directorios `__pycache__`
ignorados bajo `src/` y `pcobra/`; se clasificaron como **caché efímera de la
comprobación, fuera del commit** y se retiraron después de capturar el
resultado. No se generaron archivos versionados.

El inventario final del cambio contiene una sola ruta:

```text
docs/auditorias/higiene_final_pre_merge_2026-08-26/README.md
```

Clasificación: **informe de auditoría documental permitido**. El artefacto
ignorado `extensions/vscode/node_modules/` continúa fuera del diff y del
commit. No hay artefactos productivos, normativos, de pruebas, dependencias o
generados incluidos por esta ejecución.

### Diferencial histórico de la rama candidata

Para no confundir el commit documental con la deuda acumulada de la rama, se
inventarió además `origin/master...origin/fix/contrato-extensiones-cobra`:

| Dimensión | Resultado exacto | Clasificación |
|---|---:|---|
| rutas totales | 915 | diferencial histórico de la rama; no creado por esta ejecución |
| estados Git | 98 añadidas, 25 borradas, 770 modificadas, 22 renombradas | mezcla histórica |
| `tests/` | 460 | pruebas |
| `src/` | 239 | código productivo |
| `docs/` | 66 | documentación y auditorías |
| `scripts/` | 58 | herramientas |
| `examples/` | 52 | ejemplos |
| `.github/` | 24 | CI/configuración |
| resto | 16 | raíz, extensiones, notebooks y otros artefactos |

Ese diferencial incluye cambios históricos en `pyproject.toml` y
`extensions/vscode/package.json`; se clasifican como **dependencias/configuración
preexistentes de la rama**, no como cambios de esta auditoría. También aparecen
rutas cuyo nombre contiene `lexer`, `parser`, `token` o `grammar`, pero ninguna
fue tocada por esta ejecución; la integridad de los cuatro Lexer/Parser
canónicos se comprueba por hash a continuación.

## Tres comprobaciones focales

Se ejecutaron exactamente estas tres comprobaciones, sin suites adicionales:

### 1. Compilación de Python

```text
$ python -m compileall -q src
[sin salida]
[código 0]
```

Resultado: **PASS**.

### 2. Contrato de runtime

```text
$ python scripts/validate_runtime_contract.py
✅ Runtime contract validation: OK
   Runtime oficial: python, javascript, rust
   Verificación ejecutable: python, javascript, rust
   Runtime oficial con corelibs/standard_library mantenidos: python, javascript, rust
   Adaptador Holobit mantenido: python, javascript, rust
   Compatibilidad SDK completa: python
[código 0]
```

Resultado: **PASS**.

### 3. Sincronización del libro normativo

```text
$ python scripts/sync_libro_programacion.py --check
Sin drift documental.
[código 0]
```

Resultado: **PASS**.

## Integridad de Lexer y Parser

Los SHA-256 se calcularon antes de ejecutar las comprobaciones y se repitieron
después. Las dos columnas son idénticas:

| Archivo | SHA-256 antes | SHA-256 después |
|---|---|---|
| `src/pcobra/cobra/core/lexer.py` | `537554f0cab9fb4ca456b2b99a43fca7b275241dcddfa5bb0fc3dcad78534e70` | `537554f0cab9fb4ca456b2b99a43fca7b275241dcddfa5bb0fc3dcad78534e70` |
| `src/pcobra/cobra/core/parser.py` | `3017fa31e1707ca82358d548e71ba27d4b8e73342950ab6959b32c13dcc02505` | `3017fa31e1707ca82358d548e71ba27d4b8e73342950ab6959b32c13dcc02505` |
| `src/pcobra/core/lexer.py` | `fbd130d88ec6255c1e966752730a7cb2e2311c50125d85df487fc67d55aaf61e` | `fbd130d88ec6255c1e966752730a7cb2e2311c50125d85df487fc67d55aaf61e` |
| `src/pcobra/core/parser.py` | `656d9c911ab0760435efc48502625b6016955f00d0429228a0ffced87e982a2b` | `656d9c911ab0760435efc48502625b6016955f00d0429228a0ffced87e982a2b` |

Conclusión: **sin cambios en Lexer ni Parser**.

## Deuda histórica conocida

Esta ejecución focal no reinterpreta como regresiones los resultados ya
documentados sobre la misma línea de trabajo:

- suite global: **514 failed, 4408 passed, 54 skipped, 30 warnings y 3
  errors**; los 517 casos no satisfactorios coinciden con el baseline previo;
- batería focal de `usar`: **2 failed, 143 passed, 2 warnings**, con los dos
  fallos ya clasificados como `HISTORICAL_BASELINE`;
- calidad estática: **9 F821 de Ruff**, **2 archivos pendientes de Black** y
  **1.754 errores mypy en 273 archivos**;
- CI remoto previamente observado: `Lint` y el job `analyze` de CodeQL en
  fallo, con cuatro checks requeridos no reportados.

Las tres comprobaciones verdes de este informe no cancelan esa deuda ni
certifican la suite global, lint, Black, mypy, CodeQL o CI.

## Veredicto permitido

Veredicto: **NOT_READY_FOR_MERGE (BRANCH_DIVERGENCE_AND_KNOWN_BASELINE)**.

Es el único veredicto conservador permitido por la evidencia: aunque las tres
comprobaciones focales pasan y Lexer/Parser permanecen intactos,
`origin/master` conserva un commit no integrado, el merge no sería
fast-forward y persiste deuda histórica de pruebas, calidad y CI. En
consecuencia, este informe **no** declara `READY_FOR_MERGE`,
`READY_FOR_MERGE_WITH_KNOWN_BASELINE` ni `REMOTE_CI_PENDING`.
