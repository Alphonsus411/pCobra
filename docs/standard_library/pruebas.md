# `standard_library.pruebas`

## Propósito

`pruebas` proporciona aserciones pequeñas para ejemplos, scripts y suites ligeras sin depender de un framework externo.

## Funciones públicas

- `igual(actual, esperado, mensaje=None)`: comprueba igualdad.
- `verdadero(valor, mensaje=None)`: comprueba que un valor sea verdadero.
- `falso(valor, mensaje=None)`: comprueba que un valor sea falso.
- `contiene(contenedor, elemento, mensaje=None)`: comprueba pertenencia.
- `lanza_error(funcion, error=None)`: verifica que una función lance un error esperado.

## Ejemplo mínimo

```cobra
usar "pruebas"

pruebas.igual(2 + 2, 4)
pruebas.verdadero("cobra" contiene "co")
```

## Notas de error y degradación segura

- Las aserciones deben fallar con mensajes breves y accionables para facilitar depuración.
- `lanza_error` es útil para documentar fallos esperados y evitar que errores controlados parezcan regresiones.
