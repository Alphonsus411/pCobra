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

   Puedes añadir tus propias capturas de pantalla en ``frontend/docs/galeria``.

Puedes probarlos en línea con este badge de Binder:

.. raw:: html

   <a href="https://mybinder.org/v2/gh/tuusuario/pCobra/HEAD?filepath=notebooks/ejemplo_basico.ipynb"><img src="https://mybinder.org/badge_logo.svg" alt="Binder"></a>
