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

Cobra fue creado con la idea de facilitar la programación en español y añadir soporte para trabajar con datos complejos como los holobits. En su documentación pública, la salida oficial del proyecto se resume en una sola narrativa: pCobra transpila a 8 backends oficiales agrupados por tiers, con una política separada de runtime, Holobit y SDK.

.. include:: ../_generated/target_policy_summary.rst

La fuente de verdad de esta clasificación está en ``src/pcobra/cobra/config/transpile_targets.py`` y ``src/pcobra/cobra/cli/target_policies.py``. La documentación pública debe usar exclusivamente estos nombres canónicos y no presentar artefactos internos como si fueran backends adicionales.

Repositorio de Ejemplos
----------------------

Los proyectos de demostración se encuentran en `cobra-ejemplos <https://github.com/Alphonsus411/pCobra/tree/work/examples>`_.
