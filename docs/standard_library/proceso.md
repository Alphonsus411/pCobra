# `standard_library.proceso`

## Checklist funcional (proceso)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "proceso"`.

### Ejemplo Cobra

```cobra
usar "proceso"
# invoca funciones públicas del módulo
```

# `standard_library.proceso`

## Procesos externos

Ejecución controlada de comandos y captura de salida, código de salida y errores.

## API pública principal

- `ejecutar(comando, argumentos=None, shell=False)`
- `capturar(comando, argumentos=None)`
- `codigo_salida(resultado)`
- `entorno(nombre, valor=None)`

## Uso rápido

```cobra
usar "proceso"
```

Nombres públicos en español (fuente prevista: `__all__`).

## Nota de seguridad

`shell=False` debe ser el comportamiento por defecto para evitar interpolación accidental de comandos; solo activar shell explícitamente cuando sea indispensable y con entradas confiables.
