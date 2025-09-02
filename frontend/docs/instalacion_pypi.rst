Instalación desde PyPI
======================

Sigue los pasos siguientes para instalar ``pcobra`` en un
entorno nuevo y ejecutar un ejemplo básico.

1. **Crea y activa un entorno virtual**:

   .. code-block:: bash

      python -m venv .venv
      source .venv/bin/activate  # En Windows usa .\.venv\Scripts\activate

2. **Instala el paquete desde PyPI**:

   .. code-block:: bash

      pip install pcobra

3. **Verifica que la instalación funciona** ejecutando la CLI:

   .. code-block:: bash

      cobra --version

4. **Ejecuta un programa de prueba** para comprobar el funcionamiento de
   ``cobra``:

   .. code-block:: bash

      echo "imprimir('Hola Cobra')" > hola.co
      cobra ejecutar hola.co

5. **Confirma por escrito** que todo el procedimiento anterior se llevó a
   cabo sin problemas.

