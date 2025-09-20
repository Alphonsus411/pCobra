Manual de Cobra
===============

Versión 10.0.9

Este documento resume la sintaxis y los elementos fundamentales del lenguaje
Cobra. Incluye ejemplos de uso idiomático, limitaciones de los backends y
recomendaciones de estilo.

.. contents:: Índice
   :depth: 2

Preparación del entorno
----------------------

1. Clona el repositorio y entra en ``pCobra``.
2. Crea y activa un entorno virtual de **Python 3.9 o superior**.
3. Instala las dependencias con ``pip install -r requirements-dev.txt``.
4. Instala Cobra en modo editable con ``pip install -e .``.

   También puedes ejecutar ``pip install -e .[dev]`` para incluir los extras de
   desarrollo.

Sintaxis básica
---------------

* Declaración de variables con ``var``:

  .. code-block:: cobra

     var mensaje = "Hola"

* Funciones con ``func`` y finalización opcional con ``fin``:

  .. code-block:: cobra

     func sumar(a, b):
         return a + b
     fin

* Condicionales ``si``/``sino`` y bucles ``mientras``/``para``:

  .. code-block:: cobra

     si x > 0:
         imprimir(x)
     sino:
         imprimir(0)

Tipos y estructuras de datos
----------------------------

Cobra soporta números, cadenas, listas, diccionarios y conjuntos. Las clases se
crean con ``clase`` y se instancian como en Python.

.. code-block:: cobra

   clase Persona:
       func __init__(self, nombre):
           self.nombre = nombre
       fin

   var p = Persona("Ada")
   imprimir(p.nombre)

Módulos y paquetes
------------------

Los módulos se importan con ``import``. Para agrupar varios módulos puede
crearse un archivo ``cobra.pkg`` y usar ``cobra paquete crear`` para
empaquetarlos.

Macros y concurrencia
---------------------

La directiva ``macro`` permite insertar código reutilizable. Para lanzar tareas
en paralelo se utiliza ``hilo``.

.. code-block:: cobra

   macro saluda { imprimir("hola") }
   hilo saluda()

Funciones asincrónicas
----------------------

Para definir corrutinas se emplea la palabra clave ``asincronico`` y se espera
su resultado con ``esperar``.

.. code-block:: cobra

   asincronico func saluda():
       imprimir(1)
   fin

   asincronico func principal():
       esperar saluda()
   fin

   esperar principal()

El módulo :mod:`pcobra.corelibs.asincrono` ofrece varios atajos que reproducen
patrones habituales tanto de ``asyncio`` como de las *promises* en JavaScript y
las rutinas concurrentes en Go. ``recolectar`` equivale a
``asyncio.gather``/``Promise.all``, ``primero_exitoso`` se comporta como
``Promise.any`` al devolver el primer resultado sin excepciones y
``iterar_completadas`` se inspira en ``asyncio.as_completed`` para procesar
respuestas a medida que van llegando. ``recolectar_resultados`` devuelve una
estructura similar a ``Promise.allSettled`` con los estados finales (cumplida,
rechazada o cancelada) de cada corrutina, mientras que
``mapear_concurrencia`` implementa un patrón de *worker pool* estilo Go a
través de ``asyncio.Semaphore`` para respetar un ``limite`` máximo de tareas y
decidir, mediante ``return_exceptions``, si los errores cancelan el resto o se
registran junto a sus posiciones originales.

Decoradores
-----------

Se declaran anteponiendo ``@`` al nombre de la función que se desea modificar.

.. code-block:: cobra

   @log
   func hola():
       imprimir("hola")
   fin

Manejo de excepciones
---------------------

Las excepciones pueden atraparse con ``try``/``catch`` o sus alias
``intentar``/``capturar``.

.. code-block:: cobra

   intentar:
       abrir("no_existe.txt")
   capturar e:
       imprimir("Error:" + e)
   fin

Ejemplos adicionales
--------------------

