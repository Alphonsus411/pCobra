Sintaxis de Cobra (histórico)
=============================

.. warning::

   Documento de archivo (no operativo). Este contenido describe convenciones de
   sintaxis usadas en ciclos iniciales de Cobra, previos a la consolidación de
   la documentación canónica actual.

Contexto histórico
------------------

Este documento resume una etapa temprana del lenguaje en la que se difundían
fragmentos sintácticos sueltos para aprendizaje rápido. Se conserva solo para
trazabilidad documental de decisiones y términos usados en versiones anteriores.

Ejemplo legacy
--------------

El siguiente snippet se mantiene únicamente como referencia histórica:

.. code-block:: cobra

   func sumar(a, b) :
       return a + b

   si x > 10 :
       imprimir("x es mayor que 10")
   sino :
       imprimir("x es menor o igual a 10")

Notas de archivo
----------------

- Targets y mecanismos mencionados históricamente pueden no representar el
  contrato vigente.
- Variables de entorno, comandos y flujos de ejecución antiguos se omiten para
  evitar conflicto con la guía actual.

Ruta vigente
------------

- `Libro de Programación Cobra <../LIBRO_PROGRAMACION_COBRA.md>`_
- `Manual de Cobra <../MANUAL_COBRA.md>`_
