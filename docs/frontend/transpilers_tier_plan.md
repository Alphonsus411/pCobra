# Plan de implementación por tiers de transpilación (pCobra)

## Objetivo
Reducir y estabilizar los targets de transpilación de pCobra en dos niveles:

- **Tier 1:** Python, Rust, JavaScript, WASM.
- **Tier 2:** Go, C++, Java, Ensamblador.

## Tareas estructuradas

### Tarea 1 — Congelar el contrato de targets soportados
- [x] Actualizar el registro único de transpiladores (`TRANSPILERS`) para exponer solo los 8 targets aprobados.
- [x] Sincronizar `LANG_CHOICES` con ese registro.
- [ ] Publicar una política explícita de compatibilidad por tier en documentación técnica y de usuario.

### Tarea 2 — Retirar código de backends fuera de alcance
- [x] Eliminar implementaciones `to_*` que no pertenecen a Tier 1/2.
- [x] Eliminar nodos específicos (`*_nodes`) de backends retirados.
- [ ] Ejecutar auditoría final de imports para garantizar ausencia total de referencias obsoletas en código de producción.

### Tarea 3 — Asegurar compatibilidad con Holobit SDK y librerías base
- [x] Mantener intactos los transpiladores soportados que ya emiten construcciones `holobit`.
- [x] Conservar flujo de validación de dependencias (`validar_dependencias`) en `compilar`.
- [ ] Añadir pruebas de regresión para `graficar`, `proyectar`, `transformar`, `escalar` y `mover` en Tier 1 y Tier 2.

### Tarea 4 — Limpiar y alinear pruebas
- [x] Retirar tests unitarios/integración de backends eliminados.
- [ ] Reescribir matrices de pruebas para clasificar por Tier 1/Tier 2.
- [ ] Añadir pipeline de smoke tests mínimo para los 8 targets soportados.

### Tarea 5 — Actualizar documentación pública
- [x] Actualizar secciones principales del README (ES/EN) con la nueva lista de destinos.
- [x] Ajustar ejemplos de importación de transpiladores a los 8 soportados.
- [ ] Revisar documentación secundaria y ejemplos históricos para eliminar menciones residuales.

## Criterios de aceptación
1. El comando `cobra compilar --tipo` solo acepta los 8 targets de Tier 1/2.
2. No existen módulos `to_*` de lenguajes fuera de alcance en el árbol de código principal.
3. Los tests de compilación/transpilación de targets soportados pasan en CI.
4. README y documentación principal no anuncian destinos fuera de Tier 1/2.
