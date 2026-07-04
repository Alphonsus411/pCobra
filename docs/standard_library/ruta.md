# `standard_library.ruta`

## Checklist funcional (ruta)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "ruta"`.

### Ejemplo Cobra

```cobra
usar "ruta"
# invoca funciones públicas del módulo
```

# `standard_library.ruta`

## Rutas y nombres de archivo

Utilidades para componer, normalizar e inspeccionar rutas sin acoplar el código Cobra al sistema operativo anfitrión.

## API pública principal

- `unir(partes...)`
- `normalizar(ruta)`
- `absoluta(ruta)`
- `nombre(ruta)`
- `extension(ruta)`
- `padre(ruta)`
- `es_absoluta(ruta)`

## Uso rápido

```cobra
usar "ruta"
```

Nombres públicos en español (fuente prevista: `__all__`).
