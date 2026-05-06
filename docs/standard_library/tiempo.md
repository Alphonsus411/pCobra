# `standard_library.tiempo`

## Checklist funcional (tiempo)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "tiempo"`.

### Ejemplo Cobra

```cobra
usar "tiempo"
# invoca funciones públicas del módulo
```

# `standard_library.tiempo`

API temporal en español:
- `ahora()`
- `formatear(fecha, formato)`
- `dormir(segundos)`
- `epoch(fecha=None)`
- `desde_epoch(segundos)`
