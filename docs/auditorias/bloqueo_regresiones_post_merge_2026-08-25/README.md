# Bloqueo de auditoría de regresiones post-merge — 2026-08-25

## Alcance

Esta comprobación aplica el criterio de causalidad solicitado antes de corregir un
fallo: el mismo node ID debe pasar en `origin/fix/contrato-extensiones-cobra` y
fallar en el HEAD posterior a integrar `origin/master`.

Los nombres remotos no están disponibles en este checkout. Se usaron los SHAs
inmutables ya documentados por la auditoría pre-merge:

- base: `c756151e87c751d3246ea5d03845ab7c9211ba09`;
- master: `f684efc8a21d60eebcdce113cc8bfc21240ca37e`;
- HEAD examinado: `2e1643c12fce268c15d3af249f4ca2a6428968ca`.

## Ausencia del estado post-merge requerido

La comprobación de ancestry devuelve `0` para la base y `1` para master:

```console
git merge-base --is-ancestor c756151e87c751d3246ea5d03845ab7c9211ba09 HEAD
git merge-base --is-ancestor f684efc8a21d60eebcdce113cc8bfc21240ca37e HEAD
```

Por tanto, la base sí es ancestro de HEAD, pero `origin/master` no lo es. El HEAD
recibido no constituye el estado posterior a la integración que exige la
comparación.

Además, este comando termina con código `0`:

```console
git diff --quiet c756151e87c751d3246ea5d03845ab7c9211ba09..HEAD -- src tests
```

No hay ninguna diferencia en código productivo ni pruebas entre la base y HEAD.
El diff completo desde la base contiene exclusivamente documentación de auditoría.

## Resultado nominal y contraste focal

La suite nominal en HEAD terminó con:

```text
515 failed, 4407 passed, 54 skipped, 31 warnings, 3 errors in 557.19s
```

Ese resultado no demuestra por sí mismo que los fallos sean nuevos. Para comprobar
la causalidad se eligió uno de los node IDs informados como fallido y se ejecutó en
worktrees separados, sin modificar ninguno de los dos árboles:

```console
python -m pytest -q tests/integration/test_run_repl_equivalence.py::test_misma_secuencia_semantica_equivale_entre_run_y_repl
```

| Árbol | Resultado |
|---|---|
| `c756151e87c751d3246ea5d03845ab7c9211ba09` | `1 passed in 1.26s` |
| `2e1643c12fce268c15d3af249f4ca2a6428968ca` | `1 passed in 1.22s` |

El fallo observado dentro de la suite completa no se reproduce aisladamente en
ninguno de los dos estados. Esto es compatible con contaminación por orden o estado
global, pero no autoriza a clasificarlo como regresión de `origin/master`.

## Decisión

**BLOCKED: falta el árbol post-merge.** No existe una causa raíz atribuible a la
integración de `origin/master` que pueda corregirse con la evidencia disponible.
Modificar runtime, pruebas, Lexer, Parser o sintaxis en este punto abordaría deuda
histórica o un problema no relacionado, contra el alcance solicitado.

Antes de continuar debe proporcionarse un HEAD que contenga realmente
`f684efc8a21d60eebcdce113cc8bfc21240ca37e` como ancestro (o el SHA exacto del árbol
post-merge equivalente). Entonces se podrá repetir la comparación por node ID y
resolver una sola causa raíz demostrada por commit.
