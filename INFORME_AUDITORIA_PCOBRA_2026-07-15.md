# Informe de auditoría pCobra — 2026-07-15

Este documento registra los hallazgos priorizados para corrección incremental. El libro de programación (`docs/LIBRO_PROGRAMACION_COBRA.md`) es la fuente normativa de sintaxis y comportamiento del lenguaje; este informe no introduce sintaxis nueva ni modifica las reglas del lenguaje.

## Alcance y reglas de intervención

- No modificar Lexer ni Parser para estos hallazgos salvo autorización explícita.
- No añadir tokens, palabras reservadas, reglas gramaticales, aliases ni sintaxis Cobra inventada.
- Resolver los hallazgos uno por uno, con cambios mínimos y pruebas de regresión.
- Mantener intacto el proceso anfitrión al ejecutar código Cobra.
- Aplicar límites de recursos únicamente dentro de procesos hijos descartables.

## F-01: límites de recursos aplicados al proceso anfitrión

**Prioridad:** 1  
**Estado:** corregido en la rama de trabajo.  
**Área:** runtime / sandbox / CLI-REPL-IDLE.  

### Hallazgo

Las utilidades públicas de límites de recursos podían aplicar `RLIMIT_AS` y `RLIMIT_CPU` sobre el proceso que las invocaba. En flujos de CLI, REPL, IDLE o tests, ese comportamiento contamina el proceso anfitrión y puede dejarlo con límites irreversibles durante la sesión.

### Comportamiento esperado

Los límites efectivos de memoria y CPU deben configurarse sólo dentro de procesos hijos descartables. El proceso anfitrión debe limitarse a validar parámetros y a delegar la ejecución aislada.

### Causa raíz

La aplicación de límites estaba acoplada a funciones públicas reutilizables desde el anfitrión. Además, existían puntos de aplicación directa de `resource.setrlimit` en la sandbox en vez de una abstracción explícita para procesos hijos.

### Corrección recomendada

- Separar validación de límites y aplicación efectiva.
- Mantener las funciones públicas como compatibilidad segura sin mutar el anfitrión.
- Centralizar la aplicación real en una función interna documentada para `preexec_fn` o workers ya aislados.
- Cubrir con pruebas que `RLIMIT_AS` y `RLIMIT_CPU` del anfitrión permanecen intactos.
- Probar con programas Cobra reales ejecutados por la sandbox.

### Verificación esperada

- Reproducción previa de contaminación en proceso descartable.
- Pruebas unitarias de no contaminación del anfitrión.
- Pruebas de límites en subproceso hijo.
- Prueba de programa Cobra real con límites.
- Verificación de que Lexer y Parser no cambian.

## F-02: recursividad legítima detectada como ciclo

**Prioridad:** 2
**Estado:** corregido en la rama de trabajo.
**Área:** análisis/runtime.

### Hallazgo

El ejemplo oficial `examples/avanzados/funciones/factorial_recursivo.co` fallaba con `Recursive evaluation detected` al ejecutar una recursión legítima.

### Comportamiento esperado

Las funciones Cobra declaradas con `func` y que usan `retorno` deben poder invocarse recursivamente cuando tienen una condición de corte válida, sin que el runtime confunda la reutilización del cuerpo AST con un ciclo estructural.

### Causa raíz

La pila defensiva de evaluación usaba únicamente la identidad del nodo AST. Como el cuerpo de una función Cobra se reutiliza en cada llamada, el mismo nodo de `retorno n * factorial(n - 1)` reaparecía durante la llamada recursiva y se clasificaba erróneamente como ciclo.

### Corrección recomendada

- Mantener la detección de ciclos reales por identidad dentro de una misma invocación.
- Distinguir invocaciones recursivas legítimas mediante profundidad de llamada del runtime.
- Probar con el factorial recursivo oficial y conservar una prueba de ciclo AST real.

### Verificación esperada

- `examples/avanzados/funciones/factorial_recursivo.co` imprime `120`.
- Un AST cíclico construido manualmente sigue lanzando un error controlado sin `RecursionError`.
- Lexer y Parser permanecen sin cambios.

## F-05: divergencia semántica entre CLI, REPL e IDLE

**Prioridad:** 3
**Estado:** corregido parcialmente para la paridad CLI/REPL cubierta por contrato.
**Área:** ejecución / servicios compartidos.

### Hallazgo

La suite de contrato `tests/unit/test_cli_execution_pipeline_contract.py` fallaba antes de ejecutar los casos de paridad porque el adaptador legacy `ExecuteCommand` ya no exponía `validar_dependencias`, frontera que pruebas e integraciones históricas parchean para comparar script y REPL. Además, el contrato de bloque completo REPL necesitaba conservar una frontera observable estable al despachar bloques multilinea.

### Comportamiento esperado

