Validador semantico
===================

El sistema de validación semántica se compone de varios validadores encadenados que
recorren el árbol de sintaxis abstracta (AST). Cada validador puede realizar una
comprobación y delegar en el siguiente. De esta forma es sencillo añadir nuevas
reglas de seguridad sin modificar el resto del código.

Primitivas peligrosas
---------------------
Las primitivas actualmente marcadas como peligrosas son:

- ``leer_archivo``
- ``escribir_archivo``
- ``obtener_url``
- ``hilo``

Si se detecta el uso de alguna de estas primitivas, se lanza la excepcion
``PrimitivaPeligrosaError`` antes de que el codigo sea interpretado o transpilado.

Cadena de validadores
---------------------
La función ``construir_cadena`` genera la configuración por defecto uniendo
``ValidadorPrimitivaPeligrosa`` y ``ValidadorImportSeguro``. Es posible añadir
otros validadores pasando una lista a esta función.

.. code-block:: python

   from src.core.semantic_validators import construir_cadena, ValidadorBase

   class MiValidador(ValidadorBase):
       def visit_mi_nodo(self, nodo):
           # lógica personalizada
           self.generic_visit(nodo)
           self.delegar(nodo)

   cadena = construir_cadena([MiValidador()])

Ejemplo de deteccion
--------------------

.. code-block:: cobra

   leer_archivo('datos.txt')  # Lanzara PrimitivaPeligrosaError
   imprimir('hola')           # Esta linea se considera segura
