Hololang: sintaxis e interoperabilidad
======================================

Hololang es el lenguaje intermedio utilizado por Cobra para describir programas
orientados a holobits con un estilo declarativo inspirado en Rust. Su IR
funciona como un punto de encuentro entre el AST de Cobra y los backends que
emiten código para otros lenguajes o para el target simbólico ``asm``. En esta guía
se resume la sintaxis disponible, cómo integrarla con Cobra y cómo aprovecharla
como artefacto interno del compilador.

.. important::

   Hololang se mantiene como **IR interno/experimental** y **no** como target
   oficial de salida pública. Actualmente no existe un destino CLI registrado
   como ``hololang`` en ``cobra compilar``; su uso está acotado al pipeline
   interno Cobra → IR → backend.

.. warning::

   La política oficial de salida solo reconoce ``python``, ``rust``,
   ``javascript``, ``wasm``, ``go``, ``cpp``, ``java`` y ``asm``. Cualquier
   mención a Hololang en esta página debe leerse como explicación del pipeline
   interno, no como ampliación de los targets soportados.

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

La CLI pública de Cobra no expone a Hololang como destino oficial independiente.
Los flujos soportados públicamente son:

* **Compilar Cobra hacia un backend oficial:**

  .. code-block:: bash

     cobra compilar examples/hola_mundo/hola.co --backend python

  El comando anterior genera una salida válida de backend registrado
  (en este ejemplo, ``python``). Hololang puede intervenir internamente como IR,
  pero no aparece como destino público de la CLI.

* **Transpilación inversa soportada por política:**

  .. code-block:: bash

     cobra transpilar-inverso examples/hello_world/python.py \
         --origen python \
         --destino java

  La transpilación inversa soportada por política acepta como **origen de
  entrada** ``python``, ``javascript`` y ``java``. Estos orígenes reverse no son
  targets oficiales de salida.

.. note::

   El paquete ``src/pcobra/cobra/reverse`` contiene utilidades internas ligadas
   a Hololang. Dichas utilidades no forman parte de la política pública de
   reverse mantenida en ``src/pcobra/cobra/transpilers/reverse/policy.py``.

Generación de `asm` en el pipeline interno
-----------------------------------------

Una vez que el compilador dispone del IR interno, el flujo Cobra → backend puede
terminar en el target canónico ``asm``:

.. code-block:: bash

   cobra compilar examples/hola_mundo/hola.co --backend asm

El transpilador ``asm`` produce instrucciones legibles que describen
asignaciones, saltos condicionales y bucles. Esto es útil para auditar
optimizaciones o para integrarse con herramientas de nivel inferior.

Recursos adicionales
--------------------

* Consulta :doc:`sintaxis` para repasar el lenguaje original de Cobra.
* Usa cualquier programa ``.co`` de ``examples/`` para repetir los flujos mostrados en esta página.
* Revisa ``docs/experimental/`` si necesitas contexto sobre pipelines no oficiales conservados por motivos de investigación.

Política de targets oficial
---------------------------
En documentación pública deben emplearse únicamente nombres canónicos. Para
salida, la referencia obligatoria es ``src/pcobra/cobra/transpilers/targets.py``.
