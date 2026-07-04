# `standard_library.pruebas`

## Checklist funcional (pruebas)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "pruebas"`.

### Ejemplo Cobra

```cobra
usar "pruebas"
# invoca funciones públicas del módulo
```

# `standard_library.pruebas`

## Pruebas y aserciones

Ayudantes mínimos para expresar verificaciones en ejemplos, scripts y suites de prueba.

## API pública principal

- `afirmar(condicion, mensaje=None)`
- `igual(actual, esperado, mensaje=None)`
- `lanza(funcion, error=None)`
- `ejecutar_pruebas()`

## Uso rápido

```cobra
usar "pruebas"
```

Nombres públicos en español (fuente prevista: `__all__`).
