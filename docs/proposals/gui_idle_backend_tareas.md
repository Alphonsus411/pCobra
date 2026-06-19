# Tareas estructuradas — GUI IDLE, sugerencias y backends oficiales

Fecha: 2026-06-19

## Decisiones verificadas

- El backend público del proyecto queda limitado a los tres pilares canónicos: `python`, `javascript` y `rust`.
- No se reintroducen targets legacy como `go`, `cpp`, `java`, `wasm` o `asm` en la GUI ni en la política pública de backend.
- La GUI debe consumir la lista canónica desde `PUBLIC_BACKENDS`/`OFFICIAL_TARGETS`, nunca una lista local duplicada.
- No se cambia el contrato Lexer/Parser para estas tareas. Toda sugerencia automática debe validar primero el código de entrada y después validar los fragmentos sugeridos con `Lexer(codigo).tokenizar()` y `Parser(tokens).parsear()`.
- La librería presente y documentada para sugerencias es `agix`. La mención `agi-core` se considera incoherencia nominal si aparece en requisitos externos: no existe como dependencia declarada del proyecto, por lo que no debe inventarse una integración paralela sin ADR aprobada.

## Tarea GUI-01 — Guardado de archivos en el IDLE

**Objetivo:** mantener una experiencia tipo IDLE para crear, abrir, guardar, guardar como y recargar archivos Cobra.

**Alcance:**

- Usar `GuiFileState` para ruta activa, contenido cargado y marca de cambios sin guardar.
- Guardar solo texto normalizado del editor.
- Aceptar extensiones Cobra documentadas: `.co` y `.cobra`.
- Mostrar errores de ruta, permisos y Unicode en el panel de salida.

**Criterios de aceptación:**

- `Guardar` actualiza el archivo activo si existe.
- `Guardar como` usa la ruta indicada por el usuario y actualiza el estado activo.
- La etiqueta del archivo muestra `*` cuando hay cambios sin guardar.
- Las pruebas GUI cubren helpers de lectura/escritura sin requerir Flet instalado.

## Tarea GUI-02 — Árbol de directorios Cobra

**Objetivo:** mostrar un explorador lateral seguro para proyectos Cobra.

**Alcance:**

- Renderizar directorios y archivos `.co`/`.cobra` por defecto.
- Permitir cambiar la raíz del árbol desde la GUI.
- Cargar archivos al seleccionarlos desde el árbol.
- Mantener una opción interna para mostrar todos los archivos solo si se documenta una configuración futura.

**Criterios de aceptación:**

- El árbol no lista targets ni backends; solo rutas de archivos.
- Los directorios se ordenan antes que archivos y de forma estable.
- Seleccionar un archivo no Cobra muestra un error y no altera el contenido activo.

## Tarea GUI-03 — Herramienta de corrección tipográfica/estilística del Libro

**Objetivo:** ofrecer sugerencias de código trazables al Libro de Programación sin inventar sintaxis.

**Alcance:**

- Usar la fachada `pcobra.ia.analizador_sugerencias`.
- Mantener `agix` como nombre canónico del motor opcional.
- Rechazar `agi-core` como nombre de dependencia si no existe en el proyecto y exigir una ADR aprobada antes de cualquier integración paralela.
- Agrupar sugerencias por categorías: léxico/sintaxis, estilo, nombres, forma canónica y observabilidad.
- Validar entrada y fragmentos sugeridos con Lexer/Parser.

**Criterios de aceptación:**

- Si el código no parsea, la GUI muestra el error y no emite correcciones aplicables.
- Si falta `agix`, el botón de sugerencias queda deshabilitado o informa una acción de instalación clara.
- Cada regla interna mantiene `rule_id`, sección del Libro, categoría, severidad y marca de aplicación automática.

## Tarea BACKEND-01 — Tres pilares oficiales

**Objetivo:** asegurar que el backend público esté conformado solo por Python, JavaScript y Rust.

**Alcance:**

- Mantener `PUBLIC_BACKENDS = ("python", "javascript", "rust")` como fuente normativa.
- Mantener `ALLOWED_TARGETS`, `OFFICIAL_TARGETS`, GUI y CLI alineados con esa tupla.
- No incluir alias cortos retirados en superficies públicas, aunque puedan existir shims internos documentados.

**Criterios de aceptación:**

- Las opciones de la GUI coinciden exactamente con `PUBLIC_BACKENDS`.
- Los tests de contrato fallan si aparece cualquier backend legacy en la lista pública.
- Las rutas legacy, si existen, quedan documentadas como compatibilidad interna/de migración, no como backend público.

## Tarea QA-01 — Coherencia Lexer/Parser

**Objetivo:** evitar divergencias entre documentación, sugerencias y gramática implementada.

**Alcance:**

- No modificar tokens ni parser para introducir atajos no documentados.
- Añadir nuevas reglas de sugerencia solo si sus fragmentos válidos parsean.
- Documentar cualquier incoherencia como tarea de mejora antes de cambiar sintaxis.

**Criterios de aceptación:**

- `tests/test_lexer_parser_contract.py` y pruebas de sugerencias pasan.
- Las propuestas inválidas del Libro se prueban explícitamente como inválidas cuando corresponda.

## Incoherencias detectadas y tareas de mejora

1. **Nombre `agi-core` vs `agix`:** el proyecto declara y documenta `agix`; no se encontró una dependencia canónica `agi-core`.  
   **Mejora propuesta:** normalizar nuevas historias de usuario y documentación a `agix`, o abrir y aprobar una ADR separada si se decide migrar realmente a otra librería o añadir una integración paralela.
2. **Shims legacy internos:** existen menciones históricas y rutas de compatibilidad.  
   **Mejora propuesta:** mantenerlas fuera de la UX pública y revisar su eliminación según el calendario de compatibilidad.
3. **Validadores legacy:** cualquier validador fuera de Python/JavaScript/Rust debe permanecer en rutas internas de regresión histórica.  
   **Mejora propuesta:** auditar periódicamente documentación pública con un lint que bloquee promoción de targets legacy.
