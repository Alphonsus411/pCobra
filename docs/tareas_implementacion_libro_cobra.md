# Tareas estructuradas para implementar el libro de programación Cobra

## Objetivo

Implementar de forma incremental, verificable y mantenible la adopción del nuevo libro `docs/LIBRO_PROGRAMACION_COBRA.md` como referencia principal de aprendizaje del lenguaje.

> Formato de tickets: cada ticket está pensado para **máximo 1–2 días** de ejecución.

---

## Convenciones operativas

- **Estado permitido:** `pendiente`, `en progreso`, `bloqueado`, `hecho`.
- **Prioridad permitida:** `P0 (crítica)`, `P1 (alta)`, `P2 (media)`.
- **Responsable:** rol sugerido (asignar nombre real en cada sprint).
- **Dependencias:** tickets previos que deben cerrarse antes.

---

## A) Tickets de creación/actualización del libro

### Ticket F0-T1 · Inventario documental base
- **Tipo:** `qa-docs`
- **Duración estimada:** 1 día
- **Estado:** `pendiente`
- **Prioridad:** `P0 (crítica)`
- **Responsable:** `Doc Owner`
- **Dependencias:** `ninguna`
- **Objetivo:** construir un inventario único de documentación de aprendizaje y su estado operativo.
- **Entregable exacto:** tabla de inventario (documento, estado, justificación, enlace origen) añadida en este plan.
- **Archivos afectados:**
  - `README.md`
  - `docs/LIBRO_PROGRAMACION_COBRA.md`
  - `docs/MANUAL_COBRA.md`
  - `docs/README.en.md`
  - `docs/tareas_implementacion_libro_cobra.md`
- **Pasos exactos:**
  1. Revisar índices principales (`README.md` y `docs/README.en.md`).
  2. Identificar documentos de onboarding/aprendizaje enlazados.
  3. Clasificar cada documento por estado.
  4. Registrar resultados en este plan (sección de trazabilidad).
- **Criterio de aceptación:**
  - Existe un inventario explícito y trazable con estado por documento.
- **Checklist mínima de validación:**
  - [ ] Enlaces del inventario resuelven correctamente.
  - [ ] Estados usan solo valores permitidos.
  - [ ] Terminología homogénea (`vigente`, `redundante`, `histórico`, `requiere actualización`).
  - [ ] No faltan documentos enlazados desde índices principales.

### Ticket F0-T2 · Criterios de consolidación y obsolescencia
- **Tipo:** `contenido`
- **Duración estimada:** 1 día
- **Estado:** `pendiente`
- **Prioridad:** `P0 (crítica)`
- **Responsable:** `Tech Writer Lead`
- **Dependencias:** `F0-T1`
- **Objetivo:** fijar criterios objetivos para consolidar, archivar o retirar documentación.
- **Entregable exacto:** sección de políticas en `CONTRIBUTING.md` y resumen operativo enlazado desde este plan.
- **Archivos afectados:**
  - `docs/tareas_implementacion_libro_cobra.md`
  - `CONTRIBUTING.md`
- **Pasos exactos:**
  1. Definir qué se considera “redundante”.
  2. Definir señales de obsolescencia (comandos retirados, rutas inválidas, flags legacy).
  3. Documentar política de archivo histórico vs eliminación.
- **Criterio de aceptación:**
  - Criterios publicados y reutilizables por futuros PRs.
- **Checklist mínima de validación:**
  - [ ] Criterios incluyen ejemplos positivos y negativos.
  - [ ] Política distingue claramente `histórico` vs `eliminar`.
  - [ ] Texto consistente con terminología del libro.
  - [ ] Enlace cruzado entre `CONTRIBUTING.md` y este plan.

### Ticket F1-T1 · Enlace principal en README (ES)
- **Tipo:** `contenido`
- **Duración estimada:** 1 día
- **Estado:** `pendiente`
- **Prioridad:** `P0 (crítica)`
- **Responsable:** `Maintainer Docs ES`
- **Dependencias:** `F0-T2`
- **Objetivo:** posicionar el libro como entrada principal en español.
- **Entregable exacto:** bloque superior de documentación en `README.md` con `docs/LIBRO_PROGRAMACION_COBRA.md` en primer lugar.
- **Archivos afectados:**
  - `README.md`
