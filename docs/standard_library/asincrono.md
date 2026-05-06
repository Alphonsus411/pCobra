# `standard_library.asincrono`

## Checklist funcional (asincrono)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "asincrono"`.

### Ejemplo Cobra

```cobra
usar "asincrono"
# invoca funciones públicas del módulo
```

# `standard_library.asincrono`

Documentación sincronizada automáticamente desde `src/pcobra/standard_library/asincrono.py`.

<!-- BEGIN: AUTO-STDLIB-FUNCTIONS -->
## API pública sincronizada (`standard_library.asincrono`)

| Función |
|---|
| `ejecutar_en_hilo` |
| `grupo_tareas` |
| `limitar_tiempo` |
| `proteger_tarea` |
| `reintentar_async` |
<!-- END: AUTO-STDLIB-FUNCTIONS -->

- `dormir_async(segundos)` expone pausa cooperativa equivalente a `await sleep`.
