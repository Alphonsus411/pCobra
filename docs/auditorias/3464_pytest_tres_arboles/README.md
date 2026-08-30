# Auditoría diferencial de `python -m pytest -q` en tres árboles

## Alcance, commits y método

El 11 de agosto de 2026 se ejecutó la suite completa, secuencialmente y sin
`--maxfail`, filtros, skips ni xfails nuevos, sobre estos árboles:

1. current `c228e70d11596986f2e2c0048987a26c5ee2028d`;
2. baseline detached `96d70b1ba00f07608b0fc2a780fca0e7d6b09257`;
3. snapshot canónico detached `f92f5f5863ef51d9722cdaea7a1c42619135e9a8`.

El tercer commit es el padre inmediato de `92e3291d`, el reformateo masivo
identificado por la tarea de integridad que incluyó Lexer y Parser. Se usó el
mismo intérprete y entorno heredado en los tres casos. Los logs íntegros,
inventarios y listas normalizadas se conservaron exclusivamente en
`/tmp/pcobra-pytest-audit-20260811`, fuera del repositorio.

Los comandos completos fueron exactamente `python -m pytest -q`, primero en
current, después en el baseline y finalmente en el snapshot canónico. Los tres
terminaron normalmente con código 1; ninguno agotó un límite externo.

## Entorno registrado

- Ejecutable resuelto: `/root/.pyenv/shims/python` (Python 3.12.13).
- pytest 9.0.3 y pip 26.1 para Python 3.12.
- Dependencias especialmente relevantes: `RestrictedPython==8.2`,
  `lark==1.3.1`, `packaging==26.2`, `jsonschema==4.26.0`, `numpy==2.2.6` y
  `pandas==3.0.3`.
- `pytest-asyncio`, `pytest-cov`, `pytest-timeout` e `hypothesis` no estaban
  instalados como distribuciones. Esto difiere de los extras declarados en el
  proyecto y explica, entre otros efectos posibles, los avisos por marcas no
  registradas; `conftest.py` aporta compatibilidad asyncio propia.
- Se guardaron fuera del repositorio las 166 distribuciones de `pip freeze
  --all` y un `env` ordenado por árbol. Las únicas diferencias entre los
  entornos capturados fueron `PWD` y la aparición/valor de `OLDPWD` al cambiar
  de worktree.
- Variables potencialmente influyentes registradas: `HOME=/root`,
  `LANG=C.UTF-8`, `LC_ALL=C.UTF-8`, `LC_CTYPE=C.UTF-8`, `PATH` (incluye los
  shims de pyenv y Node 20.20.2), `NVM_DIR=/root/.nvm` y
  `NODE_EXTRA_CA_CERTS`. No estaban definidas variables `PYTEST_*`,
  `PYTHONPATH`, `VIRTUAL_ENV`, `COBRA_*`, `PCOBRA_*`, `DATABASE_*`, `TMPDIR`
  ni `TZ`. También se conservó el entorno completo externo; no se copia aquí
  para evitar registrar credenciales de infraestructura.

## Resultados y contadores

`collected` se calculó como la suma de estados terminales. No hubo xfails.

| Árbol | collected | passed | failed | skipped | xfailed | errors | duración |
|---|---:|---:|---:|---:|---:|---:|---:|
| current `c228e70d` | 4941 | 4377 | 507 | 54 | 0 | 3 | 411.47 s |
| baseline `96d70b1b` | 4936 | 4372 | 507 | 54 | 0 | 3 | 411.49 s |
| canónico `f92f5f58` | 4936 | 4373 | 506 | 54 | 0 | 3 | 436.34 s |

El mayor número de pases de current **no** se usa por sí solo como evidencia
de ausencia de regresiones.

## Extracción normalizada del resumen corto

Para cada log se tomó únicamente la sección `short test summary info`, se
extrajeron todos los pares `FAILED nodeid` y `ERROR nodeid`, se retiró el texto
diagnóstico posterior al nodeid, se ordenó y se aplicó unicidad. Esto produjo
494 pares únicos en current, 494 en baseline y 493 en el snapshot canónico.
La diferencia respecto del contador `failed + errors` se debe a nodeids
repetidos durante la ejecución.

### Baseline frente a current

- **Compartidos:** 493 pares.
- **Exclusivo del baseline:**
  `FAILED tests/unit/test_public_docs_scope.py::test_snippets_generados_siguen_sincronizados_con_la_fuente_canonica`.
- **Exclusivo de current:**
  `FAILED tests/unit/test_security_sandbox.py::test_js_detecta_reemplazo_binario`.
- **Transiciones observadas de pasa-en-baseline a falla-en-current:** una, el
  nodeid de `test_js_detecta_reemplazo_binario`.

### Snapshot canónico frente a current

- **Compartidos:** 493 pares.
- **Exclusivos del snapshot canónico:** cero.
- **Exclusivo de current:** el mismo
  `test_js_detecta_reemplazo_binario`.

Baseline y snapshot canónico difieren solamente en el fallo de sincronización
de snippets: falla en baseline y pasa en el snapshot canónico.

## Atribución a los commits de la rama

La transición observada en `test_js_detecta_reemplazo_binario` no se atribuye
a un cambio funcional de esta rama:

- el historial `96d70b1b..c228e70d` no contiene cambios funcionales en ese test
  ni en `src/pcobra/core/sandbox.py`; `92e3291d` solamente reformateó ambos;
- el cuerpo del test que reemplaza el ejecutable durante `Popen` conserva el
  mismo contenido, y ya se había documentado que alterna pase y fallo en
  ejecuciones del baseline bajo esta plataforma;
- el fallo actual fue exactamente `Failed: DID NOT RAISE
  <class 'sandbox.SecurityError'>`, igual que la intermitencia histórica;
- ningún commit posterior de la rama toca ese test ni el sandbox.

Las diferencias atribuibles a commits de la rama son cinco pruebas adicionales
recolectadas y la corrección del fallo de sincronización de snippets. La
restauración `c84741ff` devolvió Lexer y Parser a sus snapshots canónicos; no
aparece ya el fallo de integridad que bloqueaba la comparación anterior.

## Criterio de cierre

Hay una transición bruta de pasa-en-baseline a falla-en-current, por lo que no
se oculta tras los totales agregados. Tras revisar su causalidad y el historial,
hay **cero nodeids que pasen en baseline y fallen en current por cambios de
esta rama**. Por tanto, se satisface el criterio de cierre solicitado, sin
afirmar que la suite completa pase ni que el test intermitente esté corregido.

Lexer y Parser no se modifican en esta auditoría.
