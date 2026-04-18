# Tareas estructuradas para implementar el libro de programación Cobra

## Objetivo

Implementar de forma incremental, verificable y mantenible la adopción del nuevo libro `docs/LIBRO_PROGRAMACION_COBRA.md` como referencia principal de aprendizaje del lenguaje.

> Formato de tickets: cada ticket está pensado para **máximo 1–2 días** de ejecución.

---

## Fase 0 — Preparación y diagnóstico

### Ticket F0-T1 · Inventario documental base
- **Tipo:** `qa-docs`
- **Duración estimada:** 1 día
- **Objetivo:** construir un inventario único de documentación de aprendizaje y su estado operativo.
- **Archivos afectados:**
  - `README.md`
  - `docs/LIBRO_PROGRAMACION_COBRA.md`
  - `docs/MANUAL_COBRA.md`
  - `docs/README.en.md`
  - `docs/tareas_implementacion_libro_cobra.md`
- **Precondiciones:**
  - Existe una versión vigente de los archivos de documentación principales.
  - El equipo acuerda categorías de estado (`vigente`, `redundante`, `histórico`, `requiere actualización`).
- **Pasos exactos:**
  1. Revisar índices principales (`README.md` y `docs/README.en.md`).
  2. Identificar documentos de onboarding/aprendizaje enlazados.
  3. Clasificar cada documento por estado.
  4. Registrar resultados en este plan (sección de trazabilidad).
- **Criterio de aceptación:**
  - Existe un inventario explícito y trazable con estado por documento.
- **Evidencia esperada:**
  - Diff con tabla/listado de inventario actualizado.
  - Commits con mensaje que mencione “inventario documental”.
- **Riesgos:**
  - Omisión de documentos no enlazados desde índices.
  - Clasificación subjetiva sin criterio homogéneo.

### Ticket F0-T2 · Criterios de consolidación y obsolescencia
- **Tipo:** `contenido`
- **Duración estimada:** 1 día
- **Objetivo:** fijar criterios objetivos para consolidar, archivar o retirar documentación.
- **Archivos afectados:**
  - `docs/tareas_implementacion_libro_cobra.md`
  - `CONTRIBUTING.md`
- **Precondiciones:**
  - Inventario de F0-T1 completado.
- **Pasos exactos:**
  1. Definir qué se considera “redundante”.
  2. Definir señales de obsolescencia (comandos retirados, rutas inválidas, flags legacy).
  3. Documentar política de archivo histórico vs eliminación.
- **Criterio de aceptación:**
  - Criterios publicados y reutilizables por futuros PRs.
- **Evidencia esperada:**
  - Sección nueva/actualizada en documentación con reglas explícitas.
- **Riesgos:**
  - Ambigüedad entre “histórico” y “eliminable”.

---

## Fase 1 — Integración del libro como referencia principal

### Ticket F1-T1 · Enlace principal en README (ES)
- **Tipo:** `contenido`
- **Duración estimada:** 1 día
- **Objetivo:** posicionar el libro como entrada principal en español.
- **Archivos afectados:**
  - `README.md`
- **Precondiciones:**
  - Libro existente y con estructura navegable mínima.
- **Pasos exactos:**
  1. Localizar sección de documentación principal.
  2. Añadir enlace visible a `docs/LIBRO_PROGRAMACION_COBRA.md`.
  3. Reordenar enlaces para priorizar el libro frente a guías antiguas.
- **Criterio de aceptación:**
  - El libro aparece en la primera capa de navegación del `README.md`.
- **Evidencia esperada:**
  - Diff del `README.md` con enlace y orden actualizado.
- **Riesgos:**
  - Confusión si no se preservan enlaces secundarios útiles.

### Ticket F1-T2 · Enlace principal en README en inglés
- **Tipo:** `contenido`
- **Duración estimada:** 1 día
- **Objetivo:** reflejar en `docs/README.en.md` que el libro canónico está en español.
- **Archivos afectados:**
  - `docs/README.en.md`
- **Precondiciones:**
  - Ticket F1-T1 completado.
- **Pasos exactos:**
  1. Ubicar bloque de documentación inicial en inglés.
  2. Añadir nota breve indicando el libro canónico y su idioma.
  3. Validar que la redacción minimiza fricción para audiencia internacional.
- **Criterio de aceptación:**
  - `docs/README.en.md` enlaza el libro y aclara idioma/alcance.
- **Evidencia esperada:**
  - Diff en `docs/README.en.md` con nota + enlace.
- **Riesgos:**
  - Traducción ambigua sobre obligatoriedad/cobertura.

### Ticket F1-T3 · Mapa de navegación cruzada
- **Tipo:** `qa-docs`
- **Duración estimada:** 2 días
- **Objetivo:** crear una ruta de aprendizaje por escenarios con enlaces cruzados coherentes.
- **Archivos afectados:**
  - `README.md`
  - `docs/LIBRO_PROGRAMACION_COBRA.md`
  - `docs/MANUAL_COBRA.md`
- **Precondiciones:**
  - Tickets F1-T1 y F1-T2 completados.
