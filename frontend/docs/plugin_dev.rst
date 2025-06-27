Desarrollo de plugins
=====================

Un plugin permite añadir nuevos subcomandos a la CLI de Cobra mediante
paquetes externos. Cada plugin se implementa como una clase que hereda de
``PluginCommand``. La clase define metadatos que se mostrarán en el
subcomando ``plugins``: ``name`` y ``version`` además de ``author`` y
``description``.

Estructura básica
-----------------

.. code-block:: text

   mi_plugin/
       setup.py
       mi_plugin/
           __init__.py
           hola.py

En ``hola.py`` se define la clase del comando:

.. code-block:: python

   from src.cli.plugin_loader import PluginCommand


   class HolaCommand(PluginCommand):
       name = "hola"
       version = "1.0"
       author = "Tu Nombre"
       description = "Muestra un saludo"

       def register_subparser(self, subparsers):
           parser = subparsers.add_parser(self.name, help="Muestra un saludo")
           parser.set_defaults(cmd=self)

       def run(self, args):
           print("¡Hola desde un plugin!")

Registro con ``entry_points``
-----------------------------

Para que Cobra descubra el plugin se declara un ``entry_point`` en
``setup.py``:

.. code-block:: python

   from setuptools import setup

   setup(
       name="mi-plugin",
       version="1.0",
       py_modules=["mi_plugin.hola"],
       entry_points={
           'cobra.plugins': [
               'hola = mi_plugin.hola:HolaCommand',
           ],
       },
   )

Carga dinámica segura
---------------------

Durante el arranque Cobra importa cada plugin a partir de la cadena
``"modulo:Clase"`` definida en el ``entry_point``. La función
``cargar_plugin_seguro`` valida que la clase implementa ``PluginInterface``
antes de instanciarla, registrando el nombre y la versión en el sistema.

Uso
---

Instala el paquete en modo editable y ejecuta el comando:

.. code-block:: bash

   pip install -e .
   cobra plugins
   cobra hola
