Uso del kernel Jupyter
======================

Para ejecutar código Cobra en Jupyter Notebook primero instala el kernel:

.. code-block:: bash

   python -m cobra.jupyter_kernel install

Una vez instalado puedes lanzar el cuaderno con:

.. code-block:: bash

   cobra jupyter

También puedes abrir un cuaderno concreto con:

.. code-block:: bash

   cobra jupyter --notebook ruta/al/cuaderno.ipynb

Dispones de varios cuadernos de ejemplo en la carpeta ``notebooks``:

* `Ejemplo básico <../../notebooks/ejemplo_basico.ipynb>`_
* `Benchmarks <../../notebooks/benchmarks_resultados.ipynb>`_
* `Casos reales: Bioinformática <../../notebooks/casos_reales/bioinformatica.ipynb>`_
* `Casos reales: IA <../../notebooks/casos_reales/inteligencia_artificial.ipynb>`_
* `Casos reales: Análisis de datos <../../notebooks/casos_reales/analisis_datos.ipynb>`_

.. note::

   Puedes añadir tus propias capturas de pantalla en ``docs/frontend/galeria``.

Puedes probarlos en línea con este badge de Binder:

.. raw:: html

    <a href="https://mybinder.org/v2/gh/tuusuario/pCobra/HEAD?filepath=notebooks/ejemplo_basico.ipynb"><img src="https://mybinder.org/badge_logo.svg" alt="Binder"></a>

Modo Python
-----------

Si estableces la variable de entorno ``COBRA_JUPYTER_PYTHON`` el kernel transpilará
las celdas a Python mediante ``cobra.transpilers.transpiler.to_python`` y ejecutará
el resultado dentro de una *sandbox* con límites de tiempo y memoria. La salida
estándar y los errores se mostrarán en la celda correspondiente.

.. warning::

   Ejecutar código Python puede ser inseguro. El kernel mostrará una advertencia
   explícita cuando este modo esté activo.

Para activarlo:

.. code-block:: bash

   export COBRA_JUPYTER_PYTHON=1
   cobra jupyter

Este modo es útil para depurar la traducción a Python o comparar el comportamiento
del intérprete con el backend de Python, pero debe usarse con precaución.
