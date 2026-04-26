CLI de Cobra
===========

La CLI pública de Cobra se enfoca en un flujo estable para usuario final con
cinco comandos:

- ``cobra run archivo.cobra``
- ``cobra build archivo.cobra``
- ``cobra test archivo.cobra``
- ``cobra mod ...``
- ``cobra repl``

Estos comandos exponen la UX oficial. La selección de backend, adaptación de
runtime y detalles de transpilación quedan encapsulados dentro de la
arquitectura interna.

Flujo público recomendado
-------------------------

Ejecutar un programa:

.. code-block:: bash

   cobra run archivo.cobra

Construir artefactos:

.. code-block:: bash

   cobra build archivo.cobra

Ejecutar pruebas del proyecto o de un archivo:

.. code-block:: bash

   cobra test archivo.cobra

Gestionar módulos:

.. code-block:: bash

   cobra mod list
   cobra mod install paquete.cobra
   cobra mod remove paquete.cobra

Architecture overview (resumen corto)
--------------------------------------

Diagrama principal:

.. code-block:: text

   Frontend Cobra
        ↓
   BackendPipeline
        ↓
   Bindings (python/js/rust)

- ``Frontend Cobra`` analiza el código y produce AST.
- ``BackendPipeline`` resuelve backend y normaliza compilación interna.
- ``Bindings`` conecta con runtime oficial en Python, JavaScript y Rust.

Imports y biblioteca estándar (resolución determinista)
-------------------------------------------------------

La resolución de imports en la ruta pública es determinista y prioriza el
espacio estándar antes de rutas híbridas ambiguas. Para documentación y ejemplos
se usan los módulos canónicos:

- ``cobra.core``
- ``cobra.datos``
- ``cobra.web``
- ``cobra.system``

Histórico y compatibilidad legacy
---------------------------------

.. warning::
   Las opciones y comandos legacy que aparecen en esta sección se conservan
   **solo para compatibilidad temporal**. No forman parte de la UX pública
   recomendada. Para nuevos flujos usa únicamente ``run/build/test/mod``.

La política oficial de targets sigue limitándose a ``python``, ``javascript`` y
``rust``. Targets legacy e indicadores internos deben usarse únicamente en
migraciones controladas.

Subcomando ``validar-sintaxis``
-------------------------------
Valida sintaxis de Python/Cobra y/o de backends transpilados según el perfil.

Opciones principales:

- ``--perfil``: selecciona alcance de validación.

  - ``solo-cobra``: valida compilación Python de ``src/tests`` + parse de fixtures Cobra.
  - ``transpiladores``: valida solo sintaxis de código generado en backends oficiales.
  - ``completo``: ejecuta ambos bloques.

- ``--solo-cobra``: alias **deprecado** equivalente a ``--perfil=solo-cobra``.
- ``--targets``: CSV de targets al usar perfil con transpiladores.
- ``--strict``: convierte ``skipped`` en error.

Ejemplos por perfil:

.. code-block:: bash

   # Rápido (Python + parse Cobra)
   cobra validar-sintaxis --perfil solo-cobra

   # Compatibilidad (alias deprecado)
   cobra validar-sintaxis --solo-cobra

   # Solo backends para pipeline de transpiladores
   cobra validar-sintaxis --perfil transpiladores --targets=python,javascript,rust

   # Flujo completo para CI estricta
   cobra validar-sintaxis --perfil completo --strict --report-json reporte_sintaxis.json

Subcomando ``interactive``
-------------------------
El subcomando ``interactive`` se mantiene solo como alias legacy de
migración. El flujo interactivo oficial en la CLI pública es ``cobra repl``.

Para el contrato de paridad entre ejecución por archivo y REPL (misma sintaxis,
misma gramática y misma ruta canónica de pipeline), consulta:
``docs/architecture/repl-script-parity-contract.md``.

Ejemplo:

.. code-block:: bash

   cobra repl

Subcomando ``menu``
-------------------
Muestra un asistente en consola para guiar la transpilación entre lenguajes.

Ejemplo:

