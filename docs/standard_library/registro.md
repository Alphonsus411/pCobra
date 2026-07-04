# `standard_library.registro`

## Checklist funcional (registro)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "registro"`.

### Ejemplo Cobra

```cobra
usar "registro"
# invoca funciones públicas del módulo
```

# `standard_library.registro`

## Registro de eventos

Funciones simples para emitir mensajes de diagnóstico con niveles consistentes.

## API pública principal

- `configurar(nivel="info")`
- `depurar(mensaje)`
- `info(mensaje)`
- `advertencia(mensaje)`
- `error(mensaje)`

## Uso rápido

```cobra
usar "registro"
```

Nombres públicos en español (fuente prevista: `__all__`).
