Entorno de desarrollo
=====================

Esta guía explica cómo preparar el entorno para trabajar con la extensión
experimental de VS Code y el servidor LSP.

Instalación de dependencias
---------------------------

1. Instala las dependencias de Python:

   .. code-block:: bash

      pip install -r requirements-dev.txt

   También puedes ejecutar ``pip install -e .[dev]`` para instalar los extras de desarrollo junto con Cobra.

2. Para utilizar el servidor LSP ejecuta:

   .. code-block:: bash

      python -m lsp.server

Directorio de la extensión de VS Code
-------------------------------------

Dentro de ``src/frontend/vscode`` encontrarás una plantilla mínima para la
extensión de Cobra. Puedes abrir dicho directorio en VS Code y modificarla
según tus necesidades.

Ejemplo de kernel transpiler
----------------------------

Se incluye el cuaderno ``notebooks/ide_demo.ipynb`` que muestra cómo
utilizar el kernel con la variable ``COBRA_JUPYTER_PYTHON`` activada. Para
probarlo ejecuta:

.. code-block:: bash

   export COBRA_JUPYTER_PYTHON=1
   cobra jupyter notebooks/ide_demo.ipynb

El kernel transpilará cada celda a Python y la ejecutará en una *sandbox* con
límites de tiempo y memoria.

.. warning::

   Activar este modo implica ejecutar código Python, lo que puede ser inseguro.
   El kernel mostrará una advertencia al iniciarse.

Pruebas de integración
----------------------

En ``src/tests/integration`` encontrarás ``test_kernel_transpiler.py``. Este
script ejecuta el kernel en modo transpiler y comprueba que la salida es la
esperada.