- **Pasos exactos:**
  1. Localizar sección de documentación principal.
  2. Añadir enlace visible a `docs/LIBRO_PROGRAMACION_COBRA.md`.
  3. Reordenar enlaces para priorizar el libro frente a guías antiguas.
- **Criterio de aceptación:**
  - El libro aparece en la primera capa de navegación del `README.md`.
- **Checklist mínima de validación:**
  - [ ] El enlace principal no está roto.
  - [ ] El orden de enlaces deja el libro primero.
  - [ ] Texto introductorio evita ambigüedad sobre documento canónico.
  - [ ] No se eliminan enlaces secundarios útiles sin reemplazo.

### Ticket F1-T2 · Enlace principal en README en inglés
- **Tipo:** `contenido`
- **Duración estimada:** 1 día
- **Estado:** `pendiente`
- **Prioridad:** `P1 (alta)`
- **Responsable:** `Maintainer Docs EN`
- **Dependencias:** `F1-T1`
- **Objetivo:** reflejar en `docs/README.en.md` que el libro canónico está en español.
- **Entregable exacto:** nota corta en inglés + enlace directo al libro con aclaración de idioma/alcance.
- **Archivos afectados:**
  - `docs/README.en.md`
- **Pasos exactos:**
  1. Ubicar bloque de documentación inicial en inglés.
  2. Añadir nota breve indicando el libro canónico y su idioma.
  3. Validar que la redacción minimiza fricción para audiencia internacional.
- **Criterio de aceptación:**
  - `docs/README.en.md` enlaza el libro y aclara idioma/alcance.
- **Checklist mínima de validación:**
  - [ ] Enlace al libro operativo.
  - [ ] Mensaje en inglés claro y no ambiguo.
  - [ ] Terminología alineada con versión ES.
  - [ ] Sin contradicciones con el `README.md` principal.

### Ticket F1-T3 · Mapa de navegación cruzada
- **Tipo:** `qa-docs`
- **Duración estimada:** 2 días
- **Estado:** `pendiente`
- **Prioridad:** `P1 (alta)`
- **Responsable:** `Arquitecto de Contenido`
- **Dependencias:** `F1-T1, F1-T2`
- **Objetivo:** crear una ruta de aprendizaje por escenarios con enlaces cruzados coherentes.
- **Entregable exacto:** tabla de rutas (rápido, CLI, stdlib, arquitectura) y enlaces de ida/vuelta entre libro y manual.
- **Archivos afectados:**
  - `README.md`
  - `docs/LIBRO_PROGRAMACION_COBRA.md`
  - `docs/MANUAL_COBRA.md`
- **Pasos exactos:**
  1. Definir rutas sugeridas (rápido, CLI, stdlib, arquitectura).
  2. Insertar enlaces de ida/vuelta entre libro y manual.
  3. Verificar manualmente que no se generan loops confusos.
- **Criterio de aceptación:**
  - Existe una guía navegable por perfiles de uso y sin enlaces rotos.
- **Checklist mínima de validación:**
  - [ ] Todas las rutas tienen origen y destino explícito.
  - [ ] Sin enlaces rotos en navegación cruzada.
  - [ ] Terminología de perfiles consistente.
  - [ ] No hay loops de navegación sin salida útil.

### Ticket F3-T1 · Verificación de comandos del libro
- **Tipo:** `qa-docs`
- **Duración estimada:** 1 día
- **Estado:** `pendiente`
- **Prioridad:** `P0 (crítica)`
- **Responsable:** `QA CLI`
- **Dependencias:** `F1-T3`
- **Objetivo:** asegurar que los comandos CLI documentados siguen siendo ejecutables.
- **Entregable exacto:** registro de comandos críticos con estado `OK`, `ajuste`, `limitación` y corrección de docs aplicadas.
- **Archivos afectados:**
  - `docs/LIBRO_PROGRAMACION_COBRA.md`
  - `README.md`
