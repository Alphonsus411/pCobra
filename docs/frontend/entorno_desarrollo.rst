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

Actualización local tras cambios en imports de CLI
--------------------------------------------------

Cuando cambies imports usados por el entrypoint ``cobra`` (por ejemplo
``pcobra.cli`` o módulos bajo ``src/pcobra/cobra/cli``), actualiza tu entorno
local para evitar que queden rutas cacheadas de instalaciones previas.

Flujo recomendado:

.. code-block:: bash

   python -m pip install -e .[dev] --force-reinstall

Si detectas comportamientos inconsistentes, recrea el entorno virtual:

.. code-block:: bash

   deactivate  # si el venv está activo
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate  # En Windows usa .\\.venv\\Scripts\\activate
   python -m pip install -U pip
   python -m pip install -e .[dev]

Comprobación rápida del entrypoint ya instalado:

.. code-block:: bash

   cobra --ayuda

Directorio de la extensión de VS Code
-------------------------------------

Dentro de ``extensions/vscode`` encontrarás una plantilla mínima para la
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

En ``tests/integration`` encontrarás ``test_kernel_transpiler.py``. Este
script ejecuta el kernel en modo transpiler y comprueba que la salida es la
esperada.
