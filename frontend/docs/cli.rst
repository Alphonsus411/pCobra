CLI de Cobra
===========

La herramienta ``cobra`` se maneja mediante subcomandos que facilitan
la ejecución y transpilación de programas. A continuación se resumen
las opciones más importantes y un ejemplo de uso para cada una.

Subcomando ``compilar``
----------------------
Transpila un archivo Cobra a otro lenguaje.

Opciones principales:

- ``archivo``: ruta del script ``.co``.
- ``--tipo``: lenguaje de salida (``python``, ``js``, ``asm``, ``rust``,
  ``cpp``, ``go``, ``ruby``, ``r``, ``julia``, ``java``, ``cobol``,
  ``fortran``, ``pascal``, ``php``, ``matlab``, ``latex``, ``wasm``).
- ``--tipos``: lista de lenguajes separados por comas para transpilación paralela.

Ejemplo:

.. code-block:: bash

   cobra compilar hola.co --tipo python

Otro ejemplo generando varios lenguajes a la vez:

.. code-block:: bash

   cobra compilar hola.co --tipos=python,js,c

Subcomando ``ejecutar``
----------------------
Ejecuta directamente un script Cobra.

Opciones principales:

- ``archivo``: ruta del código ``.co``.
- ``--formatear``: aplica ``black`` antes de procesar el archivo.
- ``--depurar``: muestra información de depuración.
- ``--seguro``: activa el :doc:`modo seguro <modo_seguro>`.

Ejemplo:

.. code-block:: bash

   cobra ejecutar programa.co --seguro --depurar

Subcomando ``interactive``
-------------------------
Abre el intérprete interactivo. Es el modo por defecto si no se
especifica un subcomando.

Ejemplo:

.. code-block:: bash

   cobra

Subcomando ``modulos``
---------------------
Gestiona módulos instalados.

Acciones disponibles:

- ``listar`` muestra los módulos instalados.

- ``instalar <ruta>`` copia un archivo ``.co`` al directorio de módulos.
- ``remover <nombre>`` elimina un módulo instalado.

Al instalar un módulo se valida la versión indicada en ``cobra.mod`` y se
actualiza ``cobra.lock``. Este fichero almacena el nombre de cada módulo
y su versión semver bajo la clave ``modules``.

El formato del archivo es:

.. code-block:: yaml

   modules:
     modulo.co: "1.0.0"

Ejemplo:

.. code-block:: bash

   cobra modulos instalar extra/modulo.co

Subcomando ``dependencias``
--------------------------
Permite listar o instalar las dependencias definidas en
``requirements.txt`` y en ``pyproject.toml``.

Ejemplo:

.. code-block:: bash

   cobra dependencias instalar

Subcomando ``docs``
-------------------
Genera la documentación HTML del proyecto.

Ejemplo:

.. code-block:: bash

   cobra docs

Subcomando ``empaquetar``
------------------------
Crea un ejecutable independiente usando ``PyInstaller``.

Ejemplo:

.. code-block:: bash

   cobra empaquetar --output dist

Subcomando ``paquete``
----------------------
Permite crear e instalar paquetes Cobra.

Ejemplo:

.. code-block:: bash

   cobra paquete crear src demo.cobra
   cobra paquete instalar demo.cobra

Subcomando ``crear``
-------------------
Genera archivos o proyectos básicos.

Ejemplo:

.. code-block:: bash

   cobra crear proyecto mi_app

Subcomando ``agix``
------------------
Analiza un archivo y sugiere mejoras utilizando ``agix``.

Ejemplo:

.. code-block:: bash

   cobra agix ejemplo.co

Subcomando ``jupyter``
---------------------
Instala el kernel Cobra y abre ``Jupyter Notebook``.

Opcionalmente se puede indicar un cuaderno concreto con ``--notebook``.

Ejemplo:

.. code-block:: bash

   cobra jupyter --notebook ruta/al/cuaderno.ipynb

Subcomando ``gui``
-----------------
Inicia la interfaz gráfica basada en ``Flet``.

Ejemplo:

.. code-block:: bash

   cobra gui

Subcomando ``plugins``
---------------------
Muestra los plugins instalados y sus versiones registrados mediante ``entry_points``.

Ejemplo:

.. code-block:: bash

   cobra plugins

Subcomando ``contenedor``
------------------------
Construye la imagen Docker del proyecto.

Ejemplo:

.. code-block:: bash

   cobra contenedor --tag cobra

Subcomando ``init``
------------------
Inicializa un proyecto básico.

Ejemplo:

.. code-block:: bash

   cobra init mi_app

Subcomando ``benchmarks``
-----------------------
Compara el rendimiento de los distintos backends y muestra un resumen
en formato JSON. Opcionalmente puede guardarse en un archivo mediante
``--output``.

Ejemplo:

.. code-block:: bash

   cobra benchmarks --output resultados.json

Subcomando ``benchtranspilers``
------------------------------
Mide la velocidad de los distintos transpiladores generando programas de
tamaño pequeño, mediano y grande. Los tiempos se muestran en formato
JSON y opcionalmente pueden guardarse con ``--output``.

Ejemplo:

.. code-block:: bash

   cobra benchtranspilers --output transpilers.json

Subcomando ``profile``
----------------------
Ejecuta un archivo Cobra bajo ``cProfile``. Muestra en pantalla las
estadísticas básicas o las guarda en un archivo ``.prof`` mediante
``--output``.

Ejemplo:

.. code-block:: bash

   cobra profile programa.co --output perfil.prof

Si se omite ``--output`` las estadísticas se muestran por consola:

.. code-block:: bash

   cobra profile programa.co
