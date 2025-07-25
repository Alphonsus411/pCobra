Empaquetar la CLI
=================

Este proyecto puede distribuirse como un ejecutable independiente usando
`PyInstaller <https://pyinstaller.org>`_. Internamente PyInstaller se
ejecutar\u00e1 sobre ``src/cli/cli.py``. De forma manual podr\u00edas ejecutar
``pyinstaller --onefile src/cli/cli.py -n cobra``.

Para generar el ejecutable ejecuta:

.. code-block:: bash

   cobra empaquetar --output dist

El nombre del ejecutable puede cambiarse con ``--name``. Por ejemplo:

.. code-block:: bash

   cobra empaquetar --name pcobra --output dist

También puedes pasar un archivo ``.spec`` personalizado o incluir archivos
adicionales en el paquete utilizando ``--spec`` y ``--add-data``:

.. code-block:: bash

   cobra empaquetar --spec build/cobra.spec \
       --add-data "all-bytes.dat;all-bytes.dat" --output dist

Esto creará un archivo ``cobra`` (o ``cobra.exe`` en Windows) en el directorio
``dist``. Se necesita tener ``pyinstaller`` instalado previamente. Puedes
instalarlo con ``pip install pyinstaller``.

Requisitos de plataforma
------------------------

PyInstaller está disponible para Windows, macOS y Linux. El ejecutable sólo
funciona en el mismo sistema operativo donde se creó. Si deseas distribuir para
varias plataformas, debes empaquetar el proyecto en cada una de ellas.

Los pasos para generar el binario son idénticos en los tres sistemas operativos:

.. code-block:: bash

   pip install pyinstaller
   cobra empaquetar --output dist

En caso de necesitar archivos adicionales o un ``.spec`` propio, utiliza las
opciones ``--add-data`` y ``--spec`` mostradas anteriormente.