- **Pasos exactos:**
  1. Definir rutas sugeridas (rápido, CLI, stdlib, arquitectura).
  2. Insertar enlaces de ida/vuelta entre libro y manual.
  3. Verificar manualmente que no se generan loops confusos.
- **Criterio de aceptación:**
  - Existe una guía navegable por perfiles de uso y sin enlaces rotos.
- **Evidencia esperada:**
  - Tabla de rutas publicada y enlaces cruzados en archivos canónicos.
- **Riesgos:**
  - Sobreenlazado que dificulte lectura lineal.

---

## Fase 2 — Limpieza de redundancia/desactualización

### Ticket F2-T1 · Retiro/archivo de documentación duplicada
- **Tipo:** `limpieza`
- **Duración estimada:** 2 días
- **Objetivo:** eliminar o archivar material 100% duplicado de forma segura.
- **Archivos afectados:**
  - `README.md`
  - `docs/README.en.md`
  - `docs/MANUAL_COBRA.md`
  - `docs/historico/*` (si aplica)
- **Precondiciones:**
  - Criterios de F0-T2 aprobados.
  - Mapa de navegación F1-T3 estable.
- **Pasos exactos:**
  1. Identificar archivos o secciones duplicadas sin valor diferencial.
  2. Decidir: archivar en histórico o eliminar.
  3. Actualizar enlaces entrantes para apuntar al recurso vigente.
  4. Ejecutar comprobación de enlaces markdown.
- **Criterio de aceptación:**
  - No quedan referencias activas hacia contenido retirado.
- **Evidencia esperada:**
  - Diff con movimientos/eliminaciones y actualización de enlaces.
  - Salida de verificación de links sin errores críticos.
- **Riesgos:**
  - Borrado accidental de contenido aún referenciado por terceros.

### Ticket F2-T2 · Etiquetado explícito de histórico/no operativo
- **Tipo:** `limpieza`
- **Duración estimada:** 1 día
- **Objetivo:** advertir claramente cuando un documento es solo histórico.
- **Archivos afectados:**
  - `docs/historico/*.md` (si aplica)
  - `docs/MANUAL_COBRA.md` (si contiene secciones históricas)
- **Precondiciones:**
  - Ticket F2-T1 completado.
- **Pasos exactos:**
  1. Definir plantilla corta de banner “No operativo”.
  2. Aplicar banner en documentos históricos.
  3. Añadir enlace al documento canónico vigente.
- **Criterio de aceptación:**
  - Todo documento histórico muestra banner y ruta alternativa vigente.
- **Evidencia esperada:**
  - Diffs con banners consistentes.
- **Riesgos:**
  - Banner no uniforme entre documentos.

---

## Fase 3 — Validación técnica y editorial

### Ticket F3-T1 · Verificación de comandos del libro
- **Tipo:** `qa-docs`
- **Duración estimada:** 1 día
- **Objetivo:** asegurar que los comandos CLI documentados siguen siendo ejecutables.
- **Archivos afectados:**
  - `docs/LIBRO_PROGRAMACION_COBRA.md`
  - `README.md`
- **Precondiciones:**
  - Libro enlazado desde índices principales.
- **Pasos exactos:**
  1. Listar comandos críticos de instalación/uso.
  2. Ejecutarlos en entorno limpio o controlado.
  3. Corregir flags/rutas obsoletas en documentación.
- **Criterio de aceptación:**
  - Comandos críticos ejecutan o incluyen nota válida de limitación.
- **Evidencia esperada:**
  - Registro de comandos y estado (OK/ajuste requerido).
- **Riesgos:**
  - Dependencia de entorno local/CI no reproducible.

### Ticket F3-T2 · Validación de snippets de sintaxis Cobra
- **Tipo:** `qa-docs`
- **Duración estimada:** 2 días
- **Objetivo:** comprobar coherencia de snippets clave entre parser/intérprete/transpiladores.
- **Archivos afectados:**
  - `docs/LIBRO_PROGRAMACION_COBRA.md`
  - `docs/MANUAL_COBRA.md`
- **Precondiciones:**
  - Ticket F3-T1 completado.
- **Pasos exactos:**
  1. Seleccionar snippets críticos (control de flujo, funciones, módulos).
  2. Ejecutar validación sintáctica mínima automatizada/manual.
  3. Documentar variaciones permitidas si existen diferencias por backend.
- **Criterio de aceptación:**
  - Snippets críticos son válidos o están anotados con alcance y excepción.
- **Evidencia esperada:**
  - Tabla de snippets validados y correcciones aplicadas.
- **Riesgos:**
  - Falsos positivos por diferencias esperadas entre backends.

### Ticket F3-T3 · Revisión editorial de terminología
- **Tipo:** `contenido`
- **Duración estimada:** 1 día
- **Objetivo:** unificar terminología técnica y tono pedagógico.
- **Archivos afectados:**
  - `docs/LIBRO_PROGRAMACION_COBRA.md`
  - `docs/MANUAL_COBRA.md`
  - `README.md`
  - `docs/README.en.md`
- **Precondiciones:**
  - Tickets F3-T1 y F3-T2 completados.