Suma de matrices::

   func sumar_matriz():
       var a11 = 1
       var a12 = 2
       var a21 = 3
       var a22 = 4

       var b11 = 5
       var b12 = 6
       var b21 = 7
       var b22 = 8

       imprimir(a11 + b11)
       imprimir(a12 + b12)
       imprimir(a21 + b21)
       imprimir(a22 + b22)
   fin

   sumar_matriz()

Factorial recursivo::

   func factorial(n):
       si n <= 1:
           retorno 1
       sino:
           retorno n * factorial(n - 1)
       fin
   fin

   imprimir(factorial(5))

Operaciones numéricas con ``corelibs.numero``
--------------------------------------------

La biblioteca estándar también incluye utilidades numéricas inspiradas en
``math`` y ``statistics`` de Python. Permiten normalizar valores, generar
aleatorios reproducibles y analizar datos sin abandonar Cobra.

.. code-block:: python

   import pcobra.corelibs as core

   medidas = [1.2, 1.8, 2.0, 2.5]
   print(core.absoluto(-3))
   print(core.redondear(3.14159, 3))
   print(core.clamp(5, 0, 3))
   print(core.mediana(medidas))
   print(core.desviacion_estandar(medidas, muestral=True))
   print(core.es_finito(42.0))
   print(core.es_infinito(float("inf")))
   print(core.es_nan(float("nan")))
   print(core.copiar_signo(2.0, -0.0))

Las utilidades ``es_finito``, ``es_infinito`` y ``es_nan`` permiten validar los
resultados de cálculos con números de punto flotante antes de continuar con el
flujo del programa. ``copiar_signo`` resulta útil al normalizar magnitudes y
preservar el signo de ceros, infinitos o ``NaN`` para mantener la compatibilidad
con otros entornos IEEE-754.

``signo`` y ``limitar`` completan estas herramientas cuando necesitas clasificar
o acotar valores reales. ``signo`` devuelve ``-1``, ``0`` o ``1`` para enteros y
mantiene ceros con signo o ``NaN`` cuando trabajas con flotantes, mientras que
``limitar`` valida el rango ``[minimo, maximo]`` y también propaga ``NaN`` si
algún extremo no es un número válido.

.. code-block:: python

   import pcobra.corelibs as core
   import standard_library.numero as numero

   print(core.signo(-3))                 # -1: enteros devuelven -1/0/1
   print(numero.signo(-0.0))             # -0.0: conserva ceros con signo
   print(core.limitar(120, 0, 100))      # 100: satura el valor al máximo
   print(numero.limitar(float("nan"), 0.0, 1.0))  # NaN propagado

Para cálculos combinatorios y sumas sensibles a errores de redondeo dispones
de atajos adicionales. ``raiz_entera`` delega en ``math.isqrt`` para obtener la
raíz cuadrada entera de valores gigantes sin perder precisión, ``combinaciones``
y ``permutaciones`` aprovechan ``math.comb``/``math.perm`` para contar sin
repetición incluso con números negativos o muy grandes (propagando las mismas
excepciones), y ``suma_precisa`` invoca ``math.fsum`` para minimizar la pérdida
de significancia en sumas largas.

.. code-block:: python

   import pcobra.corelibs as core
   import standard_library.numero as numero

   print(core.raiz_entera(10**12 + 12345))      # 1000000
   print(core.combinaciones(52, 5))             # 2598960
   print(numero.permutaciones(10, 3))           # 720
   print(numero.suma_precisa([1e16, 1.0, -1e16]))  # 1.0

