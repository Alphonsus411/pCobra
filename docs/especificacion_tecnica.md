# Especificación Técnica de Cobra

Este documento resume la sintaxis y la semántica básica del lenguaje Cobra.

## Estructura general

Un programa Cobra está formado por sentencias separadas por saltos de línea e indentadas con espacios. El punto de entrada se define en la función `principal`.

## Comentarios

Se indican con el carácter `#` y se extienden hasta el final de la línea.

```cobra
# Esto es un comentario
```

## Variables y tipos

Las variables se asignan con `=`. Cobra soporta números, cadenas, listas y diccionarios.

```cobra
x = 10
nombre = "Ana"
lista = [1, 2, 3]
mapa = {"a": 1, "b": 2}
```

## Funciones

Las funciones se definen con `func` y pueden devolver valores con `regresar`.

```cobra
func sumar(a, b):
    regresar a + b
fin
```

## Clases y objetos

Las clases utilizan la palabra `clase`. Los métodos se declaran con `metodo`.

```cobra
clase Persona:
    metodo __init__(self, nombre):
        atributo self nombre = nombre
    metodo saludar(self):
        imprimir "Hola", atributo self nombre
    fin
fin
```

## Control de flujo

Cobra cuenta con condicionales `si`, `sino` y bucles `para` y `mientras`.

```cobra
si x > 0:
    imprimir "positivo"
sino:
    imprimir "no positivo"
fin
```

## Módulos

Los archivos pueden importarse usando `importar`.

```cobra
importar utilidades
```

## Manejo de errores

El bloque `intentar` ... `excepto` captura excepciones.

```cobra
intentar:
    ejecutar_algo()
excepto ErrorComoE:
    imprimir e
fin
```

## Semántica

Cobra evalúa expresiones de izquierda a derecha. Los parámetros se pasan por valor. El ámbito de las variables es estático, determinado por la indentación.

