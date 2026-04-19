.. Proyecto Cobra documentation master file, created by
   sphinx-quickstart on Tue Oct 15 19:07:40 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Cobra: Documentación del Lenguaje de Programación
================================================

Cobra es un lenguaje de programación experimental completamente en español. Su objetivo es proporcionar un entorno amigable para la simulación, visualización y manipulación de datos complejos, como los holobits, además de facilitar la programación estándar en entornos modernos.

¿Por dónde empezar?
-------------------

- :doc:`/LIBRO_PROGRAMACION_COBRA` como ruta principal de aprendizaje.
- :doc:`/MANUAL_COBRA` como referencia técnica canónica.
- :doc:`/guia_basica` y :doc:`/historico/README` como material secundario e histórico.

.. toctree::
   :maxdepth: 2
   :caption: Contenidos:

   caracteristicas
   arquitectura
   ../estructura_ast
   design_patterns
   cli
   backends
   ../lenguajes_soportados
   ../lenguajes
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
   ../casos_reales
   referencia
   ../standard_library/util
   ../standard_library/numero
   validador
   modo_seguro
   empaquetar
   contenedores
   paquetes
   cobrahub
   cobra_lock
   cache
   instalacion_pypi
   como_contribuir
   ../../CONTRIBUTING
   entorno_desarrollo
   qualia
   jupyter
   recursos_adicionales
   ../MANUAL_COBRA
   api/modules

Introducción
--------------------

Cobra fue creado con la idea de facilitar la programación en español y añadir soporte para trabajar con datos complejos como los holobits. En su documentación pública, la salida oficial del proyecto se resume en una sola narrativa: pCobra transpila a 3 targets oficiales (python, javascript y rust), con una política separada de runtime, Holobit y SDK.

.. include:: ../_generated/target_policy_summary.rst

La fuente de verdad de esta clasificación está en ``src/pcobra/cobra/config/transpile_targets.py`` y ``src/pcobra/cobra/cli/target_policies.py``. La documentación pública debe usar exclusivamente estos nombres canónicos y no presentar artefactos internos como si fueran backends adicionales.

Repositorio de Ejemplos
----------------------

Los proyectos de demostración se encuentran en `cobra-ejemplos <https://github.com/Alphonsus411/pCobra/tree/work/examples>`_.


Contenido histórico
-------------------

Las guías ``primeros_pasos`` y ``sintaxis`` de esta sección se movieron a ``docs/historico/`` como material de referencia histórica/no operativa:

- :doc:`../historico/primeros_pasos`
- :doc:`../historico/sintaxis`

Para el camino principal de aprendizaje usa el Libro y el Manual canónico enlazados en el README del repositorio.
Para evitar duplicidad de onboarding en esta sección frontend, se mantiene aquí solo esta referencia corta.
