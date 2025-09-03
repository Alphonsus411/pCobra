Soporte de backends
===================

Cobra permite generar código para varios lenguajes a través del subcomando
``compilar``. A partir de esta versión se incluye un backend experimental para
WebAssembly.

Para obtener el código en formato WAT basta ejecutar:

.. code-block:: bash

   cobra compilar programa.co --backend wasm

El resultado puede compilarse posteriormente con herramientas como
   ``wat2wasm`` para obtener un módulo ejecutable.

También se dispone de un backend sencillo para generar código C::

   cobra compilar programa.co --backend c

Ejemplo de generación de código Rust::

   cobra compilar programa.co --backend rust

produce:

.. code-block:: rust

   struct Persona {}

   impl Persona {
       fn saludar(self) {
           let x = 1;
       }
   }

Además un bloque ``switch`` de Cobra se traduce utilizando ``match``::

.. code-block:: rust

   match x {
       1 => {
           let y = 1;
       },
       2 => {
           let y = 2;
       },
       _ => {
           let y = 0;
       },
   }

Matriz de características
-------------------------

Para un resumen completo de la cobertura por lenguaje, revisa la `matriz de transpiladores <../../docs/matriz_transpiladores.md>`_:

.. include:: ../../docs/matriz_transpiladores.md

Diferencias identificadas
-------------------------

- Go y Java no soportan condicionales ni bucles. Consulta el `issue #11 <../issues/11_soporte_condicionales_bucles_go_java.md>`_ para seguimiento y contribuciones.

