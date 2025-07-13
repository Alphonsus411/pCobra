Desarrollo de plugins
=====================

Un plugin permite ampliar la CLI de Cobra con nuevos subcomandos
distribuidos como paquetes externos. Todas las utilidades del SDK se
encuentran en ``src.cli.plugin``. Cada plugin se implementa como una
clase que hereda de ``PluginCommand``. Esta clase define varios metadatos

(``name``, ``version``, ``author`` y ``description``) que se mostrarán al
ejecutar ``cobra plugins``.

.. _patron_command:

Patrón Command
--------------

``PluginCommand`` aplica el patrón *Command* para encapsular la lógica de cada
subcomando. Cuando la clase derivada registra su ``register_subparser`` la
acción queda disponible en la CLI y se ejecuta al invocar ``run``.

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

   from cli.plugin import PluginCommand


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
``cargar_plugin_seguro`` valida que la clase implementa
``PluginInterface`` y que define todos los metadatos requeridos. Solo en
ese caso se instancia el plugin y se registra su nombre y versión en el
sistema.

Uso
---

Instala el paquete en modo editable y ejecuta los siguientes comandos
para verificar que Cobra detecta tu plugin:

.. code-block:: bash

   pip install -e .
   cobra plugins   # muestra los metadatos registrados
   cobra hola      # ejecuta el nuevo subcomando