- **Pasos exactos:**
  1. Listar comandos críticos de instalación/uso.
  2. Ejecutarlos en entorno limpio o controlado.
  3. Corregir flags/rutas obsoletas en documentación.
- **Criterio de aceptación:**
  - Comandos críticos ejecutan o incluyen nota válida de limitación.
- **Checklist mínima de validación:**
  - [ ] Cada comando crítico tiene resultado documentado.
  - [ ] Snippets de comandos copiados sin alteración accidental.
  - [ ] Notas de limitación incluyen contexto reproducible.
  - [ ] Enlaces a secciones CLI siguen vigentes.

### Ticket F3-T2 · Validación de snippets de sintaxis Cobra
- **Tipo:** `qa-docs`
- **Duración estimada:** 2 días
- **Estado:** `pendiente`
- **Prioridad:** `P1 (alta)`
- **Responsable:** `QA Lenguaje`
- **Dependencias:** `F3-T1`
- **Objetivo:** comprobar coherencia de snippets clave entre parser/intérprete/transpiladores.
- **Entregable exacto:** tabla de snippets críticos con estado de validación y anotaciones por backend.
- **Archivos afectados:**
  - `docs/LIBRO_PROGRAMACION_COBRA.md`
  - `docs/MANUAL_COBRA.md`
- **Pasos exactos:**
  1. Seleccionar snippets críticos (control de flujo, funciones, módulos).
  2. Ejecutar validación sintáctica mínima automatizada/manual.
  3. Documentar variaciones permitidas si existen diferencias por backend.
- **Criterio de aceptación:**
  - Snippets críticos son válidos o están anotados con alcance y excepción.
- **Checklist mínima de validación:**
  - [ ] Cada snippet crítico tiene estado de validación.
  - [ ] Diferencias por backend están explicitadas.
  - [ ] Formato y resaltado de snippets consistente.
  - [ ] Terminología técnica unificada entre libro/manual.

### Ticket F3-T3 · Revisión editorial de terminología
- **Tipo:** `contenido`
- **Duración estimada:** 1 día
- **Estado:** `pendiente`
- **Prioridad:** `P1 (alta)`
- **Responsable:** `Editor Técnico`
- **Dependencias:** `F3-T1, F3-T2`
- **Objetivo:** unificar terminología técnica y tono pedagógico.
- **Entregable exacto:** glosario mínimo aplicado y listado de sustituciones terminológicas realizadas.
- **Archivos afectados:**
  - `docs/LIBRO_PROGRAMACION_COBRA.md`
  - `docs/MANUAL_COBRA.md`
  - `README.md`
  - `docs/README.en.md`
- **Pasos exactos:**
  1. Definir glosario mínimo (target/backend/transpilador/runtime/sandbox).
  2. Normalizar términos en documentos canónicos.
  3. Revisar ortografía y legibilidad.
- **Criterio de aceptación:**
  - Terminología consistente en todos los documentos de entrada.
- **Checklist mínima de validación:**
  - [ ] Glosario incluido o enlazado.
  - [ ] Sustituciones aplicadas de forma uniforme.
  - [ ] Ortografía revisada en títulos y subtítulos.
  - [ ] No hay regresión semántica por cambios editoriales.

### Ticket F4-T1 · Guía de mantenimiento del libro en CONTRIBUTING
- **Tipo:** `qa-docs`
- **Duración estimada:** 1 día
- **Estado:** `pendiente`
- **Prioridad:** `P1 (alta)`
- **Responsable:** `Maintainer de Contribución`
- **Dependencias:** `F3-T3`
- **Objetivo:** institucionalizar el mantenimiento del libro en el flujo de PRs.
- **Entregable exacto:** sección “Cómo actualizar el libro” en `CONTRIBUTING.md` + checklist obligatorio para PR.
- **Archivos afectados:**
  - `CONTRIBUTING.md`
- **Pasos exactos:**
  1. Añadir sección “Cómo actualizar el libro”.
  2. Incluir checklist mínimo para cambios de sintaxis/CLI.
  3. Definir responsables de revisión documental.