.. list-table:: Equivalencias con bibliotecas numéricas
   :header-rows: 1
   :widths: 20 25 25 30

   * - Cobra
     - Python ``math``/``statistics``
     - ``numpy``
     - JavaScript ``Math``
   * - ``absoluto(x)``
     - ``math.fabs(x)``
     - ``numpy.abs(x)``
     - ``Math.abs(x)``
   * - ``redondear(x, n)``
     - ``round(x, n)``
     - ``numpy.round(x, n)``
     - ``Math.round(x * 10**n) / 10**n``
   * - ``piso(x)``
     - ``math.floor(x)``
     - ``numpy.floor(x)``
     - ``Math.floor(x)``
   * - ``techo(x)``
     - ``math.ceil(x)``
     - ``numpy.ceil(x)``
     - ``Math.ceil(x)``
   * - ``raiz(x, n)``
     - ``math.pow(x, 1/n)``
     - ``numpy.power(x, 1/n)``
     - ``Math.pow(x, 1/n)``
   * - ``raiz_entera(x)``
     - ``math.isqrt(x)``
     - ``numpy.floor(numpy.sqrt(x))``
     - ``Math.floor(Math.sqrt(x))``
   * - ``potencia(a, b)``
     - ``math.pow(a, b)``
     - ``numpy.power(a, b)``
     - ``Math.pow(a, b)``
   * - ``limitar(x, a, b)`` / ``clamp(x, a, b)``
     - ``min(max(x, a), b)``
     - ``numpy.clip(x, a, b)``
     - ``Math.min(Math.max(x, a), b)``
   * - ``es_finito(x)``
     - ``math.isfinite(x)``
     - ``numpy.isfinite(x)``
     - ``Number.isFinite(x)``
   * - ``es_infinito(x)``
     - ``math.isinf(x)``
     - ``numpy.isinf(x)``
     - ``!Number.isFinite(x) && !Number.isNaN(x)``
   * - ``es_nan(x)``
     - ``math.isnan(x)``
     - ``numpy.isnan(x)``
     - ``Number.isNaN(x)``
   * - ``copiar_signo(a, b)``
     - ``math.copysign(a, b)``
     - ``numpy.copysign(a, b)``
     - ``Math.abs(a) * (Number.isNaN(b) ? 1 : Math.sign(b) || 1)``
   * - ``combinaciones(n, k)``
     - ``math.comb(n, k)``
     - ``numpy.math.comb(n, k)``
     - ``factorial(n) / (factorial(k) * factorial(n - k))``
   * - ``permutaciones(n, k)``
     - ``math.perm(n, k)``
     - ``numpy.math.perm(n, k)``
     - ``factorial(n) / factorial(n - k)``
   * - ``suma_precisa(valores)``
     - ``math.fsum(valores)``
     - ``numpy.sum(valores, dtype=numpy.float64)``
     - ``valores.reduce((total, x) => total + x, 0)``
   * - ``aleatorio(a, b)``
     - ``random.uniform(a, b)``
     - ``numpy.random.uniform(a, b)``
     - ``Math.random() * (b - a) + a``

Los enteros también cuentan con atajos binarios que replican la API moderna de
Python:

.. code-block:: python

   print(core.longitud_bits(255))
   print(core.contar_bits(-3))
   print(core.entero_a_bytes(-1, signed=True))
   print(core.entero_desde_bytes(b"\xff", signed=True))

Las funciones ``longitud_bits`` y ``contar_bits`` recuperan información del
entero sin escribir operadores manuales, mientras que ``entero_a_bytes`` y
``entero_desde_bytes`` facilitan la conversión a representaciones binarias en
los órdenes ``big`` y ``little``.

