# `standard_library.registro`

## Propósito

`registro` centraliza la emisión de mensajes de diagnóstico con niveles consistentes para scripts, pruebas y aplicaciones pequeñas.

## Funciones públicas

- `configurar(nivel="info", archivo=None)`: configura nivel y destino del registro.
- `debug(mensaje)`: emite un mensaje de depuración.
- `info(mensaje)`: emite un mensaje informativo.
- `aviso(mensaje)`: emite una advertencia.
- `error(mensaje)`: emite un mensaje de error.
- `obtener_registrador(nombre=None)`: devuelve el registrador configurado.

## Ejemplo mínimo

```cobra
usar "registro"

registro.configurar("info")
registro.info("aplicación iniciada")
```

## Notas de error y degradación segura

- Un nivel no reconocido debe rechazarse con un error claro.
- Si se configura salida a archivo, pueden aparecer errores de permisos o rutas inexistentes; usar salida estándar como alternativa segura cuando no sea posible escribir en disco.
