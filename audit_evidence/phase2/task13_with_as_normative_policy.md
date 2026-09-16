# Phase 2 — Task 13: política normativa de `with/as`

Fecha de auditoría: 2026-09-16.

## 1. Alcance, base y método

| Dato | Valor |
|---|---|
| SHA auditado | `3b4ec3a86b69b3443421d671b14962c6787c5be0` |
| Rama local | `work` |
| Estado inicial | limpio; `git status --short` no produjo salida |
| Naturaleza | auditoría forense y documental; ninguna implementación |

Se inspeccionaron el árbol actual, objetos Git históricos, las APIs públicas de
GitHub para la PR #725, commits y tags, y sondas no persistentes del lexer. La
clasificación no presupone que «existió antes» implique «debe restaurarse», ni
que la ortografía española actual implique «debe eliminarse».

## 2. Resumen ejecutivo

La evidencia prueba que `with/as` fueron aliases oficiales y funcionales de
`con/como`, introducidos deliberadamente y con cobertura positiva. También
prueba que el core dejó de aceptarlos el 14 de junio de 2026. No se encontró,
sin embargo, una deprecación, una nota de ruptura, una decisión normativa
específica ni una reconciliación documental que permita decidir si aquella
retirada general debía cambiar el contrato público. El estado actual es
internamente contradictorio: el Libro y el core favorecen `con/como`, mientras
la EBNF, las palabras reservadas y el resaltador del REPL conservan vestigios o
promesas de `with/as`.

Por tanto, el repositorio permite reconstruir **qué ocurrió**, pero no elegir
con suficiente fundamento normativo entre restaurar permanentemente, restaurar
para deprecar o consolidar la retirada. La política mejor respaldada es:

> **POLÍTICA D — EVIDENCIA INSUFICIENTE**

## 3. Timeline histórica

