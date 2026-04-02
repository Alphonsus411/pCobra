CLI de Cobra
===========

La herramienta ``cobra`` se maneja mediante subcomandos que facilitan
la ejecución y transpilación de programas. A continuación se resumen
las opciones más importantes y un ejemplo de uso para cada una.

Al iniciarse, la CLI muestra una cabecera con el logo de Cobra. Si se
prefiere desactivar los colores puede usarse la opción ``--no-color``.

Modos globales de la CLI (``--modo``)
-------------------------------------

La opción global ``--modo`` controla qué escenarios se habilitan en la sesión:

- ``cobra``: solo ejecución/interpretación.
- ``transpilar``: solo generación de código.
- ``mixto``: ejecución + generación de código.

Ejemplos:

.. code-block:: bash

   cobra --modo cobra ejecutar programa.co
   cobra --modo transpilar compilar programa.co --tipo python

Subcomando ``compilar``
----------------------
Transpila un archivo Cobra a otro lenguaje.

Opciones principales:

- ``archivo``: ruta del script ``.co``.
- ``--tipo``: lenguaje de salida derivado de la política canónica de targets.
- ``--backend``: alias de ``--tipo`` útil para integraciones automatizadas.
  Admite los mismos lenguajes disponibles.
- ``--tipos``: lista de lenguajes separados por comas para transpilación paralela.

Ejemplo:

.. code-block:: bash

   cobra compilar hola.co --tipo python

Otro ejemplo generando varios lenguajes a la vez:

.. code-block:: bash

   cobra compilar hola.co --tipos=python,javascript,cpp

Política de targets oficial
---------------------------

La lista de nombres canónicos disponibles para ``cobra compilar`` y sus tiers se incluye automáticamente desde la política canónica:

.. include:: ../_generated/target_policy_summary.rst

Lista oficial por tiers usada por la ayuda de CLI:

- **Tier 1**: ``python``, ``rust``, ``javascript``, ``wasm``.
- **Tier 2**: ``go``, ``cpp``, ``java``, ``asm``.

La política pública separa de forma estricta **salida oficial** y **runtime
oficial**. Generar código para ``go``, ``java``, ``wasm`` o ``asm`` no implica
que esos targets tengan ejecución real oficial en la CLI ni soporte oficial de
librerías equivalente a ``python``, ``rust``, ``javascript`` o ``cpp``.

Resumen operativo de runtime en la CLI pública:

- **Runtime oficial verificable**: ``python``, ``rust``, ``javascript`` y ``cpp``.
- **Runtime best-effort no público**: ``go`` y ``java``.
- **Solo transpilación (sin runtime oficial CLI)**: ``wasm`` y ``asm``.

SLA de soporte documental/operativo:

- **Tier 1**: triage inicial de regresiones en <= 2 días hábiles.
- **Tier 2**: triage inicial de regresiones en <= 5 días hábiles.

Para cambios de clasificación (promoción/degradación) se exige RFC + plan de migración.

Migración desde targets retirados
---------------------------------

Si tu flujo histórico dependía de targets eliminados, migra a un target oficial según tu necesidad (runtime oficial, best-effort o solo transpilación) y revisa la guía de transición:

- ``docs/migracion_targets_retirados.md``
- ``docs/historico/migracion_targets_retirados_archivo.md`` (archivo histórico, fuera del flujo activo)

Ejemplos de ``cobra compilar`` para cada backend oficial (generado):

.. include:: ../_generated/cli_backend_examples.rst

Subcomando ``ejecutar``
----------------------
Ejecuta directamente un script Cobra.

Opciones principales:

- ``archivo``: ruta del código ``.co``.
- ``--formatear``: aplica ``black`` antes de procesar el archivo.
- ``--depurar``: muestra información de depuración.
- ``--no-seguro``: desactiva el :doc:`modo seguro <modo_seguro>`.

Ejemplo:

.. code-block:: bash

   cobra ejecutar programa.co --no-seguro --depurar

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
Abre el intérprete interactivo. Es el modo por defecto si no se
especifica un subcomando.

Ejemplo:

.. code-block:: bash

   cobra

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
``python``, ``javascript``, ``cpp`` y ``rust``. Los demás targets oficiales
(``wasm``, ``go``, ``java``, ``asm``) siguen siendo destinos de transpilación y
no deben leerse como equivalentes de ejecución real.

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
solo cubre ``python``, ``javascript``, ``cpp`` y ``rust``.

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
