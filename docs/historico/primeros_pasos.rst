Primeros pasos con Cobra (histórico)
====================================

.. warning::

   Documento histórico / no operativo. Para la guía vigente consulta el
   `Libro de Programación Cobra <../LIBRO_PROGRAMACION_COBRA.md>`_ y el
   `Manual de Cobra <../MANUAL_COBRA.md>`_.

Esta guía se conserva como referencia de versiones anteriores.

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

   cobra run hola.co

Comandos públicos actuales de la CLI:

.. code-block:: bash

   cobra run hola.co
   cobra build hola.co
   cobra test hola.co
   cobra mod list

Para generar la documentación en HTML usa:

.. code-block:: bash

   make html
