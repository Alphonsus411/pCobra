# Roadmap futuro: normalización incremental de formato

> Estado: **APARCADO**. Este documento no autoriza reformateos masivos ni
> cambios de sintaxis. Su finalidad es conservar una ruta mínima y reversible
> para resolver deuda de Black sin comprometer el Libro de Programación Cobra.

## Invariantes

- No modificar Lexer ni Parser sin autorización específica.
- No introducir tokens, aliases, reglas gramaticales ni cambios de sintaxis.
- No mezclar formato con reparaciones POO, runtime o backends.
- No reformatear snapshots, fixtures o ejemplos byte-a-byte sin una prueba que
  preserve su contrato.
- Cada tarea debe ser una PR aislada, con diff mecánico y verificable.
- El Libro de Programación Cobra continúa siendo la referencia normativa.

## Situación observada

El lint sobre archivos Python versionados detecta actualmente 33 archivos que
Black reformatearía. Entre ellos hay fuentes protegidas, pruebas y snapshots;
por tanto, una única ejecución automática de Black no es aceptable.

## Secuencia propuesta

### FMT-001 — Inventario inmutable de deuda

- Registrar la lista exacta de archivos que Black reformatearía, asociada a un
  SHA de master.
- Clasificar cada archivo: fuente ordinaria, test, fixture/snapshot,
  Lexer/Parser protegido.
- No modificar ningún archivo.

**Salida:** inventario reproducible, sin cambios de código.

### FMT-002 — Política de lint incremental

- Diseñar una comprobación que exija formato sólo para archivos Python
  modificados por una PR.
- Mantener el inventario histórico como deuda visible, no como exclusión
  silenciosa.
- Validar que un archivo nuevo o editado y mal formateado falla.

**Salida:** las contribuciones nuevas no añaden deuda; el legado queda medido.

### FMT-003 — Fuentes ordinarias por grupos pequeños

- Seleccionar grupos homogéneos de fuentes no protegidas.
- Aplicar únicamente Black, sin cambios semánticos ni de imports.
- Ejecutar pruebas dirigidas del área modificada y revisar el diff.

**Salida:** una PR por grupo; sin Lexer, Parser ni snapshots.

### FMT-004 — Pruebas ordinarias por grupos pequeños

- Reformatear tests sin fixtures/snapshots byte-a-byte.
- Confirmar que no cambia texto esperado, salida ni semántica de las pruebas.
- Mantener una PR por familia de tests.

### FMT-005 — Snapshots y ejemplos

- Identificar cuáles son contratos textuales.
- Para cada grupo, decidir explícitamente si el formato forma parte del
  resultado esperado.
- No aplicar formato automático hasta que exista una prueba de equivalencia o
  una actualización contractual aprobada.

### FMT-006 — Lexer y Parser protegidos

**Requiere autorización explícita y específica.**

- Revisar si Black propone sólo formato.
- Crear una PR exclusiva para cada archivo o para ambos si el diff es
  estrictamente mecánico.
- Ejecutar pruebas focales de Lexer/Parser, pruebas POO relacionadas y revisar
  que el AST y los diagnósticos no cambien.
- No combinar con ninguna funcionalidad POO.

### FMT-007 — Cierre de deuda

- Recalcular el inventario contra el SHA actual.
- Sólo cuando no quede deuda justificada, restaurar una verificación global de
  formato de archivos versionados.
- No elevar requisitos de rama ni modificar permisos hasta tener evidencia de
  estabilidad.

## Fuera de alcance

- Cambios al Libro, al AST o a la gramática.
- Reescrituras de comportamiento durante un cambio de formato.
- Desactivar linters, usar continue-on-error o esconder deuda sin inventario.
