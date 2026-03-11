Hololang: sintaxis e interoperabilidad
======================================

Hololang es el lenguaje intermedio utilizado por Cobra para describir programas
orientados a holobits con un estilo declarativo inspirado en Rust.  Su IR
funciona como un punto de encuentro entre el AST de Cobra y los backends que
emiten código para otros lenguajes o para ensamblador simbólico.  En esta guía
se resume la sintaxis disponible, cómo integrarla con Cobra y cómo aprovecharla
para generar artefactos adicionales.

.. important::

   Hololang se mantiene como **intermedio no oficial de salida pública**.
   Actualmente no existe un destino CLI registrado como ``hololang`` en
   ``cobra compilar``; su uso está acotado al pipeline interno Cobra → IR → backend.

Sintaxis básica de Hololang
---------------------------

Todo archivo Hololang comienza importando los módulos estándar generados por el
transpilador:

.. code-block:: hololang

   use holo.core::*;
   use holo.bits::*;

A partir de ahí se pueden declarar variables, funciones y holobits utilizando la
siguiente gramática:

* Declaraciones: ``let`` crea variables inmutables y admite anotaciones de tipo
  opcionales.
* Funciones: ``fn`` define rutinas con parámetros separados por comas.
* Bloques: se delimitan con llaves ``{`` y ``}``.
* Impresión: ``print(expr);`` envía datos a la salida estándar.
* Holobits: ``holobit([1.0, -0.5, 0.8]);`` construye estructuras multidimensionales.

Ejemplo completo generado a partir de un programa Cobra:

.. code-block:: hololang

   use holo.core::*;
   use holo.bits::*;

   let saludo = "Hola desde Hololang";

   fn principal() {
       let espectro = holobit([0.8, -0.5, 1.2]);
       print(saludo);
       print("Norma:" + norma(espectro));
   }

   fn norma(holo) {
       return magnitud(holo);
   }

Interoperar con Cobra
---------------------

La CLI de Cobra expone comandos para convertir código entre ambos lenguajes:

* **De Cobra a Hololang:**

  .. code-block:: bash

     cobra compilar examples/hololang/saludo.co --backend python

  El comando anterior genera una salida válida de backend registrado
  (en este ejemplo, ``python``). Hololang se utiliza internamente como IR y no
  como destino público de la CLI.

* **Transpilación inversa disponible en la política actual:**

  .. code-block:: bash

     cobra transpilar-inverso examples/reverse/demo.py \
         --origen python \
         --destino java

  La transpilación inversa soportada por política acepta como origen
  ``python``, ``js`` y ``java``. Si trabajas con Hololang, la ruta recomendada
  es generar Hololang desde Cobra y continuar desde ese artefacto.

Generación de ensamblador desde Hololang
----------------------------------------

Una vez que dispones del código Hololang, puedes convertirlo a ensamblador
simbólico con el backend ``asm`` desde el flujo Cobra → backend:

.. code-block:: bash

   cobra compilar examples/hololang/saludo.co --backend asm

El transpilador ``asm`` produce instrucciones legibles que describen
asignaciones, saltos condicionales y bucles. Esto es útil para auditar
optimizaciones o para integrarse con herramientas de nivel inferior.

Recursos adicionales
--------------------

* Consulta :doc:`sintaxis` para repasar el lenguaje original de Cobra.
* En ``examples/hololang`` encontrarás archivos listos para realizar las
  conversiones mostradas en esta página.
