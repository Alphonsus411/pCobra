Sintaxis de Cobra
=================

***1. Declaracion de variables***

Para declarar variables en Cobra, usamos `var`:

var nombre = "Cobra"
var numero = 10
var año = 1  # Identificadores Unicode permitidos

Los nombres de variables no pueden ser palabras reservadas como ``si`` o ``mientras``. Usarlas como identificador generará un ``SyntaxError``.

**2. Funciones**

Las funciones se declaran con `func` y el cuerpo se delimita con `:`  :

func sumar(a, b) :
    return a + b

Al igual que con las variables, el nombre de la función no puede coincidir con palabras reservadas.

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

**7. Importación de módulos**

Puedes dividir tu código en varios archivos y cargarlos con ``import``:

.. code-block:: cobra

   import 'utilidades.co'
   imprimir(variable_definida_en_utilidades)

**8. Manejo de excepciones**

Para capturar errores se utiliza la estructura ``try`` / ``catch``. Puedes
lanzar excepciones con ``throw``:

.. code-block:: cobra

   try:
       throw "problema"
   catch e:
       imprimir(e)

**9. Concurrencia con hilos**

Es posible ejecutar funciones de forma concurrente:

.. code-block:: cobra

   func trabajo():
       imprimir('hola')
   fin

   hilo trabajo()

**Transpilación a Python y JavaScript**

- `imprimir` se transpila a `print` en Python y a `console.log` en JavaScript.
- Los bucles `mientras` y `para` se convierten en `while` y `for` respectivamente.
- La construcción `holobit` se traduce a `holobit([...])` en Python o `new Holobit([...])` en JavaScript.