.. code-block:: text

   $ cobra menu
   Lenguajes destino disponibles: (ver resumen generado en esta página)...
   Lenguajes de origen disponibles: (ver resumen generado en esta página)...
   ¿Desea transpilar? (s/n): s
   ¿Transpilar desde Cobra a otro lenguaje? (s/n): s
   Ruta al archivo Cobra: hola.co
   Lenguaje destino: python

Subcomandos legacy/internal
----------------------------

.. warning::
   Los comandos históricos y aliases de compatibilidad (v1/legacy) no forman
   parte de la interfaz pública recomendada. Su documentación se mantiene en
   ``docs/anexos_legacy_internal/`` y no debe usarse como onboarding.

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
Analiza un archivo y sugiere mejoras utilizando ``agix``. El proyecto requiere
``agix`` en su versión ``>=1.4,<2``, que permite ponderar la precisión e
interpretabilidad de las recomendaciones y mapea internamente módulos bajo
``src.agix`` para mantener compatibilidad. La selección de la mejor
recomendación se realiza con la clase ``Reasoner`` de
``agix.reasoning.basic``.

Se pueden ajustar los resultados mediante:

* ``--peso-precision``: factor de ponderación para la precisión (valor
  positivo).
* ``--peso-interpretabilidad``: factor para la interpretabilidad (valor
  positivo).

Además, es posible modular las recomendaciones emocionalmente con valores en
el rango ``-1`` a ``1``:

* ``--placer``: regula el grado de placer percibido.
* ``--activacion``: ajusta el nivel de activación.
* ``--dominancia``: indica el control o dominancia.

Ejemplo básico con ponderación:

.. code-block:: bash

   cobra agix ejemplo.co --peso-precision 0.8 --peso-interpretabilidad 1.2

Ejemplo con modulación emocional:

.. code-block:: bash

   cobra agix ejemplo.co --placer 0.5 --activacion 0.2 --dominancia -0.1

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

Al ejecutarlo se abre una ventana con un editor de texto y botones para
ejecutar o limpiar el código. Es una forma rápida de probar programas sin usar
la terminal.

Cuando uses ``--sandbox-docker``, la CLI solo ofrece runtimes Docker oficiales:
``python``, ``javascript`` y ``rust``.

Subcomando ``plugins``
---------------------
Muestra los plugins instalados y sus versiones registrados mediante ``entry_points``.

Acciones disponibles:

- ``buscar <texto>`` filtra por nombre o descripción.

Ejemplo:

.. code-block:: bash

   cobra plugins

Otro ejemplo filtrando la lista:

.. code-block:: bash

   cobra plugins buscar saludo

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
Compara el rendimiento de los backends con runner configurado en la suite y
muestra un resumen en formato JSON. Opcionalmente puede guardarse en un
archivo mediante ``--output``. Esto no implica paridad de ejecución para
todos los targets oficiales de transpilación: la política pública de runtime
solo cubre ``python``, ``javascript`` y ``rust``.

Ejemplo:

.. code-block:: bash

   cobra benchmarks --output resultados.json

Subcomando ``bench``
--------------------
Ejecuta la suite de benchmarks integrada. Con ``--profile`` guarda los
resultados en ``bench_results.json`` y genera un archivo ``bench_results.prof``
para análisis detallado.

Ejemplo:

.. code-block:: bash

   cobra bench --profile

Subcomando ``benchtranspilers``
------------------------------
Mide la velocidad de los distintos transpiladores generando programas de
tamaño pequeño, mediano y grande. Los tiempos se muestran en formato
JSON y opcionalmente pueden guardarse con ``--output``. Con ``--profile``
se ejecuta ``cProfile`` durante la generación y se guarda un archivo
``bench_transpilers.prof`` para su análisis. La carpeta de programas se
resuelve de forma automática desde la raíz del proyecto (directorio que
contiene ``pyproject.toml`` y ``scripts/``) y usa
``scripts/benchmarks/programs``. Si no existe ``scripts/benchmarks``,
el comando falla de forma temprana con un mensaje claro.

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
