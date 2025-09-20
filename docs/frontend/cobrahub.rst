CobraHub
========

CobraHub es un repositorio centralizado donde se pueden compartir módulos Cobra.
La CLI integra dos acciones para interactuar con este servicio: ``publicar`` y
``buscar`` dentro del subcomando ``modulos``.

Publicar un módulo
------------------

Para subir un archivo ``.co`` a CobraHub ejecuta:

.. code-block:: bash

   cobra modulos publicar ruta/al/modulo.co

Si la operación es exitosa se mostrará un mensaje indicando que el módulo fue
publicado correctamente.

Buscar un módulo
----------------

Los módulos disponibles pueden descargarse con:

.. code-block:: bash

   cobra modulos buscar nombre.co

El archivo se guardará en el directorio de módulos configurado. Puedes cambiar
la URL del servicio estableciendo la variable de entorno ``COBRAHUB_URL``.

Diálogo asistido desde la terminal
---------------------------------

Cuando la CLI requiere más contexto (por ejemplo, credenciales o etiquetas del
módulo) utiliza las utilidades de ``standard_library.interfaz`` para guiar el
proceso. En pantalla verás algo similar a lo siguiente:

.. code-block:: text

   ¿Nombre para publicar en CobraHub? [demo_modulo]:
   ¿Elige la visibilidad? (privado/público) [público]: público
   ¿Cuántas etiquetas vas a registrar? 3

Los campos se validan automáticamente y se muestran las opciones disponibles en
colores, lo que facilita publicar en CobraHub desde entornos como Codespaces o
Replit sin necesidad de interfaces gráficas adicionales.
