Sistema Qualia
==============

Qualia Spirit registra un historial de todo el codigo ejecutado y analiza el AST resultante. Con esa informacion construye una *base de conocimiento* que contiene:

- ``node_counts``: cu\u00e1ntas veces aparece cada tipo de nodo.
- ``patterns``: peque\u00f1os patrones detectados (``lambda``, ``try_catch``, etc.).
- ``variable_names``: nombres de variables y su frecuencia.
- ``modules_used``: m\u00f3dulos importados durante las ejecuciones.

Todo el estado se guarda en ``qualia_state.json`` para que las recomendaciones se mantengan entre sesiones.

Generaci\u00f3n de sugerencias
---------------------------

A partir de la informaci\u00f3n recolectada, Cobra ofrece sugerencias para
mejorar tus programas. Por ejemplo, si detecta variables con nombres muy
cortos indicar\u00e1 que uses descripciones m\u00e1s claras. Si usas ``pandas`` sin
``matplotlib`` te sugerir\u00e1 incorporar esta \u00faltima para graficar.

Uso del subcomando ``qualia``
-----------------------------

Puedes inspeccionar o reiniciar el estado con el subcomando ``qualia``:

.. code-block:: bash

   cobra qualia mostrar
   cobra qualia reiniciar

El primer comando imprime la base de conocimiento en formato JSON. El segundo
elimina ``qualia_state.json`` y comienza desde cero.

Para ver las sugerencias en el modo interactivo escribe ``sugerencias``.
En Jupyter puedes ejecutar una celda con ``%sugerencias``.
