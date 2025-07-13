Ejemplos Avanzados
===================

En esta sección se presentan programas más complejos escritos en Cobra. Se
incluyen ejemplos con clases, uso de hilos y manejo de errores para ilustrar las
capacidades del lenguaje.

Clases
------
.. code-block:: cobra

   clase Persona:
       func __init__(self, nombre):
           self.nombre = nombre
       fin

       func saludar(self):
           imprimir("Hola, soy " + self.nombre)
       fin
   fin

   var p = Persona("Ada")
   p.saludar()

Hilos
-----
.. code-block:: cobra

   func contar():
       para var i en rango(3):
           imprimir(i)
       fin
   fin

   hilo contar()
   hilo contar()

En este ejemplo se crean dos hilos que ejecutan la funcion ``contar`` de forma concurrente. Cada hilo imprime los numeros del 0 al 2 utilizando la instruccion ``hilo`` para realizar trabajo en paralelo.
Funciones asíncronas
--------------------
.. code-block:: cobra

   asincronico func saludo():
       imprimir("hola")
   fin

   asincronico func principal():
       esperar saludo()
   fin

   esperar principal()

Las funciones marcadas como ``asincronico`` se ejecutan sin bloquear el hilo principal. La palabra clave ``esperar`` se utiliza para pausar la corrutina hasta que la tarea finalice.
Manejo de errores
-----------------
.. code-block:: cobra

   func dividir(a, b):
       si b == 0:
           throw "Division por cero"
       sino:
           return a / b
       fin
   fin

   try:
       imprimir(dividir(10, 0))
   catch e:
       imprimir("Error:" + e)
   fin

Bibliotecas C con ctypes
------------------------
.. code-block:: cobra

   var triple = cargar_funcion('libtriple.so', 'triple')
   imprimir(triple(5))

Casos de Uso Reales
===================

Los programas completos que muestran Cobra en escenarios reales se encuentran
en el directorio ``casos_reales/`` de este repositorio. A continuación se
resume cada ejemplo y se incluye el código principal para referencia.

Bioinformática
--------------

En ``casos_reales/bioinformatica/`` se calcula el porcentaje de GC de una
secuencia en formato FASTA. El script es el siguiente:

.. literalinclude:: ../../casos_reales/bioinformatica/ejemplo_gc.co
   :language: cobra

Revisa el archivo ``README.md`` de la carpeta para los pasos de compilación y
ejecución.

Análisis de Datos
-----------------

``casos_reales/analisis_datos/`` contiene un programa que procesa un CSV con
``pandas`` para calcular el promedio de una columna:

.. literalinclude:: ../../casos_reales/analisis_datos/estadisticas.co
   :language: cobra

El ``README.md`` explica cómo transpilar a Python y ejecutar el resultado.

Inteligencia Artificial
-----------------------

En ``casos_reales/inteligencia_artificial/`` se muestra cómo cargar un modelo de
``scikit-learn`` y realizar una predicción:

.. literalinclude:: ../../casos_reales/inteligencia_artificial/modelo_ia.co
   :language: cobra

Consulta el ``README.md`` para conocer las dependencias y el proceso de ejecución.

Uso de plugins
--------------

Cobra puede extenderse con plugins escritos en Python que heredan de
``PluginCommand``. Un ejemplo básico es:

.. code-block:: python

   from cli.plugin import PluginCommand

   class SaludoCommand(PluginCommand):
       name = "saludo"
       version = "1.0"

       def register_subparser(self, subparsers):
           parser = subparsers.add_parser(self.name, help="Muestra un saludo")
           parser.set_defaults(cmd=self)

       def run(self, args):
           print("¡Hola desde un plugin!")

Instala el paquete que contiene este código con ``pip install -e .`` y luego
invoca ``cobra saludo`` para verificarlo.
