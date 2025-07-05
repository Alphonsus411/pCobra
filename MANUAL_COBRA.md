# Manual del Lenguaje Cobra

Versión 6.0.0

Este manual presenta en español los conceptos básicos para programar en Cobra. Se organiza en tareas que puedes seguir paso a paso.

## 1. Preparación del entorno

1. Clona el repositorio y entra en el directorio `pCobra`.
2. Crea y activa un entorno virtual.
3. Instala las dependencias con `pip install -r requirements.txt`.
   Aseg\u00farate tambi\u00e9n de tener disponible la herramienta `cbindgen`:

   ```bash
   cargo install cbindgen
   ```
4. Instala la herramienta de forma editable con `pip install -e .`.

### Instalación con pipx

Puedes instalar Cobra utilizando [pipx](https://pypa.github.io/pipx/), una herramienta que permite ejecutar aplicaciones de Python aisladas y requiere Python 3.6 o superior.

```bash
pipx install cobra-lenguaje
```

También puedes instalar Cobra directamente desde PyPI con

```bash
pip install cobra-lenguaje
```

## 2. Estructura básica de un programa

- Declara variables con `var`.
- Define funciones con `func nombre(parametros) :` y finaliza con `fin` si la función es multilinea.
- Puedes anteponer líneas con `@decorador` para aplicar decoradores a la función.
- Utiliza `imprimir` para mostrar datos en pantalla.

```cobra
var mensaje = 'Hola Mundo'
imprimir(mensaje)
```

Ejemplo con decoradores y `yield`:

```cobra
@mi_decorador
func generador():
    yield 1
fin
```

## 3. Control de flujo

- Condicionales con `si`, `sino` y `fin` opcional.
- Bucles `mientras` y `para`.
- Selección múltiple con `switch` y `case`.

```cobra
var x = 0
mientras x < 3 :
    imprimir(x)
    x += 1
```

Ejemplo de `switch`:

```cobra
switch opcion:
    case 1:
        imprimir('uno')
    case 2:
        imprimir('dos')
    sino:
        imprimir('otro')
fin
```

## 4. Trabajar con módulos

- Usa `import` para cargar archivos `.co` o módulos nativos.
- Los módulos nativos ofrecen funciones de E/S y estructuras de datos.

```cobra
import 'modulo.co'
imprimir(saludo)
```

## 5. Paquetes Cobra

- Agrupa varios módulos en un archivo con manifest ``cobra.pkg``.
- Crea un paquete con ``cobra paquete crear carpeta paquete.cobra``.
- Instálalo posteriormente con ``cobra paquete instalar paquete.cobra``.
- Los archivos ``.cobra`` corresponden a paquetes completos, mientras que los scripts usan la extensión ``.co``.

## 6. Macros

Permiten reutilizar fragmentos de código mediante la directiva `macro`.

```cobra
macro saluda { imprimir(1) }
saluda()
```
## 7. Concurrencia

- Ejecuta funciones en paralelo con la palabra clave `hilo`.

```cobra
func tarea():
    imprimir('trabajo')
fin

hilo tarea()
imprimir('principal')
```

## 8. Transpilación y ejecución

- Compila a Python, JavaScript, ensamblador, Rust o C++ con `cobra compilar archivo.co --tipo python`.
- Ejecuta directamente con `cobra ejecutar archivo.co`.

### Ejemplo de transpilación a Python

```bash
cobra compilar ejemplo.co --tipo python
```

Si prefieres usar las clases del proyecto, llama al módulo
[`backend/src/cobra/transpilers/transpiler`](backend/src/cobra/transpilers/transpiler)
de la siguiente forma:

```python
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.parser.parser import Parser

codigo = "imprimir('hola')"
parser = Parser(codigo)
arbol = parser.parsear()
print(TranspiladorPython().generate_code(arbol))
```

### Características aún no soportadas

Herencia múltiple en clases.

## 9. Modo seguro

- Añade `--seguro` para evitar operaciones peligrosas como `leer_archivo` o `hilo`.

```bash
cobra ejecutar programa.co --seguro
```

## 10. Próximos pasos

Revisa la documentación en `frontend/docs` para profundizar en la arquitectura, validadores y más ejemplos.
También puedes consultar ejemplos prácticos en la carpeta `casos_reales/` ubicada en la raíz del repositorio.

## 11. Novedades

Se añadieron nuevas construcciones al lenguaje:

- `afirmar` para realizar comprobaciones.
- `eliminar` para borrar variables.
- `global` y `nolocal` para declarar alcance de nombres.
- `lambda` para funciones anónimas.
- `con` para manejar contextos con bloque `fin`.
- `finalmente` dentro de `try` para ejecutar código final.
- Palabras en español `intentar`, `capturar` y `lanzar` como alias de `try`, `catch` y `throw`.
- Importaciones `desde` ... `como` para alias de módulos.
- Nueva estructura `switch` con múltiples `case`.

## 12. Uso de Qualia

Qualia registra cada ejecución y genera sugerencias para mejorar tu código.
El estado se guarda en `qualia_state.json`. Puedes obtener las sugerencias
ejecutando `sugerencias` en el modo interactivo o escribiendo `%sugerencias`
en el kernel de Jupyter.

## 13. Bibliotecas compartidas con ctypes

Puedes cargar funciones escritas en C mediante ``cargar_funcion``. Solo
compila una biblioteca compartida y proporciona la ruta y el nombre de la
función:

```cobra
var triple = cargar_funcion('libtriple.so', 'triple')
imprimir(triple(3))
```

## 14. Perfilado de programas

Para analizar el rendimiento de un script utiliza `cobra profile`. Puedes guardar
el resultado en un archivo `.prof` y abrirlo con herramientas como `snakeviz`:

```bash
cobra profile ejemplo.co --output ejemplo.prof --ui snakeviz
```

Si no indicas `--ui`, se mostrará un resumen en la consola. Instala `snakeviz`
con:

```bash
pip install snakeviz
```

