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

Cobra fue creado con la idea de facilitar la programacion en español, optimizando la gestion de memoria y anadiendo soporte para trabajar con datos de alta complejidad como los holobits. Su cadena de compilación puede apoyarse en una **representación intermedia (IR) interna** para coordinar la transpilación hacia distintos backends. La clasificación pública de destinos y tiers se deriva automáticamente desde la política canónica del proyecto.

.. include:: ../_generated/target_policy_summary.rst

La fuente de verdad de esta clasificación está en ``src/pcobra/cobra/transpilers/targets.py``. La documentación pública debe usar exclusivamente estos nombres canónicos y evitar aliases legacy o targets retirados. Cuando sea útil mencionar la arquitectura, debe describirse únicamente como un pipeline o IR **interno**, sin presentarlo como un lenguaje de usuario ni como un destino oficial adicional.





Repositorio de Ejemplos
----------------------

Los proyectos de demostracion se encuentran en `cobra-ejemplos <https://github.com/Alphonsus411/pCobra/tree/work/examples>`_.