Los mismos snippets Cobra deben producir salida, errores y estado final equivalentes entre la ruta script (`ExecuteCommand`/`RunService`) y la ruta REPL (`InteractiveCommand`) sin cambiar sintaxis ni gramática. El REPL debe acumular bloques completos antes de ejecutarlos y no parsear parcialmente línea a línea.

### Causa raíz

La migración de `ExecuteCommand` a `RunService` eliminó un símbolo legacy importable usado como frontera de compatibilidad. En la ruta REPL, los tests de contrato requerían comprobar simultáneamente que el texto completo del bloque se entrega a `ejecutar_codigo` y que se conserva el AST preparseado para no duplicar análisis ni romper recuperación de errores.

### Corrección aplicada

- Restaurar `validar_dependencias` como alias de compatibilidad en `execute_cmd` sin añadir una ruta de ejecución paralela.
- Mantener el despacho REPL de bloques completos con `ast_preparseado` y reforzar la prueba para validar ambas cosas.
- No tocar Lexer, Parser ni reglas gramaticales.

### Verificación esperada

- `tests/unit/test_cli_execution_pipeline_contract.py` pasa completo.
- Las pruebas de recuperación REPL que exigen `ast_preparseado` siguen pasando.
- Lexer y Parser permanecen sin cambios.

## F-06: falta de coherencia entre build y run

**Prioridad:** 4
**Estado:** corregido para la frontera pública `build` cubierta por contrato.
**Área:** pipeline de ejecución y construcción.

### Hallazgo

Las pruebas de contrato de `BuildCommandV2` no podían parchear `backend_pipeline.build` ni los mensajes públicos desde el módulo del comando, aunque `BuildService` ya era la implementación canónica. Esa deriva rompía la coherencia entre el comando público `build`, el servicio compartido y las pruebas que validan la misma ruta de resolución que `run`.

### Comportamiento esperado

`build` debe delegar en el pipeline canónico y validar runtime por la misma frontera pública estable, pero debe conservar puntos de parcheo compatibles para tests e integraciones del comando v2.

### Causa raíz

La migración a `BuildService` ocultó dependencias históricamente expuestas por `BuildCommandV2` (`backend_pipeline`, `mostrar_info` y runtime manager), de modo que el comando público y el servicio ya no compartían una frontera de contrato observable.

### Corrección aplicada

- Exponer `backend_pipeline`, `mostrar_info` y `mostrar_error` desde `build_cmd` como frontera de compatibilidad.
- Sincronizar esas referencias con `BuildService` antes de delegar, evitando duplicar la lógica de build.
- Mantener la validación de runtime en el `RuntimeManager` del servicio compartido.
- No tocar Lexer, Parser ni reglas gramaticales.

### Verificación esperada

- Los contratos de `BuildCommandV2` pueden parchear la frontera pública y pasan.
- El build de archivos UTF-8 con y sin BOM compila sin introducir token BOM.
- Lexer y Parser permanecen sin cambios.

## F-10: referencia inválida a INTERNAL_BACKENDS

**Prioridad:** 5
**Estado:** corregido para la política pública/documental cubierta por contrato.
**Área:** backends / política pública-interna.

### Hallazgo

Las pruebas documentales de superficie pública exigían que la política normativa explicara explícitamente que los backends retirados no forman parte del árbol operativo. Además, los snippets generados de política de targets estaban desincronizados con la fuente canónica.

### Comportamiento esperado

La documentación pública debe listar sólo los backends oficiales (`python`, `javascript`, `rust`) y cualquier mención a backends retirados debe quedar restringida a documentación histórica, rutas internas de migración o pruebas de rechazo.

### Causa raíz

`docs/targets_policy.md` no contenía la frase normativa requerida por el contrato documental y los bloques generados de targets no habían sido actualizados mediante el generador canónico.

### Corrección aplicada

- Añadir la regla explícita de que los backends retirados no forman parte del árbol operativo público.
- Regenerar los snippets públicos con `scripts/generate_target_policy_docs.py`.
- No ampliar la lista de backends públicos ni tocar Lexer/Parser.

### Verificación esperada

- Los tests documentales de política pública pasan.
- El linter de comandos públicos no detecta uso de `INTERNAL_BACKENDS`.
- Los snippets generados permanecen sincronizados.

## F-13: referencias mutables en la persistencia del REPL

**Prioridad:** 6
**Estado:** corregido para el estado mutable de sesión REPL.
**Área:** REPL / persistencia de estado.

### Hallazgo

La persistencia del REPL podía aceptar diccionarios de estado externos con listas mutables compartidas, permitiendo que una mutación posterior fuera de la sesión contaminara `buffer_lineas` u otros metadatos de control.

### Comportamiento esperado

