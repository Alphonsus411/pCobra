# Proyecto Cobra
[![codecov](https://codecov.io/gh/Alphonsus411/pCobra/branch/main/graph/badge.svg)](https://codecov.io/gh/Alphonsus411/pCobra)

Cobra es un lenguaje de programación diseñado en español, enfocado en la creación de herramientas, simulaciones y análisis en áreas como biología, computación y astrofísica. Este proyecto incluye un lexer, parser y transpiladores a Python y JavaScript, lo que permite una mayor versatilidad en la ejecución y despliegue del código escrito en Cobra.

## Tabla de Contenidos

- Descripción del Proyecto
- Instalación
- Estructura del Proyecto
- Características Principales
- Uso
- Ejemplo de Uso
- Pruebas
- Generar documentación
- Hitos y Roadmap
- Contribuciones
- Licencia
- [Manual de Cobra](MANUAL_COBRA.md)

## Descripción del Proyecto

Cobra está diseñado para facilitar la programación en español, permitiendo que los desarrolladores utilicen un lenguaje más accesible. A través de su lexer, parser y transpiladores, Cobra puede analizar, ejecutar y convertir código a otros lenguajes, brindando soporte para variables, funciones, estructuras de control y estructuras de datos como listas, diccionarios y clases.
Para un tutorial paso a paso consulta [Manual de Cobra](MANUAL_COBRA.md).

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

5. Instala el paquete de forma editable para usar la CLI:

````bash
pip install -e .
````

# Estructura del Proyecto

El proyecto se organiza en las siguientes carpetas y módulos:

- `backend/src/`: Contiene la lógica Python del proyecto.
- `frontend/docs/` y `frontend/build/`: Carpetas donde se genera y aloja la documentación. El archivo `frontend/docs/arquitectura.rst` describe la estructura interna del lenguaje.
- `tests/`: Incluye pruebas unitarias para asegurar el correcto funcionamiento del código.
- `README.md`: Documentación del proyecto.
- `requirements.txt`: Archivo que lista las dependencias del proyecto.

# Características Principales

- Lexer y Parser: Implementación de un lexer para la tokenización del código fuente y un parser para la construcción de un árbol de sintaxis abstracta (AST).
- Transpiladores a Python y JavaScript: Cobra puede convertir el código en estos lenguajes, facilitando su integración con aplicaciones externas.
- Soporte de Estructuras Avanzadas: Permite la declaración de variables, funciones, clases, listas y diccionarios, así como el uso de bucles y condicionales.
- Módulos nativos con funciones de E/S, utilidades matemáticas y estructuras de datos para usar directamente desde Cobra.
- Manejo de Errores: El sistema captura y reporta errores de sintaxis, facilitando la depuración.
- Visualización y Depuración: Salida detallada de tokens, AST y errores de sintaxis para un desarrollo más sencillo.
- Ejemplos de Código y Documentación: Ejemplos prácticos que ilustran el uso del lexer, parser y transpiladores.
- Identificadores en Unicode: Puedes nombrar variables y funciones utilizando
  caracteres como `á`, `ñ` o `Ω` para una mayor flexibilidad.

# Uso

Para ejecutar pruebas unitarias, utiliza pytest:

````bash
pytest backend/src/tests
````


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

# Transpilación a Python
transpiler = TranspiladorPython()
codigo_python = transpiler.transpilar(arbol)
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

Al transpilar a Python, `imprimir` se convierte en `print`, `mientras` en `while` y `para` en `for`. En JavaScript estos elementos se transforman en `console.log`, `while` y `for...of` respectivamente. El tipo `holobit` se transfiere a la llamada `holobit([...])` en Python o `new Holobit([...])` en JavaScript.

## Ejemplo de carga de módulos

Puedes dividir el código en varios archivos y cargarlos con `import`:

````cobra
# modulo.cobra
var saludo = 'Hola desde módulo'

# programa.cobra
import 'modulo.cobra'
imprimir(saludo)
````

Al ejecutar `programa.cobra`, se procesará primero `modulo.cobra` y luego se imprimirá `Hola desde módulo`.

## Ejemplo de concurrencia

Es posible lanzar funciones en hilos con la palabra clave `hilo`:

````cobra
func tarea():
    imprimir('trabajo')
fin

hilo tarea()
imprimir('principal')
````

Al transpilarlas, se generan llamadas `asyncio.create_task` en Python y `Promise.resolve().then` en JavaScript.

## Uso desde la CLI

Una vez instalado el paquete, la herramienta `cobra` ofrece varios subcomandos:

```bash
# Compilar un archivo a Python o JavaScript
cobra compilar programa.cobra --tipo python

# Ejecutar directamente un script Cobra
cobra ejecutar programa.cobra --depurar --formatear

# Gestionar módulos instalados
cobra modulos listar
cobra modulos instalar ruta/al/modulo.cobra
cobra modulos remover modulo.cobra
# Generar documentación HTML y API
cobra docs
```

El subcomando `docs` ejecuta `sphinx-apidoc` para generar la documentación de la API antes de compilar el HTML.


Si no se pasa un subcomando se abrirá el modo interactivo. Usa `cobra --help` para más detalles.

### Diseño extensible de la CLI

La CLI está organizada en clases dentro de `backend/src/cli/commands`. Cada subcomando
hereda de `BaseCommand` y define su nombre, los argumentos que acepta y la acción
a ejecutar. En `src/cli/cli.py` se instancian automáticamente y se registran en
`argparse`, por lo que para añadir un nuevo comando solo es necesario crear un
archivo con la nueva clase y llamar a `register_subparser` y `run`.

## Modo seguro (--seguro)

Tanto el intérprete como la CLI aceptan la opción `--seguro`, que ejecuta el código bajo restricciones adicionales. Al activarla se valida el AST y se prohíben primitivas como `leer_archivo`, `escribir_archivo`, `obtener_url` y `hilo`. Asimismo, las instrucciones `import` solo están permitidas para módulos instalados o incluidos en `IMPORT_WHITELIST`. Si el programa intenta utilizar estas funciones o importar otros archivos se lanzará `PrimitivaPeligrosaError`.
La validación se realiza mediante una cadena de validadores configurada por la
función `construir_cadena`, lo que facilita añadir nuevas comprobaciones en el
futuro.

# Pruebas

Las pruebas están ubicadas en la carpeta tests/ y utilizan pytest para la ejecución. Puedes añadir más pruebas para cubrir nuevos casos de uso y asegurar la estabilidad del código.

````bash
pytest backend/src/tests
````

Se han incluido pruebas que verifican los códigos de salida de la CLI. Los
subcomandos devuelven `0` al finalizar correctamente y un valor distinto en caso
de error.

### Ejemplos de subcomandos

````bash
cobra compilar programa.cobra --tipo=python
echo $?  # 0 al compilar sin problemas

cobra ejecutar inexistente.cobra
# El archivo 'inexistente.cobra' no existe
echo $?  # 1
````

### Errores comunes

- `El archivo '<archivo>' no existe`: la ruta es incorrecta o el archivo no está disponible.
- `El módulo <nombre> no existe`: se intenta eliminar un módulo no instalado.
- `Primitiva peligrosa: <nombre>`: se usó una función restringida en modo seguro.
- `Acción de módulos no reconocida`: el subcomando indicado es inválido.

Para obtener un reporte de cobertura en la terminal ejecuta:

````bash
pytest --cov=backend/src --cov-report=term-missing
````

## Generar documentación

Puedes compilar la documentación de dos maneras:

1. **Con la CLI de Cobra**. Ejecuta `cobra docs`. Este subcomando
   invoca `sphinx-apidoc` para generar automáticamente la API y luego
   usa Sphinx para crear el HTML en `frontend/build/html`.

2. **Con Make**. Desde la raíz del proyecto, ejecuta `make html` para
   compilar los archivos ubicados en `frontend/docs`.

3. **Con pdoc**. Para generar documentación de la API con [pdoc](https://pdoc.dev),
   ejecuta `python scripts/generar_pdoc.py`. El resultado se guardará en
   `frontend/build/pdoc`.

A partir de esta versión, la API se genera de forma automática antes de
cada compilación para mantener la documentación actualizada.
## Hitos y Roadmap

El proyecto avanza en versiones incrementales. A continuacion se listan las tareas previstas para las proximas entregas.

### v0.4

- Consolidar la gestion de dependencias en la CLI.
- Permitir la creacion de ejecutables para distribucion.
- Optimizar la validacion del modo seguro.
- Ampliar la documentacion con ejemplos avanzados.

### v0.5

- Incorporar un sistema de plugins para extender la CLI.
- Integrar soporte para ejecucion en Jupyter.
- Implementar optimizaciones del AST para mayor rendimiento.
- Anadir pruebas de concurrencia para mejorar la estabilidad.


# Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, sigue estos pasos:

- Haz un fork del proyecto.
- Crea una nueva rama (`git checkout -b feature/nueva-caracteristica`).
- Las ramas que comiencen con `feature/`, `bugfix/` o `doc/` recibirán etiquetas
  automáticas al abrir un pull request.
- Realiza tus cambios y haz commit (`git commit -m 'Añadir nueva característica'`).
- Envía un pull request.

# Licencia

Este proyecto está bajo la [Licencia MIT](LICENSE).


### Notas

- **Documentación y Ejemplos Actualizados**: El README ha sido actualizado para reflejar las capacidades de transpilación y la compatibilidad con Python y JavaScript.
- **Ejemplos de Código y Nuevas Estructuras**: Incluye ejemplos con el uso de estructuras avanzadas como clases y diccionarios en el lenguaje Cobra.

Si deseas agregar o modificar algo, házmelo saber.
