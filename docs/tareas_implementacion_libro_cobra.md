# Tareas estructuradas para implementar el libro de programación Cobra

## Objetivo

Implementar de forma incremental, verificable y mantenible la adopción del nuevo libro `docs/LIBRO_PROGRAMACION_COBRA.md` como referencia principal de aprendizaje del lenguaje.

## Fase 0 — Preparación y diagnóstico

### T0.1 Inventario documental
- [ ] Listar documentos de aprendizaje actuales (`README`, `docs/README.en.md`, manuales, guías y ejemplos).
- [ ] Clasificar cada documento en: **vigente**, **redundante**, **histórico** o **requiere actualización**.
- [ ] Marcar enlaces rotos o circulares.

### T0.2 Criterios de consolidación
- [ ] Definir criterio para considerar documentación redundante.
- [ ] Definir criterio de obsolescencia (comandos viejos, targets retirados, rutas inexistentes, etc.).
- [ ] Acordar política de archivo histórico vs. eliminación.

## Fase 1 — Integración del libro como referencia principal

### T1.1 Enlaces principales
- [ ] Añadir enlace al libro en `README.md` dentro de la sección de documentación.
- [ ] Añadir enlace al libro en `docs/README.en.md` (nota en inglés explicando que el contenido está en español).
- [ ] Priorizar el libro por encima de guías introductorias antiguas.

### T1.2 Navegación interna
- [ ] Crear tabla de rutas recomendadas (aprendizaje rápido, backend, CLI, stdlib, arquitectura).
- [ ] Agregar referencias cruzadas entre libro, manual y especificaciones.

## Fase 2 — Limpieza de redundancia/desactualización

### T2.1 Eliminación segura
- [ ] Eliminar documentos que estén 100% duplicados o sin referencias activas.
- [ ] Verificar que no queden enlaces colgantes tras eliminar archivos.

### T2.2 Normalización de estado
- [ ] Etiquetar documentos históricos con banner claro de “No operativo”.
- [ ] Centralizar la política vigente en un único documento canónico por tema.

## Fase 3 — Validación técnica y editorial

### T3.1 Validación de comandos
- [ ] Probar comandos de ejemplo de CLI incluidos en el libro.
- [ ] Corregir snippets con flags/rutas desactualizadas.

### T3.2 Validación de sintaxis Cobra
- [ ] Ejecutar validación de sintaxis sobre ejemplos críticos.
- [ ] Documentar variaciones permitidas si difieren entre parser/intérprete/transpiladores.

### T3.3 Calidad editorial
- [ ] Revisar consistencia de términos (target, backend, transpilar, runtime, sandbox).
- [ ] Revisar ortografía, estilo y legibilidad pedagógica.

## Fase 4 — Adopción en flujo de contribución

### T4.1 CONTRIBUTING
- [ ] Añadir sección “Cómo actualizar el libro” en `CONTRIBUTING.md`.
- [ ] Definir checklist mínimo para PRs que cambien sintaxis o CLI.

### T4.2 CI documental (opcional recomendado)
- [ ] Crear una verificación básica de enlaces markdown.
- [ ] Verificar que archivos eliminados no sigan referenciados.

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