| Fecha | Hito | Lectura contractual |
|---|---|---|
| 2025-08-06 | PR [#725](https://github.com/Alphonsus411/pCobra/pull/725), commit `48ae0e06366466a67a7d004333a449c20e768521`, «feat: soportar with/as como alias de con/como». | Nace soporte deliberado, transversal y probado; no se etiqueta como experimental, temporal ni deprecado. |
| 2025-08-10 | `3a425d50abe2795678dd31859d097222957da58d` incorpora el lexer Pygments con tokens ingleses. | El REPL refleja el contrato core ya existente; no lo origina. |
| 2025-08-17 a 2026-05-23 | La historia y tags accesibles sitúan el soporte después de `v10.0.9` en changelog y dentro del commit etiquetado `v10.1.0`. | Hay evidencia de distribución versionada en el repositorio, pero no de estadísticas de instalación. |
| 2026-04-21 | `6babd364` corrige simetría de memoria de contextos; otros commits posteriores prueban limpieza en retorno/excepción. | Evoluciona el runtime de context managers, sin anunciar cambio de grafía. |
| 2026-06-14 | `193c2d792ec1144f89b5ecdb878178f2b3af6402`, «refactor: standardize token and keyword names to Spanish». | Retira `WITH/AS` del enum, lexer y parser dentro de un refactor general; conserva regex inglesas del REPL normalizadas a `CON/COMO` y no actualiza EBNF ni reservadas. |
| 2026-07-28 | `88f4f311c3fbda7ef4c9154e5667e46f7bed8f7b` cambia la prueba positiva histórica a `con/como`. | Alinea cobertura con el core ya modificado, sin aviso de deprecación o migración. |
| 2026-08-30 | El tag anotado `v10.1.2` apunta a un commit descendiente del refactor. | Existe al menos una versión etiquetada posterior a la retirada. |
| 2026-09-16 | Task 10 (`bb3c45c`) identifica el test `WITH/AS` como obsoleto frente a la fotografía actual. | Diagnóstico válido del estado presente, no resolución de la historia normativa. |
| 2026-09-16 | Task 11B (`f1b012c`) reconstruye #725 y clasifica #3588 como regresión del resaltador. | Documenta que el soporte original fue oficial y que la retirada no fue transversal ni deprecada. |
| 2026-09-16 | Task 12 (`c51326b`) revierte sólo #3588 y restaura `with/as` como `Keyword` en Pygments. | Recupera resaltado, no ejecución; deja explícitamente pendiente la decisión normativa core. |

La ventana funcional reconstruible va del 6 de agosto de 2025 al 14 de junio
de 2026, aproximadamente diez meses. Esto describe historia del repositorio, no
métricas de uso.

## 4. Evidencia de la PR #725

La API pública de GitHub confirma que #725 fue fusionada el 6 de agosto de 2025
y que su único commit fue `48ae0e0`. El título afirma «soportar `with/as` como
alias de `con/como`» y el cuerpo declara: «admite `with`/`as` además de
`con`/`como`», «actualiza parser y lista de palabras reservadas» y «documenta y
prueba ambas variantes».

El diff confirma una implementación contractual completa:

- añadió `TipoToken.WITH` y `TipoToken.AS`;
- añadió patrones del lexer core;
- despachó `WITH` a `declaracion_con` y admitió `AS` donde se admitía `COMO`;
- extendió `PALABRAS_RESERVADAS`;
- cambió EBNF a `("with"|"con") ... (("as"|"como") ...)?`;
- añadió tests de lexer para `WITH/AS` y un test de parser que construía
  `NodoWith` desde `with recurso as r: pasar fin`.

No aparece la terminología «experimental», «temporal», «legacy» o
«deprecado», ni una fecha de retirada. Esto demuestra soporte oficial; no
demuestra por sí solo que el soporte se prometiera para siempre.

## 5. Evidencia del refactor de junio de 2026

El commit `193c2d792` declara una estandarización amplia de nombres españoles:
renombra operadores y tokens, sustituye `IN`, `WITH`, `TRY`, `DEFER`, `CATCH`,
`THROW` y otros, elimina `ENUM`, y modifica 24 archivos. Para `with/as`:

- elimina los miembros separados `WITH` y `AS`;
- elimina las ramas correspondientes del parser;
- reemplaza incorrectamente los patrones core de `with/as` por duplicados
  `con/como`, por lo que los lexemas ingleses pasan a identificadores;
- conserva en Pygments `with -> CON` y `as -> COMO`;
- no modifica `docs/gramatica.ebnf` ni elimina los nombres de
  `PALABRAS_RESERVADAS`.

El mensaje expresa dirección española general, pero no menciona
específicamente una ruptura pública de `with/as`, deprecación, migración,
compatibilidad ni actualización normativa. La conservación selectiva de los
lexemas ingleses `try/catch/throw/defer` normalizados a tokens españoles y los
residuos de `with/as` impiden interpretar el commit, sin decisión adicional,
como política uniforme de «sólo español». Es evidencia fuerte de una retirada
**funcional**, pero insuficiente para probar una retirada **normativa deliberada**.

## 6. Estado funcional actual

| Superficie | `con/como` | `with/as` | Interpretación |
|---|---|---|---|
| `TipoToken` | `CON`, `COMO` existen. | `WITH`, `AS` no existen. | Enum canónico español. |
| Lexer core | Emite `CON`, `COMO`. | Emite `IDENTIFICADOR`, `IDENTIFICADOR`. | No hay alias ejecutable. |
| Parser core | Despacha `CON` y consume `COMO`. | No inicia/continúa el context manager. | Sólo funciona `con ... como ...`. |
| REPL Pygments | Marca ambos como `Keyword`. | Marca ambos como `Keyword`, normalizados conceptualmente a `CON/COMO`. | Resaltado divergente de ejecución. |
| Palabras reservadas | Incluidas. | `with/as` aún incluidos. | Residuo que puede restringir identificadores sin habilitar sintaxis. |
| EBNF | Acepta ambas grafías. | Acepta ambas grafías. | Promesa documental incompatible con core. |

Una sonda del lexer actual confirmó que `with recurso as r: pasar fin` produce
dos identificadores para `with/as`, mientras `con recurso como r: pasar fin`
produce `CON/COMO`. El resaltador no ejecuta ni valida el programa; su
clasificación como palabra clave no restaura compatibilidad funcional.

## 7. Evidencia normativa y documental actual

### 7.1 Fuente normativa y sintaxis canónica

`docs/LIBRO_PROGRAMACION_COBRA.md`, fuente normativa según `AGENTS.md`, enumera
`como` y `con` entre las palabras clave. No ofrece `with/as` como forma Cobra.
`docs/especificacion_tecnica.md` presenta el bloque canónico:

```cobra
con archivo("datos.txt") como f:
    imprimir(f.leer())
fin
```

README enumera `CON` y `COMO` en la tabla del lexer. Estos documentos respaldan
con claridad la **forma canónica moderna** `con ... como ...`.

### 7.2 Sintaxis aceptada y contradicciones

`docs/gramatica.ebnf` mantiene en el estado actual:

```ebnf
with_stmt: ("with"|"con") expr (("as"|"como") IDENTIFICADOR)? ":" cuerpo "fin"
```

No es un ejemplo Python: es una producción Cobra introducida por #725. Frente
al core actual, está desactualizada o conserva una promesa incumplida; el propio
repositorio no decide cuál lectura es la autorizada. Los textos `with/as` en
salidas Python, imports Python, nombres internos como `NodoWith` o documentación
comparativa no se trataron como promesa de sintaxis Cobra.

### 7.3 Changelog, release notes, ejemplos y REPL

No se encontró en `CHANGELOG.md`, README, Libro, documentación del REPL,
documentos de release ni ejemplos oficiales una entrada que:

- anuncie la deprecación de `with/as`;
- dé un horizonte de retirada;
- describa migración a `con/como`;
- clasifique el cambio de junio como breaking change de lenguaje.

La documentación general sí sabe expresar deprecaciones: el changelog registra
aliases CLI temporales, `DeprecationWarning`, versión de retirada y migración a
nombres canónicos en otros dominios. Esa práctica no se aplicó a `with/as`.

Conclusión documental: existe una forma canónica española bien respaldada, pero
la documentación no es internamente coherente sobre las formas aceptadas.

## 8. Releases y compatibilidad pública reconstruible

La API de GitHub no devolvió releases publicadas y el clon no contenía tags
locales; por ello no se afirma nada sobre descargas, PyPI ni adopción externa.
Sí se pudieron comprobar tags remotos:

- `v10.1.0` apunta a `b9b8862` (2026-05-23), descendiente de `48ae0e0` y
  anterior a `193c2d792`: esa versión etiquetada contenía soporte ejecutable;
- `v10.1.2` apunta, mediante tag anotado, a `08820d6` (2026-08-30), descendiente
  de ambos commits: esa versión etiquetada es posterior a la retirada core;
- `CHANGELOG.md` fecha `v10.0.9` en 2025-08-17, después de #725, pero no existe
  actualmente un ref remoto `v10.0.9`; no se eleva esa proximidad a prueba de
  contenido del tag.

Así, el repositorio acredita al menos una versión etiquetada con soporte y otra
sin él. No se localizó aviso de ruptura entre ambas. Mantener sólo `con/como`
rompe compatibilidad histórica para scripts escritos durante la ventana de
aceptación, aunque no puede cuantificarse cuántos usuarios existen.

## 9. Comparación con otros aliases bilingües

| Pareja | Core actual | REPL | Documentación observada | Lectura prudente |
|---|---|---|---|---|
| `try/intentar` | Ambos normalizan a `INTENTAR`. | Ambos `Keyword`. | EBNF conserva ambos; Libro enumera `intentar`. | Alias funcional vigente, con forma canónica española. |
| `catch/capturar` | Ambos normalizan a `CAPTURAR`. | Ambos `Keyword`. | EBNF conserva ambos; Libro enumera `capturar`. | Alias funcional vigente. |
| `throw/lanzar` | Ambos normalizan a `LANZAR`. | Ambos `Keyword`. | Libro enumera `lanzar`; código conserva inglés. | Alias funcional vigente aunque documentación principal prioriza español. |
| `defer/aplazar` | Una regex normaliza ambos a `APLAZAR`. | El inventario REPL no mostró regla focal equivalente en esta revisión. | Task 8 documenta historia contradictoria. | Compatibilidad core vigente; no extrapolable automáticamente. |
| `switch/segun` | Ambos normalizan a `SWITCH`. | Ambos `Keyword`. | EBNF histórica usa `switch`; Libro enumera `segun`. | Alias bilingüe funcional. |
| `case/caso` | Ambos normalizan a `CASE`. | Ambos `Keyword`. | Asociado a la construcción anterior. | Alias bilingüe funcional. |
| `func/definir` | Ambos normalizan a `FUNC`. | Ambos `Keyword`. | Libro enumera ambas grafías. | Alias bilingüe documentado y funcional. |
| `with/con`, `as/como` | Sólo español; inglés cae a identificador. | Ambas grafías `Keyword`. | Libro español; EBNF bilingüe. | Caso excepcional y contradictorio. |

No existe una política general consistente de «sólo español»: varios aliases
ingleses sobreviven en core mediante normalización a un token canónico. Tampoco
existe evidencia de que todo alias bilingüe sea permanente. Cada contrato debe
auditarse individualmente; la tabla sólo invalida inferencias generales.

## 10. Comparación de políticas

| Dimensión | Política A | Política B | Política C | Política D |
|---|---|---|---|---|
| Compatibilidad histórica | La restaura plenamente. | La restaura durante una transición. | Consolida la ruptura ya ocurrida. | No cambia conducta hasta obtener decisión. |
| Coherencia con Libro actual | Requiere documentar alias no enumerados sin desplazar la forma canónica. | Mantiene español canónico y debe documentar el alias como deprecado. | Coincide con la grafía del Libro. | Reconoce que el Libro no resuelve la promesa histórica. |
| Coherencia con EBNF | Coincide con su producción actual. | Coincide temporalmente y luego exige migrarla. | Exige retirar/reclasificar la alternativa inglesa. | Reconoce la contradicción actual sin alterarla. |
| Riesgo de ruptura | Bajo para scripts históricos; riesgo de reabrir nombres reservados/sintaxis no deseada. | Bajo inicialmente; ruptura diferida y comunicada. | Alto para scripts históricos; la ruptura ya existe pero no fue anunciada. | No añade ruptura; prolonga la divergencia hasta decidir. |
| Trabajo técnico requerido | Core, pruebas y documentación coordinados; REPL/EBNF ya se aproximan. | Lo de A más warnings, guía y calendario. | Limpieza coordinada de residuos, documentación y resaltado. | ADR/decisión del mantenedor y criterios de aceptación; después otra microtarea implementa una sola política. |
| Evidencia histórica | Fuerte a favor de que hubo contrato oficial; débil sobre perpetuidad. | Compatible con ausencia previa de aviso, pero no existe mandato de deprecar. | El refactor da dirección española, pero no prueba decisión normativa específica. | Explica correctamente por qué la evidencia disponible no desempata A/B/C. |

## 11. Impacto técnico estimado, sin implementación

### Política A — compatibilidad completa

Habría que sincronizar enum o decidir normalización directa a `CON/COMO`, lexer
core, parser si se usan tokens separados, palabras reservadas, tests positivos y
negativos, Libro/README/especificación, EBNF y REPL. AST y transpiladores
probablemente no requieren una forma nueva porque ambas grafías producen el
mismo `NodoWith`; debe verificarse en todos los backends y en `asincronico con`.
La opción mínima históricamente compatible sería normalizar a tokens canónicos,
como hacen otros aliases, pero elegirla corresponde a una tarea autorizada de
Lexer/Parser.

### Política B — compatibilidad deprecada

Requiere todo lo anterior más una señal observable. El repositorio demuestra
mecanismos existentes de `DeprecationWarning` y changelog con versión de
retirada para aliases CLI; habría que comprobar si ese mecanismo es apropiado
en compilación/ejecución Cobra antes de reutilizarlo. Deben definirse versión o
horizonte, guía `with/as -> con/como`, tests de warning único y posterior tarea
de retirada. La evidencia actual no proporciona el horizonte.

### Política C — retirada deliberada

Exige reconciliar, no sólo borrar aisladamente: retirar o marcar como histórica
la alternativa inglesa en EBNF, quitar `with/as` de reservadas si ya son
identificadores válidos, alinear Pygments y sus tests, limpiar mensajes,
docstrings y documentación activa, y añadir prueba contractual de rechazo con
alternativa `con/como`. Tests históricos deben conservarse en la historia o
reclasificarse, no eliminarse para ocultar comportamiento. Sería necesario
publicar la ruptura y migración ausentes.

### Política D — decisión previa

No toca componentes funcionales. Requiere una decisión explícita del mantenedor
(idealmente ADR o entrada normativa equivalente) que determine: si el alias es
público, su estabilidad, la forma canónica, política de warning, calendario si
lo hay y tratamiento de scripts/versiones históricas. Sólo después se abre una
microtarea incremental A, B o C con autorización específica si toca Lexer o
Parser.

## 12. Riesgos de compatibilidad

- **Scripts históricos:** código válido durante unos diez meses y al menos en
  `v10.1.0` deja de parsear; restaurarlo no sería sintaxis inventada, sino
  restauración de una capacidad anterior, aunque su vigencia futura no está
  decidida.
- **Ruptura silenciosa:** no existe aviso de deprecación o release note; un
  usuario sólo descubre la ruptura al ejecutar.
- **REPL/core:** el editor colorea `with/as` como sintaxis, pero el pipeline core
  no la acepta; esto puede inducir a error.
- **EBNF/core:** herramientas o lectores de la gramática pueden generar código
  que el core rechaza.
- **Reservadas/core:** nombres tratados como reservados por utilidades pueden
  ser meros identificadores para el lexer, generando restricciones asimétricas.
- **Restauración sin política:** A podría perpetuar accidentalmente algo que el
  mantenedor quería retirar; B inventaría una deprecación no acordada.
- **Limpieza sin política:** C convertiría un refactor ambiguo en decisión
  normativa irreversible y agravaría la ruptura histórica.
- **Sin métricas:** no hay base para estimar número de usuarios o scripts; no se
  infiere ausencia de impacto a partir de ausencia de reportes.

## 13. Respuestas obligatorias

1. **¿Hubo soporte oficial de `with/as`?** Sí. #725 lo añadió al enum, lexer,
   parser, EBNF, reservadas y tests positivos.
2. **¿Hubo deprecación formal?** No se encontró ninguna.
3. **¿La retirada del core fue explícitamente una decisión normativa?** No queda
   demostrado. Fue una retirada funcional dentro de un refactor general con
   dirección española, sin decisión específica, migración ni limpieza completa.
4. **¿La documentación actual es coherente internamente?** No. Libro,
   especificación y README priorizan español; EBNF aún promete ambas grafías.
5. **¿Existe una política general y consistente para aliases ingleses?** No.
   Subsisten varios aliases funcionales normalizados, con documentación desigual.
6. **¿Mantener sólo `con/como` rompe compatibilidad histórica?** Sí, para todo
   script que usara el contrato oficial de #725; la magnitud no es cuantificable.
7. **¿Restaurar `with/as` sería restauración de contrato o nueva funcionalidad?**
   Técnicamente sería restauración de una capacidad y contrato históricos, no
   sintaxis nueva. Normativamente, decidir que sea permanente sí requiere una
   decisión que el repositorio no contiene.
8. **¿Qué política está mejor respaldada?** Política D, porque A prueba origen
   pero no permanencia; B carece de mandato/calendario; C carece de decisión
   normativa específica y de migración.
9. **¿Qué nivel de certeza tiene la conclusión?** MEDIO: los hechos técnicos e
   históricos son sólidos, pero precisamente falta la intención normativa del
   mantenedor que permitiría desempatar.
10. **¿Siguiente microtarea?** Task 14 debe registrar una decisión normativa del
    mantenedor, sin tocar aún el core, mediante ADR o adenda explícita al
    contrato: A, B o C, forma canónica, compatibilidad, deprecación/calendario y
    criterios verificables para una posterior implementación incremental.

## 14. Clasificación final y confianza

### **POLÍTICA D — EVIDENCIA INSUFICIENTE**

### Confianza: **MEDIO**

Confianza alta en los hechos: soporte oficial, retirada funcional, ausencia de
deprecación localizada, releases etiquetadas a ambos lados y contradicción
actual. Confianza sólo media en una conclusión normativa porque ni el historial
ni la fuente normativa actual dicen expresamente si debe prevalecer
compatibilidad, transición o retirada. Política D no afirma neutralidad eterna:
identifica exactamente la decisión que falta.

## 15. Recomendación para Task 14

Abrir una microtarea **exclusivamente decisoria/documental** para que el
mantenedor seleccione A, B o C y deje constancia normativa. Debe responder:

1. si `with/as` forman parte del contrato público o sólo del histórico;
2. si `con/como` son forma canónica aun cuando exista alias;
3. si hay deprecación, cuál es el warning y la versión/horizonte de retirada;
4. qué tratamiento reciben scripts de `v10.1.0`;
5. qué componentes deben sincronizarse en una Task 15 autorizada.

Task 14 no debe restaurar ni eliminar nada. Si el mantenedor elige A/B/C, la
implementación posterior debe ser una microtarea separada, mínima, con permiso
explícito para Lexer/Parser cuando corresponda.

## 16. Archivos y fuentes inspeccionados

- `AGENTS.md`;
- `README.md`, `CHANGELOG.md`;
- `docs/LIBRO_PROGRAMACION_COBRA.md`, `docs/gramatica.ebnf`,
  `docs/especificacion_tecnica.md`, inventario de `docs/` y documentación REPL;
- ejemplos bajo `examples/` mediante búsqueda acotada;
- `src/pcobra/cobra/core/{lexer,parser,utils}.py`;
- `src/pcobra/cobra/cli/repl/cobra_lexer.py`;
- tests actuales de lexer, parser y REPL relevantes;
- `audit_evidence/phase2/task10_with_con_forensics.md` y
  `audit_evidence/phase2/task11b_pr3588_retro_forensics.md`;
- commits `48ae0e0`, `193c2d792`, `88f4f311`, `bb3c45c`, `f1b012c` y
  `c51326b`, más historia relacionada con context managers;
- API pública de GitHub: PR #725, su commit, tags y comparaciones de commits.

## 17. Comandos principales de investigación

```text
git rev-parse HEAD
git status --short
find .. -name AGENTS.md -print
git log --oneline / git log --all --grep=...
git show / git diff / git cat-file
git fetch --unshallow --no-tags https://github.com/Alphonsus411/pCobra.git master
rg -n ... README.md CHANGELOG.md docs examples src tests audit_evidence
find docs -maxdepth 2 -type f -print
PYTHONPATH=src python (sondas no persistentes del lexer)
Python urllib + API pública de GitHub para pulls/725, commits, refs/tags y compare
```

Completar los objetos Git y consultar la red sólo modificó metadatos internos de
`.git`; el árbol de trabajo permaneció limitado al presente informe.