Las utilidades ``rotar_bits_izquierda`` y ``rotar_bits_derecha`` trasladan la
semántica de ``rotate_left``/``rotate_right`` presente en Go y Rust. Basta
indicar ``ancho_bits`` para emular palabras de tamaño fijo y conservar el signo
mediante representación en complemento a dos.
   * - ``mcd(a, b, ...)``
     - ``math.gcd(a, b, ...)``
     - ``numpy.gcd.reduce([a, b, ...])``
     - «Sin equivalente directo; implementar algoritmo de Euclides»
   * - ``mcm(a, b, ...)``
     - ``math.lcm(a, b, ...)``
     - ``numpy.lcm.reduce([a, b, ...])``
     - «Sin equivalente directo; usar ``mcd`` manualmente»
   * - ``es_cercano(a, b, tol_rel, tol_abs)``
     - ``math.isclose(a, b, rel_tol=tol_rel, abs_tol=tol_abs)``
     - ``numpy.isclose(a, b, rtol=tol_rel, atol=tol_abs)``
     - ``Math.abs(a - b) <= Math.max(tol_abs, tol_rel * Math.max(Math.abs(a), Math.abs(b)))``
   * - ``producto(valores, inicio)``
     - ``math.prod(valores, start=inicio)``
     - ``numpy.prod(valores, initial=inicio)``
     - ``valores.reduce((acc, v) => acc * v, inicio)``
   * - ``entero_a_base(n, base, alfabeto)``
     - ``format(n, 'x')`` / ``numpy.base_repr(n, base)``
     - ``numpy.base_repr(n, base)``
     - ``n.toString(base)``
   * - ``entero_desde_base(txt, base, alfabeto)``
     - ``int(txt, base)``
     - «Sin equivalente directo; combinar ``numpy.array`` y lógica propia»
     - ``parseInt(txt, base)``
   * - ``mediana(datos)``
     - ``statistics.median(datos)``
     - ``numpy.median(datos)``
     - «Sin equivalente directo; ordenar y promediar»
   * - ``moda(datos)``
     - ``statistics.mode(datos)``
     - ``numpy.unique(datos, return_counts=True)``
     - «Sin equivalente directo; contar frecuencias»
   * - ``desviacion_estandar(datos)``
     - ``statistics.pstdev(datos)``
     - ``numpy.std(datos)``
     - «Sin equivalente directo; implementar manualmente»

Las funciones ``entero_a_base`` y ``entero_desde_base`` admiten números con signo
y validan que la base esté en el intervalo ``[2, 36]``. El argumento opcional
``alfabeto`` permite sincronizar el conjunto de dígitos en ambas direcciones.

Manipulación de texto con ``corelibs.texto``
-------------------------------------------

El módulo :mod:`pcobra.corelibs.texto` ofrece utilidades Unicode listas para
usar en Cobra. Entre las más destacadas se encuentran:

* ``quitar_espacios``, ``dividir`` y ``unir`` para limpiar y recomponer
  cadenas, con soporte para separadores personalizados.
* ``quitar_prefijo`` y ``quitar_sufijo`` replican
  ``str.removeprefix``/``str.removesuffix`` de Python, mientras que
  ``prefijo_comun`` y ``sufijo_comun`` añaden equivalentes a
  ``commonPrefixWith``/``commonSuffixWith`` de Kotlin o
  ``String.commonPrefix``/``String.commonSuffix`` de Swift. Ambas admiten
  ignorar mayúsculas y normalizar Unicode antes de comparar.
* ``a_snake`` y ``a_camel`` producen identificadores inspirados en
  extensiones de Kotlin, las rutinas ``lowerCamelCase`` de Swift y
  utilidades de JavaScript como ``lodash.snakeCase``/``camelCase``; a su
  vez ``quitar_envoltura`` reproduce ``removeSurrounding`` de Kotlin y el
  recorte con ``hasPrefix``/``hasSuffix`` de Swift o ``String.prototype.slice``
  en JavaScript.
* ``normalizar_unicode`` acepta las formas ``NFC``, ``NFD``, ``NFKC`` y
  ``NFKD`` para unificar representaciones.
* ``indentar_texto``/``desindentar_texto``, ``envolver_texto`` y
  ``acortar_texto`` envuelven párrafos al estilo de ``textwrap``.
* Las comprobaciones ``es_alfabetico``, ``es_alfa_numerico``, ``es_decimal``,
  ``es_numerico``, ``es_identificador``, ``es_imprimible``, ``es_ascii``,
  ``es_mayusculas``, ``es_minusculas`` y ``es_espacio`` reflejan los métodos
  ``str.is*`` de Python y se exponen también desde
  :mod:`standard_library.texto` junto con utilidades como ``quitar_acentos``.

