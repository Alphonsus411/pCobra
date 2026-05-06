# `standard_library.sistema`

## Checklist funcional (sistema)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "sistema"`.

### Ejemplo Cobra

```cobra
usar "sistema"
# invoca funciones públicas del módulo
```

# `standard_library.sistema`

Funciones de sistema seguras:
- `obtener_os`
- `ejecutar` / `ejecutar_async`
- `ejecutar_stream`
- `obtener_env`
- `listar_dir`
- `directorio_actual`