La semántica incremental del REPL debe conservar variables y funciones del intérprete persistente, pero los metadatos de captura de entrada (`buffer_lineas`, profundidad de bloque y contadores) deben permanecer aislados por sesión/entrada.

### Causa raíz

`_estado_repl` se asignaba como diccionario directo, sin copia defensiva de las listas internas. Además, el control de líneas en blanco dependía sólo de `buffer_lineas`, por lo que un estado persistido que indicara `nivel_bloque > 0` podía omitir la política de bloque.

### Corrección aplicada

- Añadir un setter defensivo para `_estado_repl` que copia el diccionario y duplica listas mutables.
- Mantener la lectura interna del estado como referencia viva de la sesión activa para no romper la semántica incremental.
- Hacer que `_manejar_linea_blanca` respete tanto `buffer_lineas` como `nivel_bloque`.
- Actualizar pruebas REPL de fallback para el contrato actual basado en AST preparseado, sin reducir aserciones.
- No tocar Lexer, Parser ni reglas gramaticales.

### Verificación esperada

- Mutar un estado externo tras asignarlo al REPL no modifica el buffer interno.
- La persistencia de variables/funciones entre entradas se mantiene.
- Las suites relacionadas de REPL, paridad y recuperación de errores pasan.

## F-12: filtración de estado global y rutas de módulos

**Prioridad:** 7
**Estado:** corregido para cachés/pilas de `usar` en intérpretes independientes.
**Área:** imports / resolución de módulos.

### Hallazgo

La resolución de módulos de proyecto mediante `usar` compartía cachés y pila de carga globales entre instancias independientes de `InterpretadorCobra`, permitiendo que rutas y exports ya resueltos en una ejecución afectaran a otra.

### Comportamiento esperado

`usar "modulo"` debe resolver módulos Cobra de proyecto usando rutas lógicas seguras y mantener la semántica plana definida por el libro, pero cada ejecución/intérprete independiente debe aislar sus metadatos de resolución.

### Causa raíz

`InterpretadorCobra` guardaba referencias directas a `_USAR_PROJECT_MODULE_CACHE`, `_USAR_PROJECT_LOADING_STACK` y `_IMPORT_CO_AST_CACHE`. Además, la API de `usar_modulo` no permitía recibir estado de resolución aislado y algunos contratos legacy de parcheo dependían de superficies públicas históricas.

### Corrección aplicada

- Crear caché de módulos, pila de carga y caché de AST de import por instancia de `InterpretadorCobra`.
- Permitir que `usar_modulo` reciba `module_cache` y `loading_stack` opcionales, conservando la caché global sólo para llamadas directas legacy sin contexto de intérprete.
- Propagar el estado aislado a cargas anidadas para conservar detección de ciclos dentro de una misma ejecución.
- Mantener compatibilidad con wrappers/spies legacy y con el alias parcheable `CobraImportResolver`.
- Conservar el rechazo de módulos externos/no canónicos y permitir nombres simples de proyecto sólo si existe el `.co` correspondiente dentro de la raíz autorizada.
- No tocar Lexer, Parser ni reglas gramaticales.

### Verificación esperada

- Dos intérpretes independientes no comparten caché, pila ni caché AST de imports.
- La API directa de `usar_modulo` mantiene su comportamiento cacheado legacy cuando se usa sin intérprete.
- `cobra run` ejecuta un proyecto con `usar "util"` sin filtrar estado de otra ejecución.
- Las suites relacionadas de `usar`, rutas de proyecto y paridad REPL/script pasan.

## F-11: ciclos y duplicidad de imports

**Prioridad:** 8
**Estado:** corregido para `NodoImport` legacy y verificado para `usar`.
**Área:** imports.

### Hallazgo

`NodoImport` legacy cacheaba el AST de un módulo antes de ejecutarlo. Si durante esa ejecución se volvía a importar el mismo archivo a través de otro módulo, el AST cacheado podía reentrar sin detección propia de ciclo. Además, un import duplicado posterior reejecutaba side effects aunque el AST ya estuviera cacheado.

### Comportamiento esperado

Los imports deben mantener la sintaxis existente y la semántica documentada, pero las rutas ya importadas en una ejecución deben normalizarse como no-op y los ciclos reales deben fallar con un error explícito.

### Causa raíz

La caché `_import_ast_cache` sólo evitaba parseos repetidos; no registraba módulos en ejecución ni módulos ya ejecutados correctamente. La pila compartida con el loader detectaba ciclos durante la carga del AST, pero no cubría la reentrada producida al ejecutar un AST ya cacheado.

### Corrección aplicada

