# Proyecto Cobra
[![Codecov](https://codecov.io/gh/Alphonsus411/pCobra/branch/master/graph/badge.svg)](https://codecov.io/gh/Alphonsus411/pCobra)
[![Versión estable](https://img.shields.io/github/v/release/Alphonsus411/pCobra?label=stable)](https://github.com/Alphonsus411/pCobra/releases/latest)


Versión 8.0.0

Cobra es un lenguaje de programación diseñado en español, enfocado en la creación de herramientas, simulaciones y análisis en áreas como biología, computación y astrofísica. Este proyecto incluye un lexer, parser y transpiladores a Python, JavaScript, ensamblador, Rust, C++, Go, R, Julia, Java, COBOL, Fortran, Pascal, Ruby, PHP, Matlab y LaTeX, lo que permite una mayor versatilidad en la ejecución y despliegue del código escrito en Cobra.

## Tabla de Contenidos

- Descripción del Proyecto
- Instalación
- Estructura del Proyecto
- Características Principales
- Uso
- Tokens y reglas léxicas
- Ejemplo de Uso
- Pruebas
- Generar documentación
- Análisis con CodeQL
- [CobraHub](frontend/docs/cobrahub.rst)
- Hitos y Roadmap
- Contribuciones
- [Guía de Contribución](CONTRIBUTING.md)
- [Proponer extensiones](frontend/docs/rfc_plugins.rst)
- [Comunidad](docs/comunidad.md)
- Licencia
- [Manual de Cobra](MANUAL_COBRA.md)
- [Manual de Cobra en formato reStructuredText](docs/MANUAL_COBRA.rst)
- [Guía básica](docs/guia_basica.md)
- [Especificación técnica](docs/especificacion_tecnica.md)
- [Cheatsheet](docs/cheatsheet.tex) – compílalo a PDF con LaTeX
- [Casos de uso reales](docs/casos_reales.md)
- Notebooks de ejemplo y casos reales
- [Historial de cambios](CHANGELOG.md)

## Ejemplos

Proyectos de demostracion disponibles en [cobra-ejemplos](https://github.com/tuusuario/cobra-ejemplos).
Este repositorio incluye ejemplos básicos en la carpeta `examples/`, por
ejemplo `examples/funciones_principales.co` que muestra condicionales, bucles y
definición de funciones en Cobra.
Para ejemplos interactivos revisa los cuadernos en `notebooks/casos_reales/`.

### Ejemplos avanzados

En [examples/avanzados/](examples/avanzados/) se incluyen programas que profundizan
en Cobra con ejercicios de control de flujo, funciones recursivas e interacción
de clases. Cada tema cuenta con su propia carpeta:

- [examples/avanzados/control_flujo/](examples/avanzados/control_flujo/)
- [examples/avanzados/funciones/](examples/avanzados/funciones/)
- [examples/avanzados/clases/](examples/avanzados/clases/)

## Notebooks de ejemplo

En la carpeta `notebooks/` se incluye el cuaderno `ejemplo_basico.ipynb` con un ejemplo básico de uso de Cobra. Además, los cuadernos de `notebooks/casos_reales/` muestran cómo ejecutar los ejemplos avanzados. Para abrirlo ejecuta:

```bash
cobra jupyter --notebook notebooks/ejemplo_basico.ipynb
```
Si omites el argumento ``--notebook`` se abrirá Jupyter Notebook de manera convencional y podrás escoger el archivo desde la interfaz web.
 


## Descripción del Proyecto

Cobra está diseñado para facilitar la programación en español, permitiendo que los desarrolladores utilicen un lenguaje más accesible. A través de su lexer, parser y transpiladores, Cobra puede analizar, ejecutar y convertir código a otros lenguajes, brindando soporte para variables, funciones, estructuras de control y estructuras de datos como listas, diccionarios y clases.
Para un tutorial paso a paso consulta el [Manual de Cobra](docs/MANUAL_COBRA.rst).
La especificación completa del lenguaje se encuentra en [SPEC_COBRA.md](SPEC_COBRA.md).

## Instalación

Para instalar el proyecto, sigue estos pasos:

1. Clona el repositorio en tu máquina local:

   ```bash
   git clone https://github.com/Alphonsus411/pCobra.git
   ````
   
2. Accede al directorio del proyecto:

````bash
cd pCobra
````

3. Crea un entorno virtual y actívalo:

````bash
python -m venv .venv
source .venv/bin/activate  # Para Unix
.\.venv\Scripts\activate  # Para Windows
````

4. Instala las dependencias necesarias:

````bash
pip install -r requirements.txt
````

   Además del archivo ``requirements.txt`` la CLI consultará
   ``pyproject.toml`` para incluir las dependencias definidas en
   las secciones ``project.dependencies`` y
   ``project.optional-dependencies``.

   Esto instalará los paquetes mínimos para ejecutar Cobra:

   - `pytest` y complementos para las pruebas automatizadas.
   - `ipykernel` para el kernel de Jupyter.
   - `PyYAML` utilizado al leer `cobra.mod`.
   - `cbindgen` para generar encabezados de crates Rust
     (instalable con `cargo install cbindgen`).
   - `tomli` necesario para Python anterior a la versión 3.11.

5. Instala el paquete de forma editable para usar la CLI:

````bash
pip install -e .
````

6. Ejecuta un programa de prueba para verificar la instalación:

````bash
echo "imprimir('Hola Cobra')" > hola.co
cobra ejecutar hola.co
````

### Instalación con pipx

[pipx](https://pypa.github.io/pipx/) es una herramienta para instalar y ejecutar aplicaciones de Python de forma aislada y requiere Python 3.6 o superior. Para instalar Cobra con pipx ejecuta:

```bash
pipx install cobra-lenguaje
```

Si prefieres instalar Cobra directamente desde PyPI sin usar
`pipx`, ejecuta:

```bash
pip install cobra-lenguaje
```

## Construir la imagen Docker

Puedes crear la imagen utilizando el script `docker/scripts/build.sh` o el subcomando de la CLI:

````bash
cobra contenedor --tag cobra
````

Esto ejecutará internamente ``docker build`` y generará una imagen llamada `cobra` en tu sistema Docker.

## Descarga de binarios

Para cada lanzamiento se generan ejecutables para Linux, Windows y macOS mediante
GitHub Actions. Puedes encontrarlos en la pestaña
[Releases](https://github.com/Alphonsus411/pCobra/releases) del repositorio.
Solo descarga el archivo correspondiente a tu sistema operativo desde la versión
más reciente y ejecútalo directamente.

Crear un tag `vX.Y.Z` en GitHub desencadena la publicación automática del
paquete en PyPI y la actualización de la imagen Docker.

Si prefieres generar el ejecutable manualmente ejecuta desde la raíz del
repositorio en tu sistema (Windows, macOS o Linux):

```bash
pip install pyinstaller
cobra empaquetar --output dist
```
El nombre del binario puede ajustarse con la opción `--name`. También puedes
usar un archivo `.spec` propio o agregar datos adicionales mediante
``--spec`` y ``--add-data``:

```bash
cobra empaquetar --spec build/cobra.spec \
  --add-data "all-bytes.dat;all-bytes.dat" --output dist
```

# Estructura del Proyecto

El proyecto se organiza en las siguientes carpetas y módulos:

- `backend/src/`: Contiene la lógica Python del proyecto.
- `frontend/docs/` y `frontend/build/`: Carpetas donde se genera y aloja la documentación. El archivo `frontend/docs/arquitectura.rst` describe la estructura interna del lenguaje.
- `tests/`: Incluye pruebas unitarias para asegurar el correcto funcionamiento del código.
- `README.md`: Documentación del proyecto.
- `requirements.txt`: Archivo que lista las dependencias del proyecto.
- `pyproject.toml`: También define dependencias en las secciones
  ``project.dependencies`` y ``project.optional-dependencies``.

# Características Principales

- Lexer y Parser: Implementación de un lexer para la tokenización del código fuente y un parser para la construcción de un árbol de sintaxis abstracta (AST).
- Transpiladores a Python, JavaScript, ensamblador, Rust, C++, Go, R, Julia, Java, COBOL, Fortran, Pascal, Ruby, PHP, Matlab y LaTeX: Cobra puede convertir el código en estos lenguajes, facilitando su integración con aplicaciones externas.
- Soporte de Estructuras Avanzadas: Permite la declaración de variables, funciones, clases, listas y diccionarios, así como el uso de bucles y condicionales.
- Módulos nativos con funciones de E/S, utilidades matemáticas y estructuras de datos para usar directamente desde Cobra.
- Instalación de paquetes en tiempo de ejecución mediante la instrucción `usar`.
- Manejo de Errores: El sistema captura y reporta errores de sintaxis, facilitando la depuración.
- Visualización y Depuración: Salida detallada de tokens, AST y errores de sintaxis para un desarrollo más sencillo.
- Decoradores de rendimiento: la biblioteca ``smooth-criminal`` ofrece
  funciones como ``optimizar`` y ``perfilar`` para mejorar y medir la
  ejecución de código Python desde Cobra.
- Benchmarking: ejemplos completos de medición de rendimiento están
  disponibles en `frontend/docs/benchmarking.rst`.
- Ejemplos de Código y Documentación: Ejemplos prácticos que ilustran el uso del lexer, parser y transpiladores.
- Ejemplos Avanzados: Revisa `frontend/docs/ejemplos_avanzados.rst` para conocer casos con clases, hilos y manejo de errores.
- Identificadores en Unicode: Puedes nombrar variables y funciones utilizando
  caracteres como `á`, `ñ` o `Ω` para una mayor flexibilidad.

## Rendimiento

Los benchmarks más recientes se ejecutaron con
`scripts/benchmarks/compare_backends.py` para comparar varios backends. El
tiempo aproximado fue de **0.68&nbsp;s** para Cobra y Python,
**0.07&nbsp;s** para JavaScript y **0.04&nbsp;s** para Rust, sin consumo
significativo de memoria.

Ejecuta el script con:

```bash
python scripts/benchmarks/compare_backends.py --output bench_results.json
```

El archivo [bench_results.json](bench_results.json) se guarda en el directorio
actual y puede analizarse con el cuaderno
[notebooks/benchmarks_resultados.ipynb](notebooks/benchmarks_resultados.ipynb).

# Uso

Para conocer las opciones avanzadas del modo seguro revisa
`frontend/docs/modo_seguro.rst`. Los ejemplos de medición de rendimiento
están disponibles en `frontend/docs/benchmarking.rst`.

Para ejecutar pruebas unitarias, utiliza pytest:

````bash
PYTHONPATH=$PWD pytest backend/src/tests --cov=backend/src --cov-report=term-missing \
  --cov-fail-under=85
````

También puedes ejecutar suites específicas ubicadas en `backend/src/tests`:

````bash
python -m tests.suite_cli           # Solo pruebas de la CLI
python -m tests.suite_core          # Pruebas de lexer, parser e intérprete
python -m tests.suite_transpiladores  # Pruebas de los transpiladores
````

## Tokens y reglas léxicas

El analizador léxico convierte el código en tokens de acuerdo con las
expresiones regulares definidas en `lexer.py`. En la siguiente tabla se
describen todos los tokens disponibles:

| Token | Descripción |
|-------|-------------|
| DIVIDIR | Palabra clave o instrucción "dividir" |
| MULTIPLICAR | Palabra clave o instrucción "multiplicar" |
| CLASE | Palabra clave "clase" |
| DICCIONARIO | Palabra clave "diccionario" |
| LISTA | Palabra clave "lista" |
| RBRACE | Símbolo "}" |
| DEF | Palabra clave "def" |
| IN | Palabra clave "in" |
| LBRACE | Símbolo "{" |
| FOR | Palabra clave "for" |
| DOSPUNTOS | Símbolo ":" |
| VAR | Palabra clave "var" |
| FUNC | Palabra clave "func" o "definir" |
| REL | Palabra clave "rel" |
| SI | Palabra clave "si" |
| SINO | Palabra clave "sino" |
| MIENTRAS | Palabra clave "mientras" |
| PARA | Palabra clave "para" |
| IMPORT | Palabra clave "import" |
| USAR | Palabra clave "usar" |
| MACRO | Palabra clave "macro" |
| HOLOBIT | Palabra clave "holobit" |
| PROYECTAR | Palabra clave "proyectar" |
| TRANSFORMAR | Palabra clave "transformar" |
| GRAFICAR | Palabra clave "graficar" |
| TRY | Palabra clave "try" o "intentar" |
| CATCH | Palabra clave "catch" o "capturar" |
| THROW | Palabra clave "throw" o "lanzar" |
| ENTERO | Número entero |
| FLOTANTE | Número con punto decimal |
| CADENA | Cadena de caracteres |
| BOOLEANO | Literal booleano |
| IDENTIFICADOR | Nombre de variable o función |
| ASIGNAR | Símbolo "=" |
| SUMA | Operador "+" |
| RESTA | Operador "-" |
| MULT | Operador "*" |
| DIV | Operador "/" |
| MAYORQUE | Operador ">" |
| MENORQUE | Operador "<" |
| MAYORIGUAL | Operador ">=" |
| MENORIGUAL | Operador "<=" |
| IGUAL | Operador "==" |
| DIFERENTE | Operador "!=" |
| AND | Operador lógico "&&" |
| OR | Operador lógico "||" |
| NOT | Operador "!" |
| MOD | Operador "%" |
| LPAREN | Símbolo "(" |
| RPAREN | Símbolo ")" |
| LBRACKET | Símbolo "[" |
| RBRACKET | Símbolo "]" |
| COMA | Símbolo "," |
| RETORNO | Palabra clave "retorno" |
| FIN | Palabra clave "fin" |
| EOF | Fin de archivo |
| IMPRIMIR | Palabra clave "imprimir" |
| HILO | Palabra clave "hilo" |
| ASINCRONICO | Palabra clave "asincronico" |
| DECORADOR | Símbolo "@" |
| YIELD | Palabra clave "yield" |
| ESPERAR | Palabra clave "esperar" |
| ROMPER | Palabra clave "romper" |
| CONTINUAR | Palabra clave "continuar" |
| PASAR | Palabra clave "pasar" |
| AFIRMAR | Palabra clave "afirmar" |
| ELIMINAR | Palabra clave "eliminar" |
| GLOBAL | Palabra clave "global" |
| NOLOCAL | Palabra clave "nolocal" |
| LAMBDA | Palabra clave "lambda" |
| CON | Palabra clave "con" |
| FINALMENTE | Palabra clave "finalmente" |
| DESDE | Palabra clave "desde" |
| COMO | Palabra clave "como" |
| SWITCH | Palabra clave "switch" o "segun" |
| CASE | Palabra clave "case" o "caso" |

Las expresiones regulares se agrupan en `especificacion_tokens` y se procesan en orden para encontrar coincidencias. Las palabras clave usan patrones como `\bvar\b` o `\bfunc\b`, los números emplean `\d+` o `\d+\.\d+` y las cadenas se detectan con `"[^\"]*"` o `'[^']*'`. Los identificadores permiten caracteres Unicode mediante `[^\W\d_][\w]*`. Operadores y símbolos utilizan patrones directos como `==`, `&&` o `\(`. Antes del análisis se eliminan los comentarios de línea y de bloque con `re.sub`.

# Ejemplo de Uso

Puedes probar el lexer y parser con un código como el siguiente:

````cobra
codigo = '''
var x = 10
si x > 5 :
    proyectar(x, "2D")
sino :
    graficar(x)
'''

# Inicializamos el lexer
lexer = Lexer(codigo)
tokens = lexer.analizar_token()

# Inicializamos el parser
parser = Parser(tokens)

# Ejecutar el parser para obtener el AST
arbol = parser.parsear()
print(arbol)

# Generación de código en Python
transpiler = TranspiladorPython()
codigo_python = transpiler.generate_code(arbol)
print(codigo_python)
````

## Ejemplo de imprimir, holobits y bucles

A continuación se muestra un fragmento que utiliza `imprimir`, holobits y bucles:

````cobra
codigo = '''
var h = holobit([0.8, -0.5, 1.2])
imprimir(h)

var contador = 0
mientras contador < 3 :
    imprimir(contador)
    contador += 1

para var i en rango(2) :
    imprimir(i)
'''
````

Al generar código para Python, `imprimir` se convierte en `print`, `mientras` en `while` y `para` en `for`. En JavaScript estos elementos se transforman en `console.log`, `while` y `for...of` respectivamente. Para el modo ensamblador se generan instrucciones `PRINT`, `WHILE` y `FOR`. En Rust se produce código equivalente con `println!`, `while` y `for`. En C++ se obtienen construcciones con `std::cout`, `while` y `for`. El tipo `holobit` se traduce a la llamada `holobit([...])` en Python, `new Holobit([...])` en JavaScript, `holobit(vec![...])` en Rust o `holobit({ ... })` en C++. En Go se genera `fmt.Println`, en R se usa `print` y en Julia `println`; en Java se usa `System.out.println`, en COBOL `DISPLAY`, en Fortran `print *` y en Pascal `writeln`, en Ruby `puts`, en PHP `echo`, en Matlab `disp` y en LaTeX `\texttt{}`.

## Integración con holobit-sdk

El proyecto instala automáticamente la librería `holobit-sdk`, utilizada para visualizar y manipular holobits. Las funciones `graficar`, `proyectar` y `transformar` de `src.core.holobits` delegan en esta API.

```python
from src.core.holobits import Holobit, graficar, proyectar, transformar

h = Holobit([0.8, -0.5, 1.2, 0.0, 0.0, 0.0])
proyectar(h, "2D")
graficar(h)
transformar(h, "rotar", "z", 90)
```

## Ejemplo de carga de módulos

Puedes dividir el código en varios archivos y cargarlos con `import`:

````cobra
# modulo.co
var saludo = 'Hola desde módulo'

# programa.co
import 'modulo.co'
imprimir(saludo)
````

Al ejecutar `programa.co`, se procesará primero `modulo.co` y luego se imprimirá `Hola desde módulo`.

## Instrucción `usar` para dependencias dinámicas

La sentencia `usar "paquete"` intenta importar un módulo de Python. Si el
paquete no está disponible, Cobra ejecutará `pip install paquete` para
instalarlo y luego lo cargará en tiempo de ejecución. El módulo queda
registrado en el entorno bajo el mismo nombre para su uso posterior.
Para restringir qué dependencias pueden instalarse se emplea la variable
`USAR_WHITELIST` definida en `backend/src/cobra/usar_loader.py`. Basta con
añadir o quitar nombres de paquetes en dicho conjunto para modificar la lista
autorizada. Si la lista se deja vacía la función `obtener_modulo` lanzará
`PermissionError`, por lo que es necesario poblarla antes de permitir
instalaciones dinámicas.

## Archivo de mapeo de módulos

Los transpiladores consultan `cobra.mod` para resolver las importaciones.
Este archivo sigue un esquema YAML sencillo donde cada clave es la ruta del
módulo Cobra y sus valores indican las rutas de los archivos generados.

Ejemplo de formato:

```yaml
modulo.co:
  version: "1.0.0"
  python: modulo.py
  js: modulo.js
```

Si una entrada no se encuentra, el transpilador cargará directamente el archivo
indicado en la instrucción `import`. Para añadir o modificar rutas basta con
editar `cobra.mod` y volver a ejecutar las pruebas.

## Invocar el transpilador

La carpeta [`backend/src/cobra/transpilers/transpiler`](backend/src/cobra/transpilers/transpiler)
contiene la implementación de los transpiladores a Python, JavaScript, ensamblador, Rust, C++, Go, R, Julia, Java, COBOL, Fortran, Pascal, Ruby, PHP, Matlab y LaTeX. Una vez
instaladas las dependencias, puedes llamar al transpilador desde tu propio
script de la siguiente manera:

```python
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.parser.parser import Parser

codigo = "imprimir('hola')"
parser = Parser(codigo)
arbol = parser.parsear()
transpiler = TranspiladorPython()
resultado = transpiler.generate_code(arbol)
print(resultado)
```

Para otros lenguajes puedes invocar los nuevos transpiladores así:

```python
from cobra.transpilers.transpiler.to_cobol import TranspiladorCOBOL
from cobra.transpilers.transpiler.to_fortran import TranspiladorFortran
from cobra.transpilers.transpiler.to_pascal import TranspiladorPascal
from cobra.transpilers.transpiler.to_ruby import TranspiladorRuby
from cobra.transpilers.transpiler.to_php import TranspiladorPHP
from cobra.transpilers.transpiler.to_matlab import TranspiladorMatlab
from cobra.transpilers.transpiler.to_latex import TranspiladorLatex

codigo_cobol = TranspiladorCOBOL().generate_code(arbol)
codigo_fortran = TranspiladorFortran().generate_code(arbol)
codigo_pascal = TranspiladorPascal().generate_code(arbol)
codigo_ruby = TranspiladorRuby().generate_code(arbol)
codigo_php = TranspiladorPHP().generate_code(arbol)
codigo_matlab = TranspiladorMatlab().generate_code(arbol)
codigo_latex = TranspiladorLatex().generate_code(arbol)
```

Tras obtener el código con ``generate_code`` puedes guardarlo usando ``save_file``:

```python
transpiler.save_file("salida.py")
```

Requiere tener instalado el paquete en modo editable y todas las dependencias
de `requirements.txt`. Si necesitas generar archivos a partir de módulos Cobra,
consulta el mapeo definido en `cobra.mod`.

## Ejemplo de concurrencia

Es posible lanzar funciones en hilos con la palabra clave `hilo`:

````cobra
func tarea():
    imprimir('trabajo')
fin

hilo tarea()
imprimir('principal')
````

Al generar código para estas funciones, se crean llamadas `asyncio.create_task` en Python y `Promise.resolve().then` en JavaScript.

## Uso desde la CLI

Una vez instalado el paquete, la herramienta `cobra` ofrece varios subcomandos:

```bash
# Compilar un archivo a Python, JavaScript, ensamblador, Rust, C++, Go, R, Julia, Java, COBOL, Fortran, Pascal, Ruby, PHP, Matlab o LaTeX
cobra compilar programa.co --tipo python

# Ejemplo de mensaje de error al compilar un archivo inexistente
cobra compilar noexiste.co
# Salida:
# Error: El archivo 'noexiste.co' no existe

# Ejecutar directamente un script Cobra
cobra ejecutar programa.co --depurar --formatear

# Gestionar módulos instalados
cobra modulos listar
cobra modulos instalar ruta/al/modulo.co
cobra modulos remover modulo.co
# Crear e instalar paquetes Cobra
cobra paquete crear src demo.cobra
cobra paquete instalar demo.cobra
# Generar documentación HTML y API
cobra docs
# Crear un ejecutable independiente
cobra empaquetar --output dist
# Perfilar un programa y guardar los resultados
cobra profile programa.co --output salida.prof
# O mostrar el perfil directamente en pantalla
cobra profile programa.co
# Iniciar el iddle gráfico (requiere Flet)
cobra gui
```

Al iniciar la CLI se muestra una cabecera con el logo de Cobra:

```bash
$ cobra --help
  ____        _               ____ _     ___
 / ___|___   | |__   ___ _ __/ ___| |   |_ _|
| |   / _ \  | '_ \ / _ \ '__| |   | |    | |
| |__| (_) | | |_) |  __/ |  | |___| |___ | |
 \____\___/  |_.__/ \___|_|   \____|_____|___|
usage: cobra [-h] [--formatear] ...
```

Si deseas desactivar los colores usa `--no-color`:

```bash
cobra --no-color ejecutar programa.co
```

Los archivos con extensión ``.cobra`` representan paquetes completos, mientras que los scripts individuales se guardan como ``.co``.

El subcomando `docs` ejecuta `sphinx-apidoc` para generar la documentación de la API antes de compilar el HTML.
El subcomando `gui` abre el iddle integrado y requiere tener instalado Flet.


Si no se pasa un subcomando se abrirá el modo interactivo. Usa `cobra --help` para más detalles.

### Diseño extensible de la CLI

La CLI está organizada en clases dentro de `backend/src/cli/commands`. Cada subcomando
hereda de `BaseCommand` y define su nombre, los argumentos que acepta y la acción
a ejecutar. En `src/cli/cli.py` se instancian automáticamente y se registran en
`argparse`, por lo que para añadir un nuevo comando solo es necesario crear un
archivo con la nueva clase y llamar a `register_subparser` y `run`.
Para un tutorial completo de creación de plugins revisa
[`frontend/docs/plugins.rst`](frontend/docs/plugins.rst).

## Modo seguro (--seguro)

Tanto el intérprete como la CLI aceptan la opción `--seguro`, que ejecuta el código bajo restricciones adicionales. Al activarla se valida el AST y se prohíben primitivas como `leer_archivo`, `escribir_archivo`, `obtener_url`, `hilo`, `leer`, `escribir`, `existe`, `eliminar` y `enviar_post`. El validador `ValidadorProhibirReflexion` también bloquea llamadas a `eval`, `exec` y otras funciones de reflexión, además de impedir el acceso a atributos internos. Asimismo, las instrucciones `import` solo están permitidas para módulos instalados o incluidos en `IMPORT_WHITELIST`. Si el programa intenta utilizar estas funciones o importar otros archivos se lanzará `PrimitivaPeligrosaError`.
La validación se realiza mediante una cadena de validadores configurada por la
función `construir_cadena`, lo que facilita añadir nuevas comprobaciones en el
futuro.

## Ejecución en sandbox (--sandbox)

Algunos comandos permiten ejecutar código Python dentro de una "sandbox" gracias
a la biblioteca `RestrictedPython`. Esto limita las operaciones disponibles y
evita acciones potencialmente peligrosas como leer archivos o importar módulos
externos. Para activar esta opción utiliza `--sandbox` en los subcomandos
`ejecutar` e `interactive`.

# Pruebas

Las pruebas están ubicadas en la carpeta tests/ y utilizan pytest para la ejecución. Antes de correrlas añade el proyecto al `PYTHONPATH` o instala el paquete en modo editable (`pip install -e .`). Así pytest podrá encontrar los módulos correctamente.

````bash
PYTHONPATH=$PWD pytest backend/src/tests --cov=backend/src --cov-report=term-missing \
  --cov-fail-under=85
````

Algunas pruebas generan código en distintos lenguajes (por ejemplo C++, JavaScript o Go) y verifican que la sintaxis sea correcta. Para que estas pruebas se ejecuten con éxito es necesario contar con los compiladores o intérpretes correspondientes instalados en el sistema, como Node, gcc/g++, Go, etc. Puedes ejecutar todo el conjunto con:

```bash
PYTHONPATH=$PWD pytest
```

Se han incluido pruebas que verifican los códigos de salida de la CLI. Los
subcomandos devuelven `0` al finalizar correctamente y un valor distinto en caso
de error.

### Ejemplos de subcomandos

````bash
cobra compilar programa.co --tipo=python
cobra compilar programa.co --tipo=asm
cobra compilar programa.co --tipo=cpp
cobra compilar programa.co --tipo=go
cobra compilar programa.co --tipo=ruby
cobra compilar programa.co --tipo=r
cobra compilar programa.co --tipo=julia
cobra compilar programa.co --tipo=java
cobra compilar programa.co --tipo=cobol
cobra compilar programa.co --tipo=fortran
cobra compilar programa.co --tipo=pascal
cobra compilar programa.co --tipo=php
echo $?  # 0 al compilar sin problemas

cobra ejecutar inexistente.co
# El archivo 'inexistente.co' no existe
echo $?  # 1
````

### Errores comunes

- `El archivo '<archivo>' no existe`: la ruta es incorrecta o el archivo no está disponible.
- `El módulo <nombre> no existe`: se intenta eliminar un módulo no instalado.
- `Primitiva peligrosa: <nombre>`: se usó una función restringida en modo seguro.
- `Acción de módulos no reconocida`: el subcomando indicado es inválido.

## Selección de idioma

La CLI utiliza `gettext` para mostrar los mensajes en distintos idiomas.
Puedes definir el idioma estableciendo la variable de entorno `COBRA_LANG`
o pasando el argumento `--lang` al ejecutar `cobra`.

```bash
COBRA_LANG=en cobra --help
cobra --lang en compilar archivo.co
```

Si deseas añadir otro idioma, crea una carpeta `frontend/docs/locale/<cod>/LC_MESSAGES`
con los archivos `.po` de traducción y envía un pull request.

Para obtener un reporte de cobertura en la terminal ejecuta:

````bash
pytest --cov=backend/src --cov-report=term-missing --cov-fail-under=85
````

## Caché del AST

Cobra guarda los árboles de sintaxis en la carpeta `cache` situada en la
raíz del proyecto. Cada archivo se nombra con el SHA256 del código y tiene
extensión `.ast`. Puedes cambiar la ubicación definiendo la variable de
entorno `COBRA_AST_CACHE` antes de ejecutar la compilación.

Para limpiar la caché elimina los archivos de dicho directorio:

```bash
rm cache/*.ast
```

## Generar documentación

Para obtener la documentación HTML puedes usar `cobra docs` o
`make html` desde la raíz del proyecto. El subcomando `docs` ejecuta
`sphinx-apidoc` y luego compila el HTML en `frontend/build/html`.

Puedes compilar la documentación de dos maneras:

1. **Con la CLI de Cobra**. Ejecuta `cobra docs`.

2. **Con Make**. Ejecuta `make html` para compilar los archivos ubicados en
   `frontend/docs`.

3. **Con pdoc**. Para generar documentación de la API con [pdoc](https://pdoc.dev),
   ejecuta `python scripts/generar_pdoc.py`. El resultado se guardará en
   `frontend/build/pdoc`.

A partir de esta versión, la API se genera de forma automática antes de
cada compilación para mantener la documentación actualizada.
Para aprender a desarrollar plugins revisa
[`frontend/docs/plugin_dev.rst`](frontend/docs/plugin_dev.rst).
Para conocer en detalle la interfaz disponible consulta
[`frontend/docs/plugin_sdk.rst`](frontend/docs/plugin_sdk.rst).

## Análisis con CodeQL

Este proyecto cuenta con un workflow de GitHub Actions definido en
`.github/workflows/codeql.yml`. Dicho flujo se ejecuta en cada *push* y
*pull request*, inicializando CodeQL para el lenguaje Python y aplicando
reglas personalizadas ubicadas en `.github/codeql/custom/`.

Las reglas proporcionan comprobaciones adicionales sobre el AST y los
transpiladores:

- **ast-no-type-validation.ql** verifica que las clases de nodos cuyo
  nombre empieza por `Nodo` incluyan validaciones de tipo en
  `__post_init__`.
- **missing-codegen-exception.ql** detecta métodos `generate_code` sin
  manejo de excepciones.

Para ejecutar el análisis de CodeQL de forma local puedes usar la CLI:

```bash
curl -L -o codeql.zip \
  https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-linux64.zip
unzip codeql.zip
./codeql/codeql database create db-python --language=python --source-root=.
./codeql/codeql database analyze db-python \
  .github/codeql/custom/codeql-config.yml
```

Esto te permitirá validar los cambios antes de subirlos al repositorio.
## Hitos y Roadmap

El proyecto avanza en versiones incrementales. Puedes consultar las tareas planeadas en [ROADMAP.md](ROADMAP.md).


# Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, sigue estos pasos:

- Haz un fork del proyecto.
- Crea una nueva rama (`git checkout -b feature/nueva-caracteristica`).
- Las ramas que comiencen con `feature/`, `bugfix/` o `doc/` recibirán etiquetas
  automáticas al abrir un pull request.
- Sigue las convenciones de estilo indicadas en `CONTRIBUTING.md` 
  (formateo con `black`, longitud máxima de línea 88 y uso de `flake8`, `mypy`
  y `bandit`).
- Realiza tus cambios y haz commit (`git commit -m 'Añadir nueva característica'`).
- Ejecuta `make lint` para verificar el código con *flake8*, *mypy* y *bandit*.
- Ejecuta `make typecheck` para la verificación estática con *mypy* (y
  opcionalmente *pyright* si está instalado).
- El CI de GitHub Actions ejecuta automáticamente estas herramientas en cada pull request.
- Envía un pull request.
- Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles sobre cómo abrir
  issues y preparar pull requests.
- Para proponer nuevas extensiones consulta [frontend/docs/rfc_plugins.rst](frontend/docs/rfc_plugins.rst).

## Dependabot y seguridad

Este repositorio cuenta con [Dependabot](.github/dependabot.yml) para mantener
actualizadas las dependencias de Python y las acciones de GitHub. Cada semana se
crean PR automáticos contra la rama `master` con las versiones más recientes.

Además, en el flujo de CI se incluye un paso de **safety check** que revisa la
lista de paquetes instalados en busca de vulnerabilidades conocidas. Si se
detecta alguna, la acción devolverá un reporte detallado y el trabajo fallará.
Consulta el log del paso "Seguridad de dependencias" para ver los paquetes
afectados y las recomendaciones de actualización.

## Comunidad

Únete a nuestro servidor de Discord para recibir anuncios, resolver dudas y colaborar en el desarrollo. Puedes unirte mediante este enlace permanente: [Enlace de invitación](https://discord.gg/placeholder).
También contamos con un canal de **Telegram** y una cuenta de **Twitter** donde difundimos eventos y actualizaciones.

## Desarrollo

Para verificar el tipado de forma local ejecuta:

```bash
mypy backend/src
pyright --project pyrightconfig.json
```

`mypy` utiliza la configuración de `mypy.ini` y `pyright` toma las rutas de `pyrightconfig.json`.

## Desarrollo de plugins

La CLI puede ampliarse mediante plugins externos. Desde esta versión todo el SDK
de plugins se encuentra en ``src.cli.plugin``. Para crear uno, define una clase
que herede de ``PluginCommand`` e incluye una entrada en el grupo
``cobra.plugins`` de tu ``setup.py``:

```python
entry_points={
    'cobra.plugins': [
        'saludo = mi_paquete.mi_modulo:SaludoCommand',
    ],
}
```

Tras instalar el paquete con `pip install -e .`, Cobra detectará automáticamente
el nuevo comando.

### Instalación de plugins

Para utilizar un plugin publicado solo necesitas instalar su paquete de
distribución. Por ejemplo:

```bash
pip install mi-plugin-cobra
```

Si estás desarrollando un plugin local puedes hacerlo en modo editable desde su
directorio:

```bash
pip install -e ./mi_plugin
```

Cada plugin se registra junto con su número de versión en un registro interno.
Puedes ver la lista de plugins disponibles ejecutando:

```bash
cobra plugins
```

### Ejemplo de plugin

```python
from src.cli.plugin import PluginCommand


class HolaCommand(PluginCommand):
    name = "hola"
    version = "1.0"
    author = "Tu Nombre"
    description = "Dice hola desde un plugin"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Muestra un saludo")
        parser.set_defaults(cmd=self)

    def run(self, args):
        print("¡Hola desde un plugin!")
```
## Versionado Semántico

Este proyecto sigue el esquema [SemVer](https://semver.org/lang/es/). Los numeros se interpretan como Mayor.Menor.Parche. Cada incremento de version refleja cambios compatibles o rupturas segun esta norma.

## Historial de Cambios

- Versión 8.0.0: actualización de documentación y archivos de configuración. Ver tareas en la sección v1.3 del roadmap.

# Licencia

Este proyecto está bajo la [Licencia MIT](LICENSE).


### Notas

- **Documentación y Ejemplos Actualizados**: El README ha sido actualizado para reflejar las capacidades de transpilación y la compatibilidad con Python, JavaScript, ensamblador, Rust, C++, Go, R, Julia, Java, COBOL, Fortran, Pascal y PHP.
- **Ejemplos de Código y Nuevas Estructuras**: Incluye ejemplos con el uso de estructuras avanzadas como clases y diccionarios en el lenguaje Cobra.

Si deseas agregar o modificar algo, házmelo saber.
