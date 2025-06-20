# Proyecto Cobra

Cobra es un lenguaje de programación diseñado en español, enfocado en la creación de herramientas, simulaciones y análisis en áreas como biología, computación y astrofísica. Este proyecto incluye un lexer, parser y transpiladores a Python y JavaScript, lo que permite una mayor versatilidad en la ejecución y despliegue del código escrito en Cobra.

## Tabla de Contenidos

- Descripción del Proyecto
- Instalación
- Estructura del Proyecto
- Características Principales
- Uso
- Ejemplo de Uso
- Pruebas
- Contribuciones
- Licencia

## Descripción del Proyecto

Cobra está diseñado para facilitar la programación en español, permitiendo que los desarrolladores utilicen un lenguaje más accesible. A través de su lexer, parser y transpiladores, Cobra puede analizar, ejecutar y convertir código a otros lenguajes, brindando soporte para variables, funciones, estructuras de control y estructuras de datos como listas, diccionarios y clases.

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

# Estructura del Proyecto

El proyecto se organiza en las siguientes carpetas y módulos:

- `core/`: Contiene la lógica principal del lexer y parser.
- `tests/`: Incluye pruebas unitarias para asegurar el correcto funcionamiento del código.
- `src/`: Carpeta principal donde se implementa la lógica del lenguaje Cobra.
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

# Uso

Para ejecutar pruebas unitarias, utiliza pytest:

````bash
pytest src/tests
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

## Uso desde la CLI

Una vez instalado el paquete, puedes ejecutar archivos Cobra con:

```bash
cobra ejemplo.cobra
```

Si no se especifica un archivo se abrirá el modo interactivo.

# Pruebas

Las pruebas están ubicadas en la carpeta tests/ y utilizan pytest para la ejecución. Puedes añadir más pruebas para cubrir nuevos casos de uso y asegurar la estabilidad del código.

````bash
pytest src/tests
````

# Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, sigue estos pasos:

- Haz un fork del proyecto.
- Crea una nueva rama (`git checkout -b feature/nueva-caracteristica`).
- Realiza tus cambios y haz commit (`git commit -m 'Añadir nueva característica'`).
- Envía un pull request.

# Licencia

Este proyecto está bajo la [Licencia MIT](LICENSE).


### Notas

- **Documentación y Ejemplos Actualizados**: El README ha sido actualizado para reflejar las capacidades de transpilación y la compatibilidad con Python y JavaScript.
- **Ejemplos de Código y Nuevas Estructuras**: Incluye ejemplos con el uso de estructuras avanzadas como clases y diccionarios en el lenguaje Cobra.

Si deseas agregar o modificar algo, házmelo saber.
