# `standard_library.argumentos`

## Checklist funcional (argumentos)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "argumentos"`.

### Ejemplo Cobra

```cobra
usar "argumentos"
# invoca funciones públicas del módulo
```

# `standard_library.argumentos`

## Argumentos de programa

Lectura y validación básica de argumentos recibidos por un programa Cobra.

## API pública principal

- `obtener()`
- `contiene(nombre)`
- `valor(nombre, defecto=None)`
- `bandera(nombre)`

## Uso rápido

```cobra
usar "argumentos"
```

Nombres públicos en español (fuente prevista: `__all__`).
