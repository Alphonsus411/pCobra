CobraHub
========

CobraHub es el punto de publicación, búsqueda e instalación de artefactos Cobra.
El flujo recomendado trabaja con paquetes ``.co`` construidos por la capa de
empaquetado ``pcobra.cobra.packaging``. Para el formato completo de paquetes y
las notas de diseño consulta :doc:`paquetes` y el documento
``../cobrahub_paquetes.md``. Ese documento también recoge el contrato HTTP
mínimo provisional para ``POST /paquetes``, ``GET /paquetes?q=consulta`` y
``GET /paquetes/{nombre}``, compatible con una futura infraestructura tipo PyPI.


Contrato ``PackageRepository``
-----------------------------

La CLI de CobraHub no acopla la publicación, búsqueda, descarga ni lectura de
metadatos a una implementación concreta. Esas operaciones se expresan mediante
el contrato ``PackageRepository``:

* ``publish(package_path, metadata, checksum)``: publica un paquete ``.co``
  local ya validado, enviando los metadatos normalizados y el checksum esperado
  del artefacto.
* ``search(query)``: busca paquetes a partir de una consulta textual y devuelve
  resultados normalizados.
* ``download(name, version=None)``: descarga un paquete por nombre; ``version``
  es opcional y, si se omite, el repositorio puede resolver la versión por
  defecto o más reciente según su política.
* ``read_metadata(package_path)``: lee metadatos de un paquete local tras
  comprobar que el archivo es un paquete Cobra válido.

La implementación HTTP actual usa endpoints provisionales:

* ``POST /paquetes`` para publicar paquetes.
* ``GET /paquetes?q=...`` para buscar paquetes.
* ``GET /paquetes/{nombre}`` para descargar paquetes, con ``version`` como
  parámetro opcional cuando se necesita una versión concreta.

``read_metadata(package_path)`` no usa la red: opera sobre el archivo local y
reutiliza la validación del paquete.

Por ahora quedan fuera de alcance la resolución transitiva de dependencias, la
autenticación compleja, las firmas criptográficas, un índice global completo, el
yanking o deprecación de versiones y los mirrors. Mantener este contrato separado
permite evolucionar CobraHub hacia un repositorio tipo PyPI sin tocar Lexer ni
Parser, porque el empaquetado y el transporte siguen viviendo en capas externas
a la sintaxis del lenguaje.

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

10. Revisar, limpiar o validar la caché local de paquetes descargados o
    publicados:

   .. code-block:: bash

      cobra hub cache listar
      cobra hub cache limpiar
      cobra hub cache validar

Los comandos ``cobra paquete crear|construir|validar|inspeccionar|extraer``
gestionan el ciclo de vida local moderno del artefacto. ``cobra paquete
instalar`` se conserva como alias legacy de extracción/instalación local. Los
comandos ``cobra hub publicar|buscar|instalar`` usan ese artefacto para publicar,
buscar e instalar paquetes mediante la API recomendada de CobraHub. No se
recomienda enviar paquetes ``.co`` con ``cobra.pkg.json`` al flujo
``cobra paquete`` → ``cobra mod publish``; ``cobra modulos publicar|buscar`` se
mantiene solo como compatibilidad histórica de módulos sueltos.


Caché local de CobraHub
-----------------------

CobraHub mantiene una caché local de paquetes ``.co`` para reutilizar artefactos
descargados o publicados sin contactar de nuevo con el servicio remoto. Por
defecto se ubica en ``~/.cobra/hub/cache`` y puede redirigirse con la variable
de entorno ``COBRAHUB_CACHE_DIR``.

Las operaciones disponibles son locales y no rompen los comandos existentes de
publicación, búsqueda o instalación:

.. code-block:: bash

   cobra hub cache listar
   cobra hub cache limpiar
   cobra hub cache limpiar demo
   cobra hub cache validar

``listar`` muestra los archivos ``.co`` cacheados. ``limpiar`` sin argumentos
elimina todos los paquetes cacheados; con un nombre elimina ``<nombre>.co`` y
sus variantes versionadas ``<nombre>-<version>.co``. ``validar`` recorre cada
``.co`` de la caché y aplica las mismas comprobaciones estructurales y de
integridad usadas para paquetes Cobra: primero ``es_paquete_cobra()`` y después
``validar_paquete()``. El comando devuelve código ``0`` si todos los paquetes
son válidos y ``1`` si al menos una entrada está corrupta o no es un paquete
Cobra.

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
existentes que publican o buscan archivos sueltos. Estos comandos legacy se
conservan por compatibilidad y no deben eliminarse sin una política de
deprecación explícita.

.. list-table:: Alias legacy y comandos recomendados
   :header-rows: 1
   :widths: 24 24 16 36

   * - comando legacy
     - comando recomendado
     - estado
     - notas de compatibilidad
   * - ``cobra modulos publicar``
     - ``cobra hub publicar`` para paquetes ``.co`` con manifiesto
     - Compatibilidad
     - ``modulos`` publica módulos sueltos mediante el flujo histórico; no debe usarse como destino recomendado de paquetes ``.co`` con ``cobra.pkg.json``.
   * - ``cobra modulos buscar``
     - ``cobra hub buscar`` o ``cobra hub instalar``
     - Compatibilidad
     - Para código nuevo, busca paquetes con ``hub buscar`` e instálalos con ``hub instalar``; ``modulos buscar`` queda para módulos sueltos históricos.
   * - ``cobra paquete instalar``
     - ``cobra paquete extraer``
     - Alias legacy
     - Alias de extracción/instalación local; útil para scripts antiguos que esperan un destino local.
   * - ``cobra paquete crear <fuente> <salida>``
     - ``cobra paquete crear <fuente>`` + ``cobra paquete construir <fuente> <salida>``
     - Alias legacy
     - Mantiene el flujo antiguo de creación + construcción en una sola invocación.

Este flujo legacy usa el subcomando ``modulos`` y la configuración histórica de
CobraHub, incluida la variable de entorno ``COBRAHUB_URL`` cuando aplique. Para
código nuevo se recomienda usar el flujo local de paquetes con ``cobra paquete
crear|construir|validar|inspeccionar|extraer`` y el flujo remoto con ``cobra hub
publicar|buscar|instalar``.

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
empaquetado no forma parte de la sintaxis del lenguaje: un paquete ``.co`` se
detecta como un ZIP legible con ``cobra.pkg.json`` en la raíz, no como sintaxis
Cobra. La construcción,
validación, inspección, extracción, publicación e instalación de paquetes viven
en ``pcobra.cobra.packaging`` y tratan los archivos fuente como contenido del ZIP
hasta que el usuario decida ejecutarlos con los comandos habituales.
