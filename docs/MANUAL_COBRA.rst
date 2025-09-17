Manual de Cobra
===============

Versión 10.0.9

Este documento resume la sintaxis y los elementos fundamentales del lenguaje
Cobra. Incluye ejemplos de uso idiomático, limitaciones de los backends y
recomendaciones de estilo.

.. contents:: Índice
   :depth: 2

Preparación del entorno
----------------------

1. Clona el repositorio y entra en ``pCobra``.
2. Crea y activa un entorno virtual de **Python 3.9 o superior**.
3. Instala las dependencias con ``pip install -r requirements-dev.txt``.
4. Instala Cobra en modo editable con ``pip install -e .``.

   También puedes ejecutar ``pip install -e .[dev]`` para incluir los extras de
   desarrollo.

Sintaxis básica
---------------

* Declaración de variables con ``var``:

  .. code-block:: cobra

     var mensaje = "Hola"

* Funciones con ``func`` y finalización opcional con ``fin``:

  .. code-block:: cobra

     func sumar(a, b):
         return a + b
     fin

* Condicionales ``si``/``sino`` y bucles ``mientras``/``para``:

  .. code-block:: cobra

     si x > 0:
         imprimir(x)
     sino:
         imprimir(0)

Tipos y estructuras de datos
----------------------------

Cobra soporta números, cadenas, listas, diccionarios y conjuntos. Las clases se
crean con ``clase`` y se instancian como en Python.

.. code-block:: cobra

   clase Persona:
       func __init__(self, nombre):
           self.nombre = nombre
       fin

   var p = Persona("Ada")
   imprimir(p.nombre)

Módulos y paquetes
------------------

Los módulos se importan con ``import``. Para agrupar varios módulos puede
crearse un archivo ``cobra.pkg`` y usar ``cobra paquete crear`` para
empaquetarlos.

Macros y concurrencia
---------------------

La directiva ``macro`` permite insertar código reutilizable. Para lanzar tareas
en paralelo se utiliza ``hilo``.

.. code-block:: cobra

   macro saluda { imprimir("hola") }
   hilo saluda()

Funciones asincrónicas
----------------------

Para definir corrutinas se emplea la palabra clave ``asincronico`` y se espera
su resultado con ``esperar``.

.. code-block:: cobra

   asincronico func saluda():
       imprimir(1)
   fin

   asincronico func principal():
       esperar saluda()
   fin

   esperar principal()

Decoradores
-----------

Se declaran anteponiendo ``@`` al nombre de la función que se desea modificar.

.. code-block:: cobra

   @log
   func hola():
       imprimir("hola")
   fin

Manejo de excepciones
---------------------

Las excepciones pueden atraparse con ``try``/``catch`` o sus alias
``intentar``/``capturar``.

.. code-block:: cobra

   intentar:
       abrir("no_existe.txt")
   capturar e:
       imprimir("Error:" + e)
   fin

Ejemplos adicionales
--------------------

Suma de matrices::

   func sumar_matriz():
       var a11 = 1
       var a12 = 2
       var a21 = 3
       var a22 = 4

       var b11 = 5
       var b12 = 6
       var b21 = 7
       var b22 = 8

       imprimir(a11 + b11)
       imprimir(a12 + b12)
       imprimir(a21 + b21)
       imprimir(a22 + b22)
   fin

   sumar_matriz()

Factorial recursivo::

   func factorial(n):
       si n <= 1:
           retorno 1
       sino:
           retorno n * factorial(n - 1)
       fin
   fin

   imprimir(factorial(5))

Operaciones numéricas con ``corelibs.numero``
--------------------------------------------

La biblioteca estándar también incluye utilidades numéricas inspiradas en
``math`` y ``statistics`` de Python. Permiten normalizar valores, generar
aleatorios reproducibles y analizar datos sin abandonar Cobra.

.. code-block:: python

   import pcobra.corelibs as core

   medidas = [1.2, 1.8, 2.0, 2.5]
   print(core.absoluto(-3))
   print(core.redondear(3.14159, 3))
   print(core.clamp(5, 0, 3))
   print(core.mediana(medidas))
   print(core.desviacion_estandar(medidas, muestral=True))

