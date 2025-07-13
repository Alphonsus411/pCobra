Benchmarking y medición de rendimiento
======================================

Esta guía explica cómo obtener métricas de ejecución en programas Cobra.
Desde la versión 9.0 se incluye una pequeña suite de benchmarking basada en el
módulo ``src.core.performance`` y la librería ``smooth-criminal``. Dicho módulo
expone los ayudantes ``optimizar`` y ``perfilar`` para decorar funciones o medir
su comportamiento.

Uso de ``perfilar``
-------------------

El siguiente ejemplo ejecuta una función varias veces y devuelve estadísticas
de tiempo:

.. code-block:: python

    from core.performance import perfilar

    def sumar(a, b):
        return a + b

    datos = perfilar(sumar, args=(1, 2))
    print(datos)

Optimización con ``optimizar``
------------------------------

Si deseas aplicar automáticamente optimizaciones de ``smooth-criminal`` usa
``optimizar`` como decorador:

.. code-block:: python

    from core.performance import optimizar

    @optimizar()
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

Resultados recientes
--------------------

Los benchmarks pueden ejecutarse con ``cobra bench``. El siguiente
resumen se obtuvo con ``scripts/benchmarks/compare_backends.py``.

Las cifras que se muestran a continuación corresponden a Cobra 9.0.

También puedes ejecutar el script manualmente:

.. code-block:: bash

   python scripts/benchmarks/compare_backends.py --output salida.json

.. list-table:: Tiempos y memoria aproximados
   :header-rows: 1

   * - Backend
     - Tiempo (s)
     - Memoria (KB)
   * - cobra
     - 0.95
     - 64000
   * - python
     - 0.10
     - 0
   * - js
     - 0.05
     - 0

Pruebas de mutación
-------------------

Para evaluar la efectividad de las pruebas se incluye un script que ejecuta
`MutPy` sobre el código fuente. Primero instala la dependencia opcional:

.. code-block:: bash

   pip install .[mutation]

Luego lanza el análisis:

.. code-block:: bash

   python scripts/run_mutation.py

Se recomienda alcanzar un porcentaje de detección de mutantes de al
menos 70 %.

Benchmark de transpiladores
---------------------------

Para medir la velocidad de cada transpilador puedes ejecutar ``cobra
benchtranspilers``. Este comando genera programas pequeños, medianos y
grandes y calcula el tiempo que tarda cada transpilador en producir el
código de salida. Con la opción ``--profile`` se registra un informe
detallado en ``bench_transpilers.prof``.

Ejemplo:

.. code-block:: bash

   cobra benchtranspilers --output transpilers.json

El archivo resultante es una lista de objetos con las claves
``size`` (tamaño del programa), ``lang`` (lenguaje de salida) y
``time`` (segundos de ejecución).

Benchmark de hilos
------------------

El comando ``cobra benchthreads`` ejecuta un programa con y sin hilos
usando tanto la CLI como el kernel de Jupyter. La salida es un JSON con
los tiempos totales, uso de CPU y operaciones de E/S.

.. code-block:: bash

   cobra benchthreads --output threads.json