- **Criterio de aceptación:**
  - PRs con impacto en lenguaje/CLI tienen checklist documental explícito.
- **Checklist mínima de validación:**
  - [ ] Sección localizada fácilmente desde índice de `CONTRIBUTING.md`.
  - [ ] Checklist breve y accionable.
  - [ ] Responsables/document owners identificados.
  - [ ] Coherencia terminológica con el libro.

---

## B) Tickets de limpieza de redundancia

### Ticket F2-T1 · Retiro/archivo de documentación duplicada
- **Tipo:** `limpieza`
- **Duración estimada:** 2 días
- **Estado:** `pendiente`
- **Prioridad:** `P0 (crítica)`
- **Responsable:** `Maintainer Docs`
- **Dependencias:** `F0-T2, F1-T3`
- **Objetivo:** eliminar o archivar material 100% duplicado de forma segura.
- **Entregable exacto:** PR con movimientos/eliminaciones justificadas + actualización de todos los enlaces entrantes.
- **Archivos afectados:**
  - `README.md`
  - `docs/README.en.md`
  - `docs/MANUAL_COBRA.md`
  - `docs/historico/*` (si aplica)
- **Pasos exactos:**
  1. Identificar archivos o secciones duplicadas sin valor diferencial.
  2. Decidir: archivar en histórico o eliminar.
  3. Actualizar enlaces entrantes para apuntar al recurso vigente.
  4. Ejecutar comprobación de enlaces markdown.
- **Criterio de aceptación:**
  - No quedan referencias activas hacia contenido retirado.
- **Checklist mínima de validación:**
  - [ ] Lista de elementos retirados con justificación.
  - [ ] Enlaces actualizados y verificados.
  - [ ] Banner histórico aplicado cuando corresponda.
  - [ ] No se rompe navegación principal.

### Ticket F2-T2 · Etiquetado explícito de histórico/no operativo
- **Tipo:** `limpieza`
- **Duración estimada:** 1 día
- **Estado:** `pendiente`
- **Prioridad:** `P1 (alta)`
- **Responsable:** `Editor de Archivo Histórico`
- **Dependencias:** `F2-T1`
- **Objetivo:** advertir claramente cuando un documento es solo histórico.
- **Entregable exacto:** banner “No operativo” homogéneo en todos los documentos históricos + enlace al documento canónico vigente.
- **Archivos afectados:**
  - `docs/historico/*.md` (si aplica)
  - `docs/MANUAL_COBRA.md` (si contiene secciones históricas)
- **Pasos exactos:**
  1. Definir plantilla corta de banner “No operativo”.
  2. Aplicar banner en documentos históricos.
  3. Añadir enlace al documento canónico vigente.
- **Criterio de aceptación:**
  - Todo documento histórico muestra banner y ruta alternativa vigente.
- **Checklist mínima de validación:**
  - [ ] Banner uniforme en estilo y mensaje.
  - [ ] Enlace al documento canónico operativo.
  - [ ] Terminología histórica consistente.
  - [ ] Sin ambigüedad entre “histórico” y “vigente”.

---

## Tablero de ejecución

| Ticket | Estado | Bloqueado por | PR |
|---|---|---|---|
| F0-T1 | pendiente | — | — |
| F0-T2 | pendiente | F0-T1 | — |
| F1-T1 | pendiente | F0-T2 | — |
| F1-T2 | pendiente | F1-T1 | — |
| F1-T3 | pendiente | F1-T1, F1-T2 | — |
| F2-T1 | pendiente | F0-T2, F1-T3 | — |
| F2-T2 | pendiente | F2-T1 | — |
| F3-T1 | pendiente | F1-T3 | — |
| F3-T2 | pendiente | F3-T1 | — |
| F3-T3 | pendiente | F3-T1, F3-T2 | — |
| F4-T1 | pendiente | F3-T3 | — |

> Actualizar este tablero en cada PR: cambiar `Estado`, anotar `Bloqueado por` real (si cambia), y añadir enlace/ID en columna `PR`.
