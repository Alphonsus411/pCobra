Primeros pasos con Cobra
=======================

Esta breve guía explica cómo instalar el proyecto y ejecutar un programa sencillo.

Instalación
-----------

1. Clona el repositorio y entra al directorio:

.. code-block:: bash

   git clone https://github.com/Alphonsus411/pCobra.git
   cd pCobra

2. Crea un entorno virtual y actívalo:

.. code-block:: bash

   python -m venv .venv
   source .venv/bin/activate  # Linux o macOS
   .\\.venv\\Scripts\\activate  # Windows

3. Instala las dependencias y la CLI:

.. code-block:: bash

   pip install -r requirements-dev.txt
   pip install -e .

   # También puedes usar ``pip install -e .[dev]`` para instalar los extras de desarrollo

Uso básico
----------

Puedes ejecutar archivos ``.co`` directamente con la CLI.
Por ejemplo, si tienes ``hola.co``:

.. code-block:: cobra

   imprimir("Hola, Cobra")

Lo ejecutas con:

.. code-block:: bash

   cobra ejecutar hola.co

Para generar la documentación en HTML usa:

.. code-block:: bash

   make html
