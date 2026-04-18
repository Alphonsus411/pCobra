Manual de Cobra
===============

.. note::
   **Estado del documento: Referencia**.
   Este manual es técnico y no reemplaza la ruta didáctica del
   ``LIBRO_PROGRAMACION_COBRA.md``.

Versión 10.0.13

Propósito y alcance
-------------------

Este documento consolida la referencia técnica del lenguaje:

- sintaxis y keywords,
- estructuras de datos y objetos,
- aliases soportados,
- reglas de flujo y errores,
- contrato operativo de la CLI.

Para aprendizaje guiado usa ``LIBRO_PROGRAMACION_COBRA.md``.
Para un resumen breve consulta ``guia_basica.md``.

.. contents:: Índice
   :depth: 2

CLI pública y contrato
----------------------

Comandos oficiales::

   cobra run archivo.co
   cobra build archivo.co
   cobra test archivo.co
   cobra mod list

Los comandos legacy pueden existir por compatibilidad histórica, pero no son la
superficie pública recomendada.

Sintaxis esencial
-----------------

- Asignación: ``x = 1``
- Condicionales: ``si``, ``sino_si`` / ``sino si``, ``sino``
- Bucles: ``mientras``, ``para``
- Funciones: ``funcion`` / ``func``
- Clases: ``clase``
- Comentarios: ``# ...``

Operadores lógicos:

- simbólicos: ``&&``, ``||``, ``!``
- alias: ``y``, ``o``, ``no``

Tipos y estructuras
-------------------

- escalares: texto, números y booleanos,
- listas, diccionarios y otras colecciones según backend,
- objetos con atributos y métodos.

Alias de métodos especiales
---------------------------

Mapeos frecuentes aceptados por el parser:

- ``inicializar`` -> ``__init__``
- ``iterar`` -> ``__iter__``
- ``texto`` -> ``__str__``
- ``representar`` -> ``__repr__``
- ``llamar`` -> ``__call__``
- ``obtener_item`` / ``poner_item`` / ``borrar_item`` ->
  ``__getitem__`` / ``__setitem__`` / ``__delitem__``
- ``entrar`` / ``salir`` -> ``__enter__`` / ``__exit__``
- ``entrar_async`` / ``salir_async`` -> ``__aenter__`` / ``__aexit__``

Si dos declaraciones convergen al mismo nombre especial, el parser reporta
advertencia para evitar colisiones silenciosas.

Control de flujo
----------------

- condicionales encadenados,
- ``romper`` y ``continuar`` en bucles,
- guard clauses con ``garantia`` / ``guard``,
- diferidos con ``defer`` / ``aplazar`` en orden LIFO.

Errores y excepciones
---------------------

- ``try/catch/finally`` y alias ``intentar/capturar/finalmente``,
- ``throw`` / ``lanzar`` para propagar errores,
- ``ExcepcionCobra`` como excepción genérica de runtime.

Módulos e imports
-----------------

La carga de módulos usa ``import`` y variantes por símbolo. El empaquetado con
``cobra.pkg`` permanece como mecanismo legacy para migraciones históricas.

Asincronía y concurrencia
-------------------------

- corrutinas con ``asincronico``,
- espera explícita con ``esperar``,
- helpers asincrónicos expuestos por ``corelibs.asincrono``.

Targets y compatibilidad
------------------------

Targets oficiales priorizados por la documentación pública:

- ``python``
- ``javascript``
- ``rust``

Referencias relacionadas
------------------------

- ``LIBRO_PROGRAMACION_COBRA.md`` (guía pedagógica principal)
- ``guia_basica.md`` (resumen rápido histórico)
- ``SPEC_COBRA.md`` (especificación)
- ``contrato_runtime_holobit.md`` (contratos runtime)
