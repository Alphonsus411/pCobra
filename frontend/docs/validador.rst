Validador semantico
===================

El validador semantico recorre el arbol de sintaxis abstracta (AST) para detectar llamadas
que utilizan primitivas consideradas peligrosas. Su finalidad es prevenir que programas
Cobra ejecuten acciones que puedan comprometer al sistema o realicen operaciones
no deseadas durante la fase de analisis.

Primitivas peligrosas
---------------------
Las primitivas actualmente marcadas como peligrosas son:

- ``leer_archivo``
- ``escribir_archivo``
- ``obtener_url``
- ``hilo``

Si se detecta el uso de alguna de estas primitivas, se lanza la excepcion
``PrimitivaPeligrosaError`` antes de que el codigo sea interpretado o transpilado.

Ejemplo de deteccion
--------------------

.. code-block:: cobra

   leer_archivo('datos.txt')  # Lanzara PrimitivaPeligrosaError
   imprimir('hola')           # Esta linea se considera segura
