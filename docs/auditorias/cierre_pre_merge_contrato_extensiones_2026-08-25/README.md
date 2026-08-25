# Cierre pre-merge del contrato de extensiones — 2026-08-25

## Identidad

- **Rama auditada:** `fix/contrato-extensiones-cobra`.
- **Fecha UTC de inicio:** `2026-08-25T12:37:02Z`.
- **SHA inicial:** `9d7f34f6447d23f114451564716ccf1ecb82ee41`.
- **SHA de `origin/master` consultado:** `f684efc8a21d60eebcdce113cc8bfc21240ca37e`.
- **SHA de `master` integrado:** no existe; la integración quedó bloqueada y el intento se abortó.
- **SHA final del código auditado:** `9d7f34f6447d23f114451564716ccf1ecb82ee41`; el único commit posterior es este informe documental.
- **Estado inicial:** árbol limpio; el checkout suministrado se llamaba `work`, sin remoto configurado. Se añadió `origin`, se actualizaron las refs y se creó la rama local solicitada en el mismo SHA.

## Sincronización y conflictos

`git merge --no-ff origin/master` fue rechazado porque Git considera que las ramas no tienen un ancestro común. Un intento diagnóstico con `--allow-unrelated-histories` produjo **770 conflictos `add/add`**. Los conflictos abarcan, entre otros, CodeQL, workflows, el libro normativo, matrices generadas, runtime, scripts contractuales y tests.

Resolver esa cantidad de conflictos no constituye una corrección mínima ni focal, y no permite conservar con evidencia suficiente el comportamiento de la rama. Conforme a la regla de detener una línea fuera de alcance y a la prohibición de reescrituras generales, se ejecutó `git merge --abort`. No quedó commit de merge.

## Archivos modificados y commits creados

- Código, tests, Lexer, Parser y auditorías históricas: **sin modificaciones**.
- Archivo nuevo: este `README.md` de cierre.
- Commits de corrección funcional: **0**.
- Commit documental: el commit que incorpora este informe.

## Integridad de Lexer y Parser

Hashes SHA-256 antes del intento, durante el conflicto y después de abortarlo (sin variación):

| Archivo | SHA-256 |
|---|---|
| `src/pcobra/cobra/core/lexer.py` | `537554f0cab9fb4ca456b2b99a43fca7b275241dcddfa5bb0fc3dcad78534e70` |
| `src/pcobra/cobra/core/parser.py` | `3017fa31e1707ca82358d548e71ba27d4b8e73342950ab6959b32c13dcc02505` |
| `src/pcobra/core/lexer.py` | `fbd130d88ec6255c1e966752730a7cb2e2311c50125d85df487fc67d55aaf61e` |
| `src/pcobra/core/parser.py` | `656d9c911ab0760435efc48502625b6016955f00d0429228a0ffced87e982a2b` |

### Comprobación posterior al merge documental

Se repitió la comprobación en `15ca90bd036aacd19ae42ac483caa525ded40184`,
después del merge documental, tomando como referencia
`origin/fix/contrato-extensiones-cobra` en
`c756151e87c751d3246ea5d03845ab7c9211ba09`. Los hashes recalculados coinciden
byte a byte con los cuatro valores previos de la tabla anterior:

| Archivo | SHA-256 posterior | Comparación con el hash previo |
|---|---|---|
| `src/pcobra/cobra/core/lexer.py` | `537554f0cab9fb4ca456b2b99a43fca7b275241dcddfa5bb0fc3dcad78534e70` | Coincide |
| `src/pcobra/cobra/core/parser.py` | `3017fa31e1707ca82358d548e71ba27d4b8e73342950ab6959b32c13dcc02505` | Coincide |
| `src/pcobra/core/lexer.py` | `fbd130d88ec6255c1e966752730a7cb2e2311c50125d85df487fc67d55aaf61e` | Coincide |
| `src/pcobra/core/parser.py` | `656d9c911ab0760435efc48502625b6016955f00d0429228a0ffced87e982a2b` | Coincide |

Asimismo, se ejecutó el diff limitado exactamente a esos cuatro paths:

```console
git diff origin/fix/contrato-extensiones-cobra...HEAD -- src/pcobra/cobra/core/lexer.py src/pcobra/cobra/core/parser.py src/pcobra/core/lexer.py src/pcobra/core/parser.py
```

La salida fue vacía. El `merge-base` de la comparación es
`c756151e87c751d3246ea5d03845ab7c9211ba09`, y el historial entre esa referencia
y `HEAD` tampoco registra commits que afecten a los cuatro paths. Por tanto, no
existe una diferencia previa introducida por `master` que deba atribuirse a un
commit remoto y no se activa la condición de detener esta certificación. No se
modificaron Lexer, Parser, gramática, tokens, precedencia ni sintaxis.

## Gates y pruebas

La fase 2 es un prerrequisito de los gates posteriores. Como `origin/master` no pudo integrarse, ejecutar las fases 3–10 sobre el árbol anterior no demostraría seguridad pre-merge y podría producir una conclusión engañosa.

| Gate | Estado | Motivo |
|---|---|---|
| Integridad básica post-merge | NOT DEMONSTRATED | No existe árbol post-merge. |
| Runtime Contract | NOT DEMONSTRATED | Sin integración verificable. |
| Syntax report / libro | NOT DEMONSTRATED | Sin integración verificable. |
| Contrato `usar` | NOT DEMONSTRATED | Sin integración verificable. |
| Holobit | NOT DEMONSTRATED | Sin integración verificable. |
| Runtime API | NOT DEMONSTRATED | Sin integración verificable. |
| CodeQL pytest / CLI | NOT DEMONSTRATED | Sin integración verificable. |
| Lint, typecheck y smoke | NOT DEMONSTRATED | Sin integración verificable. |
| Suite global | NOT DEMONSTRATED | `passed`, `failed`, `skipped` y `errors`: no disponibles. |

## Clasificación de fallos

- `HISTORICOS_QUE_SIGUEN`: no demostrable en esta ronda.
- `HISTORICOS_QUE_DESAPARECEN`: no demostrable en esta ronda.
- `FALLOS_NUEVOS`: no demostrable; no puede afirmarse que sea cero.
- Fallos históricos supervivientes exactos: **no demostrable**.
- Fallos nuevos exactos: **no demostrable**.

## CodeQL y riesgos residuales

CodeQL local y remoto no se evaluaron porque la integración previa quedó bloqueada. El riesgo residual principal es estructural: las refs conocidas representan historiales sin ancestro común y una unión forzada exige resolver 770 conflictos de alcance transversal. Cualquier evaluación contractual posterior sin corregir primero la procedencia del historial carecería de una base comparable fiable.

Se recomienda restaurar o publicar una ref de la rama que comparta el historial correcto con `master`, o proporcionar una estrategia de reconciliación explícita revisada por mantenedores. No debe intentarse resolver masivamente los conflictos bajo este encargo.

## Recomendación final

**NOT_READY_FOR_MERGE**
