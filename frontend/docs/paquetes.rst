Paquetes Cobra
==============

Un paquete Cobra es un archivo comprimido que agrupa varios módulos ``.co`` y un
manifest llamado ``cobra.pkg``. Este manifest utiliza sintaxis TOML para
especificar los metadatos del paquete.

Estructura de ``cobra.pkg``
---------------------------

.. code-block:: toml

   [paquete]
   nombre = "demo"
   version = "0.1"

   [modulos]
   archivos = ["main.co", "util.co"]

Creación e instalación
----------------------

Para crear un paquete desde una carpeta que contenga archivos ``.co`` ejecuta:

.. code-block:: bash

   cobra paquete crear src demo.cobra --nombre=demo --version=0.1

El archivo resultante ``demo.cobra`` puede instalarse en el directorio de
módulos predeterminado con:

.. code-block:: bash

   cobra paquete instalar demo.cobra

Los módulos incluidos estarán disponibles para ser importados con ``import``.