.. list-table:: Equivalencias con bibliotecas numéricas
   :header-rows: 1
   :widths: 20 25 25 30

   * - Cobra
     - Python ``math``/``statistics``
     - ``numpy``
     - JavaScript ``Math``
   * - ``absoluto(x)``
     - ``math.fabs(x)``
     - ``numpy.abs(x)``
     - ``Math.abs(x)``
   * - ``redondear(x, n)``
     - ``round(x, n)``
     - ``numpy.round(x, n)``
     - ``Math.round(x * 10**n) / 10**n``
   * - ``piso(x)``
     - ``math.floor(x)``
     - ``numpy.floor(x)``
     - ``Math.floor(x)``
   * - ``techo(x)``
     - ``math.ceil(x)``
     - ``numpy.ceil(x)``
     - ``Math.ceil(x)``
   * - ``raiz(x, n)``
     - ``math.pow(x, 1/n)``
     - ``numpy.power(x, 1/n)``
     - ``Math.pow(x, 1/n)``
   * - ``potencia(a, b)``
     - ``math.pow(a, b)``
     - ``numpy.power(a, b)``
     - ``Math.pow(a, b)``
   * - ``clamp(x, a, b)``
     - ``min(max(x, a), b)``
     - ``numpy.clip(x, a, b)``
     - ``Math.min(Math.max(x, a), b)``
   * - ``aleatorio(a, b)``
     - ``random.uniform(a, b)``
     - ``numpy.random.uniform(a, b)``
     - ``Math.random() * (b - a) + a``
   * - ``mediana(datos)``
     - ``statistics.median(datos)``
     - ``numpy.median(datos)``
     - «Sin equivalente directo; ordenar y promediar»
   * - ``moda(datos)``
     - ``statistics.mode(datos)``
     - ``numpy.unique(datos, return_counts=True)``
     - «Sin equivalente directo; contar frecuencias»
   * - ``desviacion_estandar(datos)``
     - ``statistics.pstdev(datos)``
     - ``numpy.std(datos)``
     - «Sin equivalente directo; implementar manualmente»

Transpilación y ejecución
-------------------------

El comando ``cobra compilar`` genera código para múltiples lenguajes. También
puede ejecutarse un archivo directamente con ``cobra ejecutar``.
El subcomando ``cobra verificar`` (``cobra verify`` en la versión en inglés)
permite comparar la salida de un programa transpilado a distintos lenguajes
(actualmente Python y JavaScript) y avisa si alguna difiere.
Adicionalmente puedes convertir código escrito en otros lenguajes a Cobra y
volver a transpilarlos con ``cobra transpilar-inverso``::

   cobra transpilar-inverso ejemplo.py --origen=python --destino=js

Limitaciones de los backends
----------------------------

* **Python y JavaScript**: implementan la mayoría de características y son los
  más estables.
* **C y C++**: se consideran experimentales; no soportan clases ni excepciones
  complejas.
* **Rust**: carece de herencia múltiple y requiere anotaciones de tipo
  explícitas para estructuras complejas.
* **WebAssembly**: limitado a operaciones numéricas básicas y sin soporte de
  cadenas.
* **Otros backends** (Go, R, Julia, etc.): poseen cobertura parcial y pueden
  carecer de bibliotecas estándar equivalentes.

Recomendaciones de estilo
-------------------------

* Utiliza indentación de cuatro espacios y nombres en ``snake_case``.
* Mantén los comentarios en español y procura líneas de menos de 79 caracteres.
* Prefiere expresiones claras antes que construcciones complejas y evita macros
  innecesarias.

Funciones del sistema
---------------------

La biblioteca estándar expone ``corelibs.sistema.ejecutar`` para lanzar procesos del
sistema. Por motivos de seguridad es **obligatorio** proporcionar una lista blanca de
ejecutables permitidos mediante el parámetro ``permitidos`` o definiendo la variable
de entorno ``COBRA_EJECUTAR_PERMITIDOS`` separada por ``os.pathsep``. La lista se
captura al importar el módulo, por lo que modificar la variable de entorno después no
surte efecto. Invocar la función sin esta configuración producirá un ``ValueError``.

Limitaciones de recursos en Windows
-----------------------------------

En sistemas Windows, las funciones que intentan limitar la memoria o el tiempo
de CPU pueden no aplicarse. Cobra mostrará advertencias como::

   No se pudo establecer el límite de memoria en Windows; el ajuste se omitirá.
   No se pudo establecer el límite de CPU en Windows; el ajuste se omitirá.

Para asegurar estos límites, ejecuta Cobra dentro de un contenedor (por
ejemplo, Docker o WSL2) donde las restricciones de recursos sí se pueden
aplicar.

Recursos adicionales
--------------------

- :doc:`guia_basica <guia_basica>`
- :doc:`especificacion_tecnica <especificacion_tecnica>`
- :doc:`recursos_adicionales <frontend/recursos_adicionales>`
