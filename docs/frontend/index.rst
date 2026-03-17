.. Proyecto Cobra documentation master file, created by
   sphinx-quickstart on Tue Oct 15 19:07:40 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Cobra: Documentación del Lenguaje de Programación
================================================

Cobra es un lenguaje de programación experimental completamente en español. Su objetivo es proporcionar un entorno amigable para la simulación, visualización y manipulación de datos complejos, como los holobits, además de facilitar la programación estándar en entornos modernos.

.. toctree::
   :maxdepth: 2
   :caption: Contenidos:

   caracteristicas
   arquitectura
   ../../docs/estructura_ast
   design_patterns
   cli
   backends
   ../../docs/lenguajes_soportados
   ../../docs/lenguajes
   sintaxis
   hololang
   avances
   proximos_pasos
   optimizaciones
   benchmarking
   modulos_nativos
   plugins
   plugin_dev
   plugin_sdk
   rfc_plugins
   ejemplos
   ejemplos_avanzados
   ../../docs/casos_reales
   referencia
   ../../docs/standard_library/util
   ../../docs/standard_library/numero
   validador
   modo_seguro
   empaquetar
   contenedores
   paquetes
   cobrahub
   cobra_lock
   cache
   instalacion_pypi
   primeros_pasos
   como_contribuir
   ../../CONTRIBUTING
   entorno_desarrollo
   qualia
   jupyter
   recursos_adicionales
   ../../docs/MANUAL_COBRA
   api/modules

Introducción
--------------------

Cobra fue creado con la idea de facilitar la programacion en español, optimizando la gestion de memoria y anadiendo soporte para trabajar con datos de alta complejidad como los holobits. Su cadena de compilación incorpora Hololang como lenguaje intermedio para coordinar la transpilación hacia distintos backends. Actualmente, los destinos canónicos de salida son: ``python``, ``rust``, ``javascript``, ``wasm``, ``go``, ``cpp``, ``java`` y ``asm``.

Tier de soporte de backends:

* **Tier 1**: ``python``, ``rust``, ``javascript``, ``wasm``.
* **Tier 2**: ``go``, ``cpp``, ``java``, ``asm``.

La fuente de verdad de esta clasificación está en ``src/pcobra/cobra/transpilers/targets.py``.





Repositorio de Ejemplos
----------------------

Los proyectos de demostracion se encuentran en `cobra-ejemplos <https://github.com/Alphonsus411/pCobra/tree/work/examples>`_.
