# Proyecto Cobra

Cobra es un lenguaje de programación diseñado en español, con un enfoque en la creación de herramientas, simulaciones y análisis en áreas como biología, computación y astrofísica. Este proyecto incluye un lexer y un parser robusto, que permite la interpretación y ejecución de un subconjunto del lenguaje definido.

## Tabla de Contenidos

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Instalación](#instalación)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Características Principales](#características-principales)
- [Uso](#uso)
- [Pruebas](#pruebas)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)

## Descripción del Proyecto

Cobra está diseñado para facilitar la programación en español, permitiendo que los desarrolladores utilicen un lenguaje más accesible para aquellos que no están familiarizados con el inglés. A través de su lexer y parser, Cobra puede analizar y ejecutar código, manejando variables, funciones y estructuras de control, lo que permite una amplia gama de aplicaciones.

## Instalación

Para instalar el proyecto, sigue estos pasos:

1. Clona el repositorio en tu máquina local:

   ```bash
   git clone https://github.com/tu_usuario/Cobra.git
   ````
   
2. Accede al directorio del proyecto:

````bash
cd Cobra
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

- **Lexer y Parser**: Implementación de un lexer para la tokenización del código fuente y un parser para la construcción de un árbol de sintaxis abstracta (AST).
- **Manejo de Declaraciones**: Soporte para declaraciones de variables, holobits, funciones y estructuras de control como condicionales y bucles.
- **Manejo de Errores**: El sistema captura y reporta errores de sintaxis, facilitando la depuración.
- **Visualización**: Salida detallada de tokens y errores de sintaxis para facilitar el desarrollo y la depuración.
- **Soporte para Llamadas a Funciones**: Implementación de un sistema para manejar argumentos en llamadas a funciones.

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

# Ejecutar el parser
arbol = parser.parsear()
print(arbol)
````

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

Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo LICENSE.


### Notas

- **Descripciones Detalladas**: Se han agregado secciones que explican de manera más completa qué hace el proyecto y cómo usarlo.
- **Ejemplos de Código**: Se ha incluido un ejemplo práctico que ilustra cómo usar el lexer y el parser.
- **Contribuciones**: Se ha dejado claro cómo otros pueden contribuir al proyecto.

Si deseas agregar o modificar algo, házmelo saber.
