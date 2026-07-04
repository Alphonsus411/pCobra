# `standard_library.serializacion`

## Checklist funcional (serializacion)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "serializacion"`.

### Ejemplo Cobra

```cobra
usar "serializacion"
# invoca funciones públicas del módulo
```

# `standard_library.serializacion`

## Serialización de datos

Conversión entre estructuras Cobra y representaciones textuales interoperables como JSON.

## API pública principal

- `a_json(valor)`
- `desde_json(texto)`
- `guardar_json(ruta, valor)`
- `cargar_json(ruta)`

## Uso rápido

```cobra
usar "serializacion"
```

Nombres públicos en español (fuente prevista: `__all__`).
