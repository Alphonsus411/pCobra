Empaquetar la CLI
=================

Este proyecto puede distribuirse como un ejecutable independiente usando
`PyInstaller <https://pyinstaller.org>`_.

Para generar el ejecutable ejecuta:

.. code-block:: bash

   cobra empaquetar --output dist

Esto creará un archivo ``cobra`` (o ``cobra.exe`` en Windows) en el directorio
``dist``. Se necesita tener ``pyinstaller`` instalado previamente. Puedes
instalarlo con ``pip install pyinstaller``.

Requisitos de plataforma
------------------------

PyInstaller está disponible para Windows, macOS y Linux. El ejecutable sólo
funciona en el mismo sistema operativo donde se creó. Si deseas distribuir para
varias plataformas, debes empaquetar el proyecto en cada una de ellas.