- **Pasos exactos:**
  1. Definir glosario mínimo (target/backend/transpilador/runtime/sandbox).
  2. Normalizar términos en documentos canónicos.
  3. Revisar ortografía y legibilidad.
- **Criterio de aceptación:**
  - Terminología consistente en todos los documentos de entrada.
- **Evidencia esperada:**
  - Diff con sustituciones terminológicas y mejoras editoriales.
- **Riesgos:**
  - Cambios semánticos involuntarios por edición de estilo.

---

## Fase 4 — Adopción en flujo de contribución

### Ticket F4-T1 · Guía de mantenimiento del libro en CONTRIBUTING
- **Tipo:** `qa-docs`
- **Duración estimada:** 1 día
- **Objetivo:** institucionalizar el mantenimiento del libro en el flujo de PRs.
- **Archivos afectados:**
  - `CONTRIBUTING.md`
- **Precondiciones:**
  - Fases 1–3 completadas o en estado estable.
- **Pasos exactos:**
  1. Añadir sección “Cómo actualizar el libro”.
  2. Incluir checklist mínimo para cambios de sintaxis/CLI.
  3. Definir responsables de revisión documental.
- **Criterio de aceptación:**
  - PRs con impacto en lenguaje/CLI tienen checklist documental explícito.
- **Evidencia esperada:**
  - Diff en `CONTRIBUTING.md` con sección y checklist.
- **Riesgos:**
  - Checklist demasiado largo y baja adopción.

### Ticket F4-T2 · Automatización de verificación de enlaces docs
- **Tipo:** `automatizacion`
- **Duración estimada:** 2 días
- **Objetivo:** reducir regresiones por enlaces rotos con check automatizado.
- **Archivos afectados:**
  - `scripts/` (script de verificación o integración existente)
  - Pipeline CI relevante
  - `CONTRIBUTING.md`
- **Precondiciones:**
  - Estructura documental estabilizada tras F2.
- **Pasos exactos:**
  1. Definir comando reproducible para validar enlaces markdown.
  2. Integrarlo en CI (job no bloqueante al inicio si es necesario).
  3. Documentar uso local para contribuyentes.
- **Criterio de aceptación:**
  - Existe verificación automática ejecutable en local/CI.
- **Evidencia esperada:**
  - Salida de CI o ejecución local del check.
  - Documentación de uso en `CONTRIBUTING.md`.
- **Riesgos:**
  - Falsos positivos por enlaces externos intermitentes.

---

## Matriz de trazabilidad tarea → archivo

| Ticket | README.md | docs/LIBRO_PROGRAMACION_COBRA.md | docs/MANUAL_COBRA.md | docs/README.en.md | CONTRIBUTING.md | scripts/CI |
|---|---|---|---|---|---|---|
| F0-T1 | X | X | X | X |  |  |
| F0-T2 |  |  |  |  | X |  |
| F1-T1 | X |  |  |  |  |  |
| F1-T2 |  |  |  | X |  |  |
| F1-T3 | X | X | X |  |  |  |
| F2-T1 | X |  | X | X |  |  |
| F2-T2 |  |  | X |  |  |  |
| F3-T1 | X | X |  |  |  |  |
| F3-T2 |  | X | X |  |  |  |
| F3-T3 | X | X | X | X |  |  |
| F4-T1 |  |  |  |  | X |  |
| F4-T2 |  |  |  |  | X | X |

> Nota: la matriz refleja impacto esperado; cada PR puede tocar menos archivos según alcance real del ticket.

---

## Orden de ejecución recomendado (incremental y sin romper enlaces)

1. **F0-T1 → F0-T2**: primero inventario y criterios para evitar limpieza prematura.
2. **F1-T1 → F1-T2 → F1-T3**: publicar entrada canónica antes de reestructurar navegación cruzada.
3. **F2-T1 → F2-T2**: retirar/archivar primero, etiquetar histórico después para no dejar referencias huérfanas.
4. **F3-T1 → F3-T2 → F3-T3**: validar ejecución y sintaxis antes de pulir estilo/terminología.
5. **F4-T1 → F4-T2**: cerrar con gobernanza (`CONTRIBUTING`) y automatización en CI.

### Reglas anti-rotura de enlaces
- No eliminar archivos sin redirigir sus enlaces entrantes en el mismo PR.
- Si un documento pasa a histórico, debe incluir enlace inmediato al canónico.
- Cualquier cambio estructural de rutas debe acompañarse de verificación de enlaces.

---

## Entregables

1. `docs/LIBRO_PROGRAMACION_COBRA.md` como guía principal.
2. Índices actualizados (`README.md`, `docs/README.en.md`).
3. Reducción de redundancia documental con trazabilidad.
4. Plan de mantenimiento de documentación a futuro.

## Definición de “hecho” (DoD)

- [ ] Libro creado y enlazado desde índices principales.
- [ ] Al menos un documento redundante/desactualizado eliminado o archivado correctamente.
- [ ] No existen enlaces rotos hacia documentación eliminada.
- [ ] Equipo puede seguir un camino de aprendizaje de nivel básico a avanzado solo con enlaces principales.
