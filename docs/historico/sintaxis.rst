Sintaxis de Cobra (histórico)
=============================

.. warning::

   Documento histórico / no operativo. Para la sintaxis y contrato vigentes
   consulta el `Libro de Programación Cobra <../LIBRO_PROGRAMACION_COBRA.md>`_
   y el `Manual de Cobra <../MANUAL_COBRA.md>`_.

***1. Declaración de variables***

Para declarar variables en Cobra, usamos `var`:

var nombre = "Cobra"
var numero = 10
var año = 1  # Identificadores Unicode permitidos

Los nombres de variables no pueden ser palabras reservadas como ``si`` o ``mientras``.
Usarlas como identificador generará un ``ParserError``.

**2. Funciones**

Las funciones se declaran con `func` y el cuerpo se delimita con `:`:

func sumar(a, b) :
    return a + b

Al igual que con las variables, el nombre de la función no puede coincidir con palabras reservadas.

**3. Condicionales**

Para condicionales, se usan `si` y `sino`:

si x > 10 :
    imprimir("x es mayor que 10")
sino :
    imprimir("x es menor o igual a 10")

**4. Bucles**

Cobra soporta los bucles `mientras` y `para`:

mientras x < 5 :
    imprimir(x)
    x += 1

para var i en rango(5) :
    imprimir(i)

**5. Holobits**

Los holobits permiten trabajar con datos multidimensionales:

var h = holobit([0.8, -0.5, 1.2])
imprimir(h)

**6. Importación de módulos**

Puedes dividir tu código en varios archivos y cargarlos con ``import``:

.. code-block:: cobra

   import 'utilidades.co'
   imprimir(variable_definida_en_utilidades)

**7. Manejo de excepciones**

Para capturar errores se utiliza la estructura ``try`` / ``catch``. Puedes
lanzar excepciones con ``throw``:

.. code-block:: cobra

   try:
       throw "problema"
   catch e:
       imprimir(e)

**8. Concurrencia con hilos**

Es posible ejecutar funciones de forma concurrente:

.. code-block:: cobra

   func trabajo():
       imprimir('hola')
   fin

   hilo trabajo()

**9. Decoradores de funciones**

Puedes anteponer `@` a una función para modificar su comportamiento con un decorador:

.. code-block:: cobra

   @temporizador
   func saluda():
       imprimir('hola')
   fin

**Targets oficiales de salida (estado vigente)**

Cobra documenta como salida oficial únicamente a ``python``, ``javascript`` y ``rust``.

- ``python``: soporte contractual ``full``.
- ``javascript`` y ``rust``: soporte contractual ``partial``.

Targets legacy como ``wasm``, ``go``, ``cpp``, ``java`` y ``asm`` se tratan como
históricos/internos y no forman parte del contrato público de salida.

Activar el parser de Lark
-------------------------

Si deseas utilizar el parser alternativo implementado con ``Lark`` establece la variable
 de entorno ``COBRA_PARSER`` a ``lark`` antes de ejecutar Cobra:

.. code-block:: bash

   export COBRA_PARSER=lark
   cobra run programa.co

Si no defines esta variable se seguirá empleando el parser tradicional.
