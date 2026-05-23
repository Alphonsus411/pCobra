# Checklist de revisión previa a merge (foco seguridad `usar` + BUG-001)

## Alcance
- Revisar únicamente rutas de `cobra run` y carga de fuente (`usar`/resolución de módulos), evitando tocar pipeline ajeno al flujo estabilizado de BUG-001.

## Controles obligatorios
- [ ] **No se habilitan imports externos directos**: confirmar que `validar_nombre_modulo_usar` sigue rechazando alias externos (p.ej. `numpy`, `node-fetch`, `serde`, SDKs).
- [ ] **No se exponen símbolos no públicos**: verificar que en la superficie `usar` no aparecen `os`, `pathlib`, SDKs backend ni símbolos privados (`_`/`__`).
- [ ] **Se mantiene rechazo de módulos fuera del catálogo público**: validar error de permiso para módulos no mapeados en catálogo oficial.
- [ ] **Se mantiene validación global de primitivas peligrosas**: confirmar que llamadas peligrosas sin habilitación explícita por `usar` siguen bloqueadas por el validador semántico.
- [ ] **No hay traceback en errores de usuario**: validar que el mensaje final sea controlado (tipo `PermissionError`/mensaje de dominio) y no fuga stacktrace interno.

## Evidencia mínima recomendada
- [ ] Ejecutar pruebas negativas específicas:
  - módulo no público vía `usar`;
  - primitiva peligrosa sin `usar` autorizado.
- [ ] Ejecutar pruebas de regresión acotadas a `cobra run`/carga de fuente para garantizar ausencia de efectos colaterales en BUG-001.
