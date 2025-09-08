Optimizaciones del AST
======================

El proyecto incluye un conjunto de visitantes que mejoran el \ *performance\* del código generado o ejecutado. Actualmente existen cuatro optimizaciones sencillas:

Plegado de constantes
---------------------
``optimize_constants`` recorre el AST evaluando expresiones cuyos operandos son valores literales. De esta forma, operaciones como ``2 + 3`` se reemplazan por ``5`` antes de la interpretación o de la transpilación.

Eliminación de código muerto
----------------------------
``remove_dead_code`` elimina instrucciones que nunca se ejecutarán. Por ejemplo, todo lo que aparezca después de ``return`` dentro de una función se descarta y, si un condicional tiene una condición constante, solo se conserva la rama correspondiente.

Integración de funciones simples
--------------------------------
``inline_functions`` identifica funciones sin parámetros y con un único ``return`` para sustituir sus llamadas por el valor retornado, eliminando además la definición original cuando es posible.

Eliminación de subexpresiones comunes
------------------------------------
``eliminate_common_subexpressions`` detecta expresiones idénticas que se repiten dentro de una misma función o en el nivel global. Dichas expresiones se calculan una única vez asignándose a una variable temporal y las repeticiones se reemplazan por el identificador generado.

Estas optimizaciones se aplican automáticamente antes de ejecutar el intérprete y en los transpiladores a Python, JavaScript, ensamblador, Rust, C++, Go, Kotlin, Swift, R, Julia, Java, COBOL, Fortran, Pascal, Ruby, PHP, Perl, VisualBasic, Matlab, Mojo, LaTeX, C y WebAssembly.

Decoradores de rendimiento (``Smooth Criminal``)
------------------------------------------------
Se incorporó la biblioteca ``smooth-criminal`` al núcleo para facilitar la optimización de funciones de usuario. Desde ``src.core`` se exponen los ayudantes ``optimizar`` y ``perfilar`` que utilizan dicha librería para aplicar decoradores como ``bad``, ``bad_and_dangerous`` o ``jam`` y obtener métricas de ejecución.

Ejemplo de uso con herramientas nuevas
--------------------------------------

.. code-block:: python

    from core.performance import perfilar, bad_and_dangerous, jam

    def suma(x, y):
        return x + y

    # Métricas detalladas con ``bad_and_dangerous``
    datos = bad_and_dangerous(suma, args=(1, 2), repeat=3)

    # Decorador ``jam`` para optimizar bucles
    @jam(loops=5)
    def incrementa(x):
        return x + 1

    resultado = incrementa(10)

    # Profiling sencillo mediante ``perfilar``
    estadisticas = perfilar(suma, args=(2, 3), repeticiones=4)
