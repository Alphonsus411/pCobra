Manual de Cobra
===============

Este documento resume la sintaxis y los elementos fundamentales del lenguaje
Cobra. Incluye ejemplos de uso idiomático, limitaciones de los backends y
recomendaciones de estilo.

.. contents:: Índice
   :depth: 2

Preparación del entorno
----------------------

1. Clona el repositorio y entra en ``pCobra``.
2. Crea y activa un entorno virtual.
3. Instala las dependencias con ``pip install -r requirements.txt``.
4. Instala Cobra en modo editable con ``pip install -e .``.

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

Transpilación y ejecución
-------------------------

El comando ``cobra compilar`` genera código para múltiples lenguajes. También
puede ejecutarse un archivo directamente con ``cobra ejecutar``.
El subcomando ``cobra verificar`` permite comparar la salida de un programa
transpilado a distintos lenguajes (actualmente Python y JavaScript) y avisa si
alguna difiere.

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

Recursos adicionales
--------------------

- :doc:`guia_basica <guia_basica>`
- :doc:`especificacion_tecnica <especificacion_tecnica>`
- :doc:`recursos_adicionales <../frontend/docs/recursos_adicionales>`
