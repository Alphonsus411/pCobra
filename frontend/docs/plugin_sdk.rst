API de PluginInterface
======================

La clase ``PluginInterface`` define la interfaz mínima que deben implementar los
plugins externos de la CLI. Todas las utilidades del SDK se encuentran ahora en
``src.cli.plugin``. Cada plugin expone metadatos de identificación y dos métodos
esenciales para registrar el subcomando y ejecutar la lógica correspondiente.

Atributos
---------

``name``
    Nombre del subcomando.
``version``
    Versión del plugin.
``author``
    Autor o mantenedor.
``description``
    Descripción breve que aparece en ``cobra plugins``.

Métodos
-------

``register_subparser(subparsers)``
    Recibe el objeto ``argparse`` y debe añadir el subcomando junto con sus
    opciones.

``run(args)``
    Ejecuta la funcionalidad principal del plugin.

Ejemplo de implementación
-------------------------

.. code-block:: python

   from cli.plugin import PluginCommand


   class HolaCommand(PluginCommand):
       name = "hola"
       version = "1.0"
       author = "Tu Nombre"
       description = "Muestra un saludo"

       def register_subparser(self, subparsers):
           parser = subparsers.add_parser(self.name, help=self.description)
           parser.set_defaults(cmd=self)

       def run(self, args):
           print("¡Hola desde un plugin!")

Registro a través de ``entry_points``
------------------------------------

Para que Cobra cargue el plugin se declara un ``entry_point`` en ``setup.py``:

.. code-block:: python

   entry_points={
       'cobra.plugins': [
           'hola = mi_plugin.hola:HolaCommand',
       ],
   }

Gestión de versiones
--------------------

Al instanciarse, cada plugin registra su nombre y versión en el
``plugin_registry`` del módulo ``src.cli.plugin``. Puedes consultarlo con:

.. code-block:: python

   from cli.plugin import obtener_registro

   print(obtener_registro())  # {'hola': '1.0'}

Si actualizas el paquete con una nueva versión, el registro se actualiza de
forma automática cuando Cobra vuelve a cargar el plugin.

Registro y versionado de plugins
--------------------------------

Puedes inspeccionar los plugins cargados y sus versiones mediante el
registro interno. Importa la función ``obtener_registro`` y
muestra su contenido:

.. code-block:: python

   from cli.plugin import obtener_registro

   for nombre, version in obtener_registro().items():
       print(nombre, version)