.. code-block:: python

   import pcobra.corelibs as core
   import standard_library.texto as texto

   print(core.quitar_prefijo("🧪Prueba", "🧪"))
   print(core.prefijo_comun("Canción", "cancio\u0301n", ignorar_mayusculas=True, normalizar="NFC"))
   print(texto.sufijo_comun("astronomía", "economía"))
   print(texto.es_palindromo("Sé verlas al revés"))
   print(core.a_snake("MiValorHTTP"))
   print(texto.a_camel("hola-mundo cobra", inicial_mayuscula=True))
   print(core.quitar_envoltura("«mañana»", "«", "»"))

Asimismo, :mod:`pcobra.corelibs.numero` incorpora ``interpolar`` y
``envolver_modular`` inspiradas en ``f32::lerp`` de Rust y en
``kotlin.math.lerp``/``mod``. La primera acota el factor a ``[0, 1]`` para
evitar extrapolaciones involuntarias y la segunda devuelve residuos euclidianos
con el mismo signo que el divisor incluso si se usan valores negativos.

.. code-block:: python

   import pcobra.corelibs as core
   import standard_library.numero as numero

   print(core.interpolar(10.0, 20.0, 1.5))    # 20.0
   print(numero.interpolar(-5.0, 5.0, 0.25))  # 0.0
   print(core.envolver_modular(-3, 5))         # 2
   print(numero.envolver_modular(7.5, -5.0))   # -2.5

Transpilación y ejecución
-------------------------

El comando ``cobra compilar`` genera código para múltiples lenguajes. También
puede ejecutarse un archivo directamente con ``cobra ejecutar``.
El subcomando ``cobra verificar`` (``cobra verify`` en la versión en inglés)
permite comparar la salida de un programa transpilado a distintos lenguajes
(actualmente Python y JavaScript) y avisa si alguna difiere.
Adicionalmente puedes convertir código escrito en otros lenguajes a Cobra y
volver a transpilarlos con ``cobra transpilar-inverso``::

   cobra transpilar-inverso ejemplo.py --origen=python --destino=js

Limitaciones de los backends
----------------------------

* **Python y JavaScript**: implementan la mayoría de características y son los
  más estables.
* **C y C++**: se consideran experimentales; no soportan clases ni excepciones
  complejas.
* **Rust**: carece de herencia múltiple y requiere anotaciones de tipo
  explícitas para estructuras complejas.
* **WebAssembly**: limitado a operaciones numéricas básicas y sin soporte de
  cadenas.
* **Otros backends** (Go, R, Julia, etc.): poseen cobertura parcial y pueden
  carecer de bibliotecas estándar equivalentes.

Recomendaciones de estilo
-------------------------

* Utiliza indentación de cuatro espacios y nombres en ``snake_case``.
* Mantén los comentarios en español y procura líneas de menos de 79 caracteres.
* Prefiere expresiones claras antes que construcciones complejas y evita macros
  innecesarias.

Funciones del sistema
---------------------

La biblioteca estándar expone ``corelibs.sistema.ejecutar`` para lanzar procesos del
sistema. Por motivos de seguridad es **obligatorio** proporcionar una lista blanca de
ejecutables permitidos mediante el parámetro ``permitidos`` o definiendo la variable
de entorno ``COBRA_EJECUTAR_PERMITIDOS`` separada por ``os.pathsep``. La lista se
captura al importar el módulo, por lo que modificar la variable de entorno después no
surte efecto. Invocar la función sin esta configuración producirá un ``ValueError``.

Limitaciones de recursos en Windows
-----------------------------------

En sistemas Windows, las funciones que intentan limitar la memoria o el tiempo
de CPU pueden no aplicarse. Cobra mostrará advertencias como::

   No se pudo establecer el límite de memoria en Windows; el ajuste se omitirá.
   No se pudo establecer el límite de CPU en Windows; el ajuste se omitirá.

Para asegurar estos límites, ejecuta Cobra dentro de un contenedor (por
ejemplo, Docker o WSL2) donde las restricciones de recursos sí se pueden
aplicar.

Recursos adicionales
--------------------

- :doc:`guia_basica <guia_basica>`
- :doc:`especificacion_tecnica <especificacion_tecnica>`
- :doc:`recursos_adicionales <frontend/recursos_adicionales>`
