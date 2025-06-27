Lockfile ``cobra.lock``
======================

El archivo ``cobra.lock`` mantiene un listado de los módulos instalados y sus versiones.
Su contenido es un documento YAML con la clave ``modules`` donde cada entrada
indica el nombre del módulo y su versión semver.

Ejemplo::

   modules:
     util.co: "1.2.0"
     red.co: "0.5.1"

Cuando se instala o actualiza un módulo mediante la CLI, se valida que la
versión declarada sea correcta y se actualiza este archivo.

Para listar los módulos instalados ejecuta::

   cobra modulos listar

Para instalar un módulo desde un archivo::

   cobra modulos instalar ruta/al/modulo.co
