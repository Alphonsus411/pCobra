Paquetes Cobra
==============

Un paquete Cobra publicable usa la extensión ``.co`` y se distribuye como un
contenedor ZIP. El contenedor conserva la estructura de carpetas del proyecto,
incluye un manifiesto ``cobra.pkg.json`` y registra checksums SHA-256 para los
archivos empaquetados.

Este formato pertenece a la capa de herramientas de empaquetado y CobraHub: no
modifica la sintaxis del lenguaje ni requiere cambios en el Lexer o el Parser.
Los archivos fuente Cobra pueden seguir usando ``.cobra`` o ``.co``; cuando
``.co`` se usa como paquete publicable, la CLI lo trata como un ZIP con
metadatos.

Fuente de verdad pública
------------------------

El módulo ``pcobra.cobra.packaging`` es la fuente de verdad del empaquetado
``.co``. Su API pública explícita está formada por ``crear_paquete``,
``validar_paquete``, ``construir_paquete``, ``extraer_paquete``,
``inspeccionar_paquete``, ``verificar_integridad`` y ``es_paquete_cobra``.
La CLI, IDLE y CobraHub deben delegar en estas funciones para crear, detectar,
validar, inspeccionar, verificar o extraer paquetes; no deben reimplementar la
lógica de manifiestos, ZIPs ni checksums.

Contenido incluido
------------------

La construcción del paquete no aplica una allowlist por extensión. En concreto,
``cobra paquete construir`` recorre la carpeta fuente, preserva rutas relativas
y añade todos los archivos regulares encontrados, con estas reglas:

* el manifiesto ``cobra.pkg.json`` se regenera en la raíz del ZIP y no se copia
  como archivo de contenido normal;
* se omiten las carpetas de trabajo ``.git``, ``__pycache__`` y
  ``.pytest_cache``;
* se incluyen archivos fuente ``.cobra``;
* se incluyen archivos ``.co`` de texto usados como fuente Cobra;
* se incluye documentación como ``README.md``, archivos ``.md`` bajo
  ``docs/`` y archivos ``.txt``;
* se incluye ``Dockerfile`` cuando existe en el proyecto;
* se incluyen recursos arbitrarios, también binarios o con extensiones no
  conocidas, bajo carpetas como ``resources/``, ``assets/`` o ``docs/``;
* se conservan las carpetas anidadas porque cada entrada se guarda con su ruta
  relativa dentro del proyecto.

Por tanto, el límite de seguridad del formato no es la extensión del archivo,
sino el manifiesto y la integridad: cada archivo incluido debe estar declarado
en ``files`` y tener su checksum correspondiente en ``checksums``.

Manifiesto ``cobra.pkg.json``
-----------------------------

El manifiesto ``cobra.pkg.json`` describe los metadatos del paquete y la lista de
archivos incluidos. Cada entrada se acompaña de su checksum SHA-256 para que las
operaciones de validación e inspección puedan detectar cambios o corrupción del
contenedor.

Ejemplo simplificado:

.. code-block:: json

   {
     "format": "cobra-package-v1",
     "name": "demo",
     "version": "0.1.0",
     "files": [
       "src/main.co",
       "README.md",
       "Dockerfile",
       "assets/imagenes/logo.bin",
       "resources/i18n/es.dat"
     ],
     "checksums": {
       "src/main.co": "...",
       "README.md": "...",
       "Dockerfile": "...",
       "assets/imagenes/logo.bin": "...",
       "resources/i18n/es.dat": "..."
     }
   }

Flujo recomendado
-----------------

Crear la estructura inicial del paquete:

.. code-block:: bash

   cobra paquete crear mi_paquete --nombre demo --version 0.1.0

Construir el contenedor publicable ``.co``:

.. code-block:: bash

   cobra paquete construir mi_paquete dist/demo.co

Validar estructura y manifiesto del contenedor:

.. code-block:: bash

   cobra paquete validar dist/demo.co

Verificación de integridad
--------------------------

Antes de publicar o instalar un paquete, usa ``verificar`` para expresar de
forma explícita la comprobación de integridad SHA-256 de los archivos declarados
en ``cobra.pkg.json``. El comando ``integridad`` se mantiene como alias legacy
para scripts existentes y es equivalente a ``verificar``.

.. code-block:: bash

   cobra paquete verificar dist/demo.co
   cobra paquete integridad dist/demo.co

Inspeccionar los metadatos y archivos incluidos:

.. code-block:: bash

   cobra paquete inspeccionar dist/demo.co

Extraer el paquete en una carpeta local:

.. code-block:: bash

   cobra paquete extraer dist/demo.co ./vendor/demo

Compatibilidad con comandos legacy
----------------------------------

Los comandos legacy se mantienen por compatibilidad con scripts existentes y no
deben eliminarse sin una política de deprecación explícita. Para paquetes
nuevos, el formato recomendado es el contenedor ``.co`` con manifiesto
``cobra.pkg.json`` y checksums SHA-256.

.. list-table:: Alias legacy y comandos recomendados
   :header-rows: 1
   :widths: 24 24 16 36

   * - comando legacy
     - comando recomendado
     - estado
     - notas de compatibilidad
   * - ``cobra modulos publicar``
     - ``cobra hub publicar``
     - Compatibilidad
     - ``modulos`` conserva el flujo histórico de módulos sueltos; ``hub`` publica paquetes ``.co`` validados.
   * - ``cobra modulos buscar``
     - ``cobra hub buscar`` o ``cobra hub instalar``
     - Compatibilidad
     - Usa ``hub buscar`` para descubrimiento y ``hub instalar`` para descarga e instalación de paquetes CobraHub.
   * - ``cobra paquete instalar``
     - ``cobra paquete extraer``
     - Alias legacy
     - Alias de extracción/instalación local hacia el directorio indicado o ``~/.cobra/packages`` por defecto.
   * - ``cobra paquete crear <fuente> <salida>``
     - ``cobra paquete crear <fuente>`` + ``cobra paquete construir <fuente> <salida>``
     - Alias legacy
     - La forma posicional crea el manifiesto y construye el artefacto en un solo paso para compatibilidad.

Véase también
-------------

* :doc:`../cobrahub_paquetes`
* La sección "Paquetes ``.co`` y CobraHub" del ``README.md`` del repositorio.
