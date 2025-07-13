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
- ``leer``
- ``escribir``
- ``existe``
- ``eliminar``
- ``enviar_post``

Reflexión e introspección
-------------------------
Además de las primitivas anteriores, la cadena incluye el ``ValidadorProhibirReflexion``. Este validador bloquea llamadas a ``eval``, ``exec``, ``getattr``, ``setattr`` y ``hasattr``, así como el acceso a ``globals()`` , ``locals()`` o ``vars()`` y a atributos como ``__dict__`` o ``__class__``.

Si se detecta el uso de alguna de estas primitivas, se lanza la excepcion
``PrimitivaPeligrosaError`` antes de que el codigo sea interpretado o transpilado.

Cadena de validadores
---------------------
La función ``construir_cadena`` genera la configuración por defecto uniendo
``ValidadorPrimitivaPeligrosa`` y ``ValidadorImportSeguro``. Es posible añadir
otros validadores pasando una lista a esta función.

.. code-block:: python

   from core.semantic_validators import construir_cadena, ValidadorBase

   class MiValidador(ValidadorBase):
       def visit_mi_nodo(self, nodo):
           # lógica personalizada
           self.generic_visit(nodo)
           self.delegar(nodo)

   cadena = construir_cadena([MiValidador()])

Registro automático de validadores
---------------------------------
Los validadores también pueden cargarse de forma automática desde un módulo
externo mediante la opción ``--validadores-extra`` de la CLI. El módulo debe
definir una lista ``VALIDADORES_EXTRA`` con las instancias a añadir.

.. code-block:: python

   # archivo validadores.py
   from core.semantic_validators.base import ValidadorBase

   class Demo(ValidadorBase):
       def visit_valor(self, nodo):
           self.generic_visit(nodo)
           self.delegar(nodo)

   VALIDADORES_EXTRA = [Demo()]

Posteriormente se indica la ruta al ejecutar Cobra:

.. code-block:: bash

   cobra ejecutar prog.co --seguro --validadores-extra validadores.py

Ejemplo de deteccion
--------------------

.. code-block:: cobra

   leer_archivo('datos.txt')  # Lanzara PrimitivaPeligrosaError
   imprimir('hola')           # Esta linea se considera segura
