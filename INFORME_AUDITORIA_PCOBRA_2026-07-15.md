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
**Estado:** pendiente.  
**Área:** análisis/runtime.  

La recursividad válida no debe confundirse con ciclos estructurales inválidos del AST o de estructuras internas. Cualquier corrección debe inspeccionar primero la estructura actual producida por el Parser y detenerse si requiere cambios gramaticales.

## F-05: divergencia semántica entre CLI, REPL e IDLE

**Prioridad:** 3  
**Estado:** pendiente.  
**Área:** ejecución / servicios compartidos.  

Los mismos programas Cobra deben conservar semántica equivalente entre los distintos frontends de ejecución, reutilizando servicios comunes sin alterar sintaxis.

## F-06: falta de coherencia entre build y run

**Prioridad:** 4  
**Estado:** pendiente.  
**Área:** pipeline de ejecución y construcción.  

`build` y `run` deben compartir contratos de validación y resolución cuando apliquen al mismo programa fuente.

## F-10: referencia inválida a INTERNAL_BACKENDS

**Prioridad:** 5  
**Estado:** pendiente.  
**Área:** backends / política pública-interna.  

Eliminar referencias públicas inválidas a backends internos sin ampliar la superficie pública.

## F-13: referencias mutables en la persistencia del REPL

**Prioridad:** 6  
**Estado:** pendiente.  
**Área:** REPL / persistencia de estado.  

La persistencia del REPL no debe compartir referencias mutables que permitan contaminación accidental entre entradas.

## F-12: filtración de estado global y rutas de módulos

**Prioridad:** 7  
**Estado:** pendiente.  
**Área:** imports / resolución de módulos.  

La resolución de módulos debe evitar estado global persistente entre ejecuciones independientes.

## F-11: ciclos y duplicidad de imports

**Prioridad:** 8  
**Estado:** pendiente.  
**Área:** imports.  

Los ciclos y duplicados deben detectarse o normalizarse sin cambiar la sintaxis de importación existente.

## F-08: separación y saneamiento de las pruebas vigentes y legacy

**Prioridad:** 9  
**Estado:** pendiente.  
**Área:** tests.  

Separar cobertura vigente de pruebas legacy sin eliminar aserciones para ocultar fallos.

## F-09: workflows configurados para una rama diferente

**Prioridad:** 10  
**Estado:** pendiente.  
**Área:** CI.  

Alinear workflows con la rama activa del repositorio sin modificar comportamiento runtime.

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
