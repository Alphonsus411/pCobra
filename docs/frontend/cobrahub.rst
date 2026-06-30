CobraHub
========

CobraHub es el punto de publicación, búsqueda e instalación de artefactos Cobra.
El flujo recomendado trabaja con paquetes ``.co`` construidos por la capa de
empaquetado ``pcobra.cobra.packaging``. Para el formato completo de paquetes y
las notas de diseño consulta :doc:`paquetes` y el documento
``../cobrahub_paquetes.md``. Ese documento también recoge el contrato HTTP
mínimo provisional para ``POST /paquetes``, ``GET /paquetes?q=consulta`` y
``GET /paquetes/{nombre}``, compatible con una futura infraestructura tipo PyPI.

Flujo recomendado de paquetes
-----------------------------

El flujo principal separa la preparación local del paquete de las operaciones
contra CobraHub:

1. Crear una estructura inicial de paquete:

   .. code-block:: bash

      cobra paquete crear mi_paquete --nombre demo --version 0.1.0

2. Construir el contenedor publicable ``.co``:

   .. code-block:: bash

      cobra paquete construir mi_paquete dist/demo.co

3. Validar que el contenedor sea legible, tenga manifiesto y conserve los
   checksums esperados:

   .. code-block:: bash

      cobra paquete validar dist/demo.co

4. Verificar explícitamente la integridad antes de publicar o instalar. El
   comando devuelve código ``0`` si los checksums son válidos y ``1`` si falla:

   .. code-block:: bash

      cobra paquete verificar dist/demo.co

5. Inspeccionar metadatos y archivos incluidos antes de publicar o instalar:

   .. code-block:: bash

      cobra paquete inspeccionar dist/demo.co

6. Extraer el contenido en una carpeta local cuando necesites auditarlo o
   reutilizarlo:

   .. code-block:: bash

      cobra paquete extraer dist/demo.co salida/demo

7. Publicar el paquete en CobraHub:

   .. code-block:: bash

      cobra hub publicar dist/demo.co

8. Buscar paquetes disponibles:

   .. code-block:: bash

      cobra hub buscar demo

9. Instalar un paquete desde CobraHub:

   .. code-block:: bash

      cobra hub instalar demo

Los comandos ``cobra paquete`` gestionan el ciclo de vida local del artefacto.
Los comandos ``cobra hub`` usan ese artefacto para publicar, buscar e instalar
paquetes mediante la API recomendada de CobraHub.

Qué cuenta como paquete ``.co``
------------------------------

La extensión ``.co`` no basta para identificar un paquete publicable. Un archivo
``.co`` solo se considera paquete Cobra cuando cumple estas dos condiciones:

* es un ZIP legible;
* contiene ``cobra.pkg.json`` en la raíz del ZIP.

Por tanto, un archivo ``.co`` de texto puede seguir siendo código fuente Cobra,
y un ZIP con extensión ``.co`` pero sin ``cobra.pkg.json`` no es un paquete Cobra
válido. La detección y validación de este formato vive en
``pcobra.cobra.packaging``.

Compatibilidad legacy de módulos
--------------------------------

Los comandos históricos de módulos se mantienen para no romper scripts ni flujos
existentes que publican o buscan archivos sueltos:

.. code-block:: bash

   cobra modulos publicar ruta/al/modulo.co
   cobra modulos buscar nombre.co

Este flujo legacy usa el subcomando ``modulos`` y la configuración histórica de
CobraHub, incluida la variable de entorno ``COBRAHUB_URL`` cuando aplique. Para
código nuevo se recomienda usar el flujo de paquetes con ``cobra paquete`` y
``cobra hub``.

Diálogo asistido desde la terminal
---------------------------------

Cuando la CLI requiere más contexto (por ejemplo, credenciales, nombre del
paquete o etiquetas) utiliza las utilidades de ``standard_library.interfaz``
para guiar el proceso. En pantalla verás algo similar a lo siguiente:

.. code-block:: text

   ¿Nombre para publicar en CobraHub? [demo]:
   ¿Elige la visibilidad? (privado/público) [público]: público
   ¿Cuántas etiquetas vas a registrar? 3

Los campos se validan automáticamente y se muestran las opciones disponibles en
colores, lo que facilita publicar en CobraHub desde entornos como Codespaces o
Replit sin necesidad de interfaces gráficas adicionales.

Relación con Lexer y Parser
---------------------------

Lexer y Parser no se modifican para soportar paquetes ``.co`` porque el
empaquetado no forma parte de la sintaxis del lenguaje. La construcción,
validación, inspección, extracción, publicación e instalación de paquetes viven
en ``pcobra.cobra.packaging`` y tratan los archivos fuente como contenido del ZIP
hasta que el usuario decida ejecutarlos con los comandos habituales.
