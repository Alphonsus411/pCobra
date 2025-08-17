Sistema de plugins
==================

La CLI de Cobra se puede extender instalando paquetes externos que expongan
un "entry point" en el grupo ``cobra.plugins``. Durante el arranque la
aplicación busca dichos entry points e instancia cada plugin. Todas las
utilidades necesarias se importan desde ``src.cli.plugin``.

Para un tutorial detallado sobre cómo desarrollar plugins consulta
:doc:`plugin_dev`.

Al cargarse, la información de nombre y versión se almacena en un registro
interno accesible desde ``src.cli.plugin``. Para consultar qué
plugins están disponibles se proporciona el subcomando ``plugins``::

   cobra plugins

.. code-block:: text

   saludo 1.0 - Comando de saludo de ejemplo

Guía paso a paso
----------------

A continuación se muestra cómo crear un plugin sencillo utilizando
``PluginCommand``.

1. **Crea un módulo Python** donde se implementará el plugin. Por ejemplo,
   ``mi_paquete/mi_plugin.py``.
2. **Importa** ``PluginCommand`` e implementa una clase que herede de ella:

     .. code-block:: python

        from cli.plugin import PluginCommand


      class SaludoCommand(PluginCommand):
          name = "saludo"
          version = "1.0"

          def register_subparser(self, subparsers):
              parser = subparsers.add_parser(self.name, help="Muestra un saludo")
              parser.set_defaults(cmd=self)

          def run(self, args):
              print("¡Hola desde un plugin!")

3. **Declara el entry point** en ``pyproject.toml`` y configura un sistema de
   construcción moderno:

   .. code-block:: toml

      [build-system]
      requires = ["setuptools>=61.0"]
      build-backend = "setuptools.build_meta"

      [project.entry-points."cobra.plugins"]
      saludo = "mi_paquete.mi_plugin:SaludoCommand"

4. **Instala el paquete** en modo editable con ``pip install -e .`` para que
   el comando quede disponible.
5. **Comprueba la instalación** ejecutando ``cobra plugins``. Deberías ver el
   nombre y la versión registrados.
6. **Utiliza tu plugin** directamente desde la CLI:

   .. code-block:: bash

      cobra saludo

Con estos pasos se crea un plugin funcional que se integra de forma automática
con el sistema de comandos de Cobra.

Para una descripción completa de la interfaz disponible consulta
:doc:`plugin_sdk`.

Ejemplo: convertir Markdown a Cobra
-----------------------------------

Dentro de ``examples/plugins`` se incluye el plugin ``md2cobra`` que extrae
los bloques de código iniciados con `````cobra```` de un archivo Markdown y los
guarda en un script ``.co``. Para instalarlo y utilizarlo ejecuta::

   pip install -e examples/plugins

Una vez instalado, el subcomando queda disponible::

   cobra md2cobra --input notas.md --output resultado.co

Ejemplo completo
----------------
``SaludoCommand`` está disponible en
``examples/plugins/saludo_plugin.py``. Para instalarlo en modo editable
ejecuta:

.. code-block:: bash

   cd examples/plugins
   pip install -e .

Comprueba que queda registrado con:

.. code-block:: bash

   cobra plugins

.. code-block:: text

   saludo 1.0 - Comando de saludo de ejemplo

Finalmente, prueba el comando:

.. code-block:: bash

   cobra saludo

.. code-block:: text

   ¡Hola desde el plugin de ejemplo!

Ejemplo: mostrar la hora actual
-------------------------------
``HoraCommand`` se encuentra en ``examples/plugins/hora_plugin.py`` y muestra
la hora actual. Tras instalar los ejemplos de plugins con ``pip install -e``
podrás ejecutar:

.. code-block:: bash

   cobra hora

.. code-block:: text

   Hora actual: 12:34:56

