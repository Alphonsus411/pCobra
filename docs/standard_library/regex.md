# `standard_library.regex`

## Checklist funcional (regex)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "regex"`.

### Ejemplo Cobra

```cobra
usar "regex"
# invoca funciones públicas del módulo
```

# `standard_library.regex`

## Expresiones regulares

Búsqueda, validación y reemplazo de texto mediante patrones regulares.

## API pública principal

- `coincide(patron, texto)`
- `buscar(patron, texto)`
- `encontrar_todos(patron, texto)`
- `reemplazar(patron, sustituto, texto)`

## Uso rápido

```cobra
usar "regex"
```

Nombres públicos en español (fuente prevista: `__all__`).
