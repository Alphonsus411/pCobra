Sintaxis de Cobra
=================

***1. Declaracion de variables***

Para declarar variables en Cobra, usamos `var`:

var nombre = "Cobra"
var numero = 10

**2. Funciones**

Las funciones se declaran con `func` y el cuerpo se delimita con `:`  :

func sumar(a, b) :
    return a + b

**3. Funciones relativas (rel)**

Las funciones relativas se utilizan en contextos temporales específicos:

rel calculo_temporal(x) :
    return x * 2

**4. Condicionales**

Para condicionales, se usan `si` y `sino` :

si x > 10 :
    imprimir("x es mayor que 10")
sino :
    imprimir("x es menor o igual a 10")

**5. Bucles**

Cobra soporta los bucles `mientras` y `para` :

mientras x < 5 :
    imprimir(x)
    x += 1

para var i en rango(5) :
    imprimir(i)

**6. Holobits**

Los holobits permiten trabajar con datos multidimensionales:

var h = holobit([0.8, -0.5, 1.2])
imprimir(h)

**Transpilación a Python y JavaScript**

- `imprimir` se transpila a `print` en Python y a `console.log` en JavaScript.
- Los bucles `mientras` y `para` se convierten en `while` y `for` respectivamente.
- La construcción `holobit` se traduce a `holobit([...])` en Python o `new Holobit([...])` en JavaScript.

