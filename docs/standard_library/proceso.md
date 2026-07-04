# `standard_library.proceso`

## Propósito

`proceso` ofrece una capa breve para ejecutar procesos externos, capturar su salida y revisar códigos de finalización sin acoplar el código Cobra directamente a detalles del runtime anfitrión.

## Funciones públicas

- `ejecutar(comando, argumentos=None, shell=False)`: ejecuta un comando y devuelve el resultado del proceso.
- `capturar(comando, argumentos=None)`: ejecuta un comando capturando salida estándar y errores.
- `codigo_salida(resultado)`: extrae el código de salida de un resultado.
- `salida(resultado)`: obtiene la salida estándar capturada.
- `errores(resultado)`: obtiene la salida de error capturada.

## Ejemplo mínimo

```cobra
usar "proceso"

resultado = proceso.capturar("python", ["--version"])
si proceso.codigo_salida(resultado) == 0:
    imprimir(proceso.salida(resultado))
```

## Notas de error y degradación segura

- Mantener `shell=False` salvo que sea imprescindible; activar shell con entradas no confiables puede permitir inyección de comandos.
- Comandos inexistentes, permisos insuficientes o límites del entorno deben tratarse como fallos controlados revisando `codigo_salida` y `errores`.
