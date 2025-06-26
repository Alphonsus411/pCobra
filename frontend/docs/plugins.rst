Sistema de plugins
==================

La CLI de Cobra se puede extender instalando paquetes externos que expongan
un "entry point" en el grupo ``cobra.plugins``. Durante el arranque la
aplicación busca dichos entry points e instancia cada plugin.

Al cargarse, la información de nombre y versión se almacena en un registro
interno accesible desde ``src.cli.plugin_registry``. Para consultar qué
plugins están disponibles se proporciona el subcomando ``plugins``::

   cobra plugins

