Desarrollo de plugins
=====================

Un plugin permite ampliar la CLI de Cobra con nuevos subcomandos
distribuidos como paquetes externos. Todas las utilidades del SDK se
encuentran en ``src.cobra.cli.plugin``. Cada plugin se implementa como una
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
       pyproject.toml
       mi_plugin/
           __init__.py
           hola.py

En ``hola.py`` se define la clase del comando:

.. code-block:: python

   from cobra.cli.plugin import PluginCommand


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

Registro con ``entry points``
-----------------------------

Para que Cobra descubra el plugin se declara un ``entry point`` en
``pyproject.toml`` y se configura un ``build-system`` moderno:

.. code-block:: toml

   [build-system]
   requires = ["setuptools>=61.0"]
   build-backend = "setuptools.build_meta"

   [project]
   name = "mi-plugin"
   version = "1.0"

   [project.entry-points."cobra.plugins"]
   hola = "mi_plugin.hola:HolaCommand"

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

Para conocer la descripción completa de la interfaz disponible consulta
:doc:`plugin_sdk`.
