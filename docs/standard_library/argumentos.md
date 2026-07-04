# `standard_library.argumentos`

## Propósito

`argumentos` facilita leer y consultar argumentos de línea de comandos con convenciones simples para flags y pares clave-valor.

## Funciones públicas

- `obtener_argumentos()`: devuelve la lista de argumentos recibidos por el programa.
- `contiene_flag(argumentos, nombre)`: indica si una bandera está presente.
- `obtener_opcion(argumentos, nombre, defecto=None)`: devuelve el valor de una opción o un valor por defecto.
- `parsear_pares(argumentos)`: convierte argumentos tipo clave-valor en una estructura consultable.

## Ejemplo mínimo

```cobra
usar "argumentos"

args = argumentos.obtener_argumentos()
modo = argumentos.obtener_opcion(args, "--modo", "normal")
si argumentos.contiene_flag(args, "--verbose"):
    imprimir(modo)
```

## Notas de error y degradación segura

- Validar tipos antes de parsear; una cadena plana no debe tratarse como lista de argumentos.
- Usar valores por defecto para opciones ausentes y validar los valores antes de emplearlos en rutas, procesos o configuración.
