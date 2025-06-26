Benchmarking y medición de rendimiento
======================================

Esta guía explica cómo obtener métricas de ejecución en programas Cobra.
El módulo ``src.core.performance`` se basa en la librería ``smooth-criminal``
y expone los ayudantes ``optimizar`` y ``perfilar`` para decorar funciones o
medir su comportamiento.

Uso de ``perfilar``
-------------------

El siguiente ejemplo ejecuta una función varias veces y devuelve estadísticas
de tiempo:

.. code-block:: python

    from src.core.performance import perfilar

    def sumar(a, b):
        return a + b

    datos = perfilar(sumar, args=(1, 2), repeticiones=10)
    print(datos)

Optimización con ``optimizar``
------------------------------

Si deseas aplicar automáticamente optimizaciones de ``smooth-criminal`` usa
``optimizar`` como decorador:

.. code-block:: python

    from src.core.performance import optimizar

    @optimizar(workers=2)
    def proceso():
        # código intensivo en CPU
        pass

Otras herramientas
------------------

Además de ``smooth-criminal`` puedes emplear la biblioteca estándar
``timeit`` para microbenchmarks rápidos:

.. code-block:: python

    import timeit

    tiempo = timeit.timeit("x = 1 + 1", number=100000)
    print(tiempo)

Para más información sobre configuraciones seguras consulta
:doc:`modo_seguro`.