- Añadir `_import_execution_stack` por intérprete para detectar ciclos de ejecución de `NodoImport`.
- Añadir `_imported_module_paths` por intérprete para convertir imports duplicados exitosos en no-op.
- Mantener `NodoImport` separado de `usar_modulo` y sin aplicar la semántica pública/exportada de `usar`.
- Conservar la detección ya existente de ciclos de `usar` y las rutas canónicas relativas en mensajes.
- No tocar Lexer, Parser ni reglas gramaticales.

### Verificación esperada

- `a.co -> b.co -> a.co` mediante `NodoImport` falla con `Ciclo de módulos detectado en import`.
- Importar dos veces el mismo `.co` no reejecuta side effects.
- `usar` sigue detectando ciclos y normalizando duplicados por caché.
- Las suites relacionadas de imports/usar pasan.

## F-08: separación y saneamiento de las pruebas vigentes y legacy

**Prioridad:** 9
**Estado:** corregido para clasificación pytest de pruebas legacy/vigentes.
**Área:** tests.

### Hallazgo

La configuración de pytest no distinguía entre pruebas legacy realmente históricas/cuarentenables y pruebas vigentes que contienen `legacy` porque protegen compatibilidad, rechazo o ausencia de rutas antiguas. Esto impedía seleccionar explícitamente la cobertura sin mezclar ambos conceptos.

### Comportamiento esperado

La suite debe mantener todas las aserciones existentes, pero exponer una clasificación clara para ejecutar cobertura vigente, contratos vigentes sobre legacy y pruebas legacy explícitas sin borrar ni silenciar fallos.

### Causa raíz

Sólo existían marcadores genéricos (`slow`, `integration`, `experimental`, etc.). No había marcadores `legacy`/`legacy_contract` ni una regla de colección que separara contratos vigentes relacionados con legacy de pruebas históricas.

### Corrección aplicada

- Registrar los marcadores pytest `legacy` y `legacy_contract`.
- Clasificar automáticamente `tests/legacy/**` como `legacy`.
- Clasificar pruebas que mencionan `legacy` en ruta/nodeid como `legacy_contract` cuando no están marcadas explícitamente como `legacy`.
- Añadir pruebas de contrato para el clasificador.
- No eliminar pruebas, no añadir skips/xfails y no reducir aserciones.
- No tocar Lexer, Parser ni reglas gramaticales.

### Verificación esperada

- `pytest -m legacy_contract` puede seleccionar guardas vigentes relacionadas con legacy.
- `pytest -m 'not legacy'` conserva contratos vigentes sobre legacy.
- La clasificación está cubierta por pruebas unitarias.

## F-09: workflows configurados para una rama diferente

**Prioridad:** 10
**Estado:** corregido.
**Área:** CI.

### Diagnóstico

La rama activa del repositorio es `work`, pero varios workflows mantenían filtros `push`/`pull_request` fijados a `main`. Esto impedía que las comprobaciones asociadas se ejecutaran automáticamente sobre la rama real de trabajo.

### Corrección aplicada

Se alinearon únicamente los filtros de rama de los workflows afectados para apuntar a `work`, conservando disparadores manuales, tags y lógica de jobs existentes. No se modificó runtime, sintaxis, Lexer ni Parser.

### Verificación

Se añadió una prueba de regresión que comprueba que los workflows con filtros explícitos de rama apuntan a `work` y no conservan referencias a `main`.

## F-14: entorno virtual versionado

**Prioridad:** 11  
**Estado:** pendiente.  
**Área:** repositorio / empaquetado.  

Evitar versionar artefactos de entorno virtual.

## F-15: dependencias opcionales desalineadas

**Prioridad:** 12  
**Estado:** pendiente.  
**Área:** packaging.  

Alinear extras/dependencias opcionales con las rutas de ejecución reales.

## F-16: contrato SemVer incoherente

**Prioridad:** 13  
**Estado:** pendiente.  
**Área:** versionado.  

Normalizar el contrato de versión pública y documentación asociada sin cambiar sintaxis.

## F-17: snapshots y pruebas legacy desactualizados

**Prioridad:** 14  
**Estado:** pendiente.  
**Área:** tests / snapshots.  

Actualizar snapshots sólo cuando representen el comportamiento normativo vigente.

## F-03: ejecución de NodoPara

**Prioridad:** 15  
**Estado:** pendiente condicionado.  
**Área:** runtime.  

Sólo debe corregirse si la estructura actual del Parser ya contiene información suficiente para ejecutar `NodoPara` sin tocar Lexer ni Parser.

## F-04: modelo de objetos

**Prioridad:** 16  
**Estado:** pendiente condicionado.  
**Área:** runtime / objetos.  

Sólo debe corregirse si puede implementarse con la estructura AST existente.

## F-07: ejemplos oficiales

**Prioridad:** 17  
**Estado:** pendiente.  
**Área:** ejemplos.  

No cambiar sintaxis de ejemplos ni ocultar errores. Los ejemplos oficiales deben ejecutarse conforme al libro.
