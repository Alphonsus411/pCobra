Entorno de desarrollo
=====================

Esta guía explica cómo preparar el entorno para trabajar con la extensión
experimental de VS Code y el servidor LSP.

Instalación de dependencias
---------------------------

1. Instala las dependencias de Python:

   .. code-block:: bash

      pip install -r requirements.txt

2. Para utilizar el servidor LSP ejecuta:

   .. code-block:: bash

      python -m lsp.server

Directorio de la extensión de VS Code
-------------------------------------

Dentro de ``frontend/vscode`` encontrarás una plantilla mínima para la
extensión de Cobra. Puedes abrir dicho directorio en VS Code y modificarla
según tus necesidades.
