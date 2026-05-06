# `standard_library.red`

## Checklist funcional (red)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "red"`.

### Ejemplo Cobra

```cobra
usar "red"
# invoca funciones públicas del módulo
```

# `standard_library.red`

Utilidades seguras de red HTTPS con lista blanca de hosts (`COBRA_HOST_WHITELIST`).
Incluye `obtener_url`, `enviar_post`, variantes async, `descargar_archivo` y `obtener_json`.
