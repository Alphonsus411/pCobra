# `standard_library.temporal`

## Checklist funcional (temporal)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "temporal"`.

### Ejemplo Cobra

```cobra
usar "temporal"
# invoca funciones públicas del módulo
```

# `standard_library.temporal`

## Fechas, horas e intervalos

Utilidades temporales orientadas a marcas de tiempo, duraciones e intervalos de ejecución.

## API pública principal

- `ahora()`
- `utc()`
- `medir(funcion)`
- `duracion(segundos)`
- `formatear(instante, formato)`

## Uso rápido

```cobra
usar "temporal"
```

Nombres públicos en español (fuente prevista: `__all__`).
