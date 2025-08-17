# Manual del Lenguaje Cobra

Versión 10.0.9

Este manual presenta en español los conceptos básicos para programar en Cobra. Se organiza en tareas que puedes seguir paso a paso.

## 1. Preparación del entorno

1. Clona el repositorio y entra en el directorio `pCobra`.
2. Crea y activa un entorno virtual de **Python 3.8 o superior**.
3. Instala las dependencias con `pip install -r requirements-dev.txt`.
   Aseg\u00farate tambi\u00e9n de tener disponible la herramienta `cbindgen`:

   ```bash
   cargo install cbindgen
   ```
4. Instala la herramienta de forma editable con `pip install -e .`.

   Puedes usar ``pip install -e .[dev]`` para incluir los extras de desarrollo.

### Instalación con pipx

Puedes instalar Cobra utilizando [pipx](https://pypa.github.io/pipx/), una herramienta que permite ejecutar aplicaciones de Python aisladas y requiere Python 3.8 o superior.

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
imprimir(valor_inexistente)  # Variable no definida
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
[`src/cobra/transpilers/transpiler`](src/cobra/transpilers/transpiler)
de la siguiente forma:

```python
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.core import Parser

codigo = "imprimir('hola')"
parser = Parser(codigo)
arbol = parser.parsear()
print(TranspiladorPython().generate_code(arbol))
```

### Guías rápidas de transpilación entre lenguajes

Convierte programas entre distintos lenguajes usando la CLI:

- **De Cobra a C**

  ```bash
  cobra compilar hola.co --tipo c
  ```

- **De Python a JavaScript**

  ```bash
  cobra transpilar-inverso ejemplo.py --origen=python --destino=js
  ```

- **De COBOL a Python**

  ```bash
  cobra transpilar-inverso reporte.cob --origen=cobol --destino=python
  ```

### Transpiladores disponibles

La carpeta [`examples/hello_world`](examples/hello_world) incluye ejemplos de "Hello World" para cada generador, junto con un `README.md` que documenta los comandos para obtener cada salida y los resultados pre-generados:

- **ASM** – [hola.asm](examples/hello_world/asm/hola.asm)
- **C** – [hola.c](examples/hello_world/c/hola.c)
- **COBOL** – [hola.cob](examples/hello_world/cobol/hola.cob)
- **C++** – [hola.cpp](examples/hello_world/cpp/hola.cpp)
- **Fortran** – [hola.f90](examples/hello_world/fortran/hola.f90)
- **Go** – [hola.go](examples/hello_world/go/hola.go)
- **Java** – [Hola.java](examples/hello_world/java/Hola.java)
- **JavaScript** – [hola.js](examples/hello_world/javascript/hola.js)
- **Julia** – [hola.jl](examples/hello_world/julia/hola.jl)
- **Kotlin** – [hola.kt](examples/hello_world/kotlin/hola.kt)
- **LaTeX** – [hola.tex](examples/hello_world/latex/hola.tex)
- **Matlab** – [hola.m](examples/hello_world/matlab/hola.m)
- **Mojo** – [hola.mojo](examples/hello_world/mojo/hola.mojo)
- **Pascal** – [hola.pas](examples/hello_world/pascal/hola.pas)
- **Perl** – [hola.pl](examples/hello_world/perl/hola.pl)
- **PHP** – [hola.php](examples/hello_world/php/hola.php)
- **Python** – [hola.py](examples/hello_world/python/hola.py)
- **R** – [hola.r](examples/hello_world/r/hola.r)
- **Ruby** – [hola.rb](examples/hello_world/ruby/hola.rb)
- **Rust** – [hola.rs](examples/hello_world/rust/hola.rs)
- **Swift** – [hola.swift](examples/hello_world/swift/hola.swift)
- **Visual Basic** – [Hola.vb](examples/hello_world/visualbasic/Hola.vb)
- **WebAssembly** – [hola.wat](examples/hello_world/wasm/hola.wat)

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
El estado se guarda en `qualia_state.json` para conservar la información entre
sesiones.

Cada vez que ejecutes o transpilas un programa se actualiza la base de
conocimiento. Puedes consultarla con:

```bash
cobra qualia mostrar
```

Si deseas empezar de cero ejecuta:

```bash
cobra qualia reiniciar
```

En el modo interactivo escribe `sugerencias` para obtener las recomendaciones
actuales o bien `%sugerencias` en Jupyter. Las propuestas se vuelven más
detalladas a medida que Qualia aprende de tu código.

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

## 15. Funciones del sistema

La biblioteca estándar expone `corelibs.sistema.ejecutar` para lanzar
procesos del sistema. Por motivos de seguridad es **obligatorio**
proporcionar una lista blanca de ejecutables permitidos mediante el
parámetro ``permitidos`` o definiendo la variable de entorno
``COBRA_EJECUTAR_PERMITIDOS`` separada por ``os.pathsep``. La lista se
captura al importar el módulo, por lo que modificar la variable de
entorno después no surte efecto. Invocar la función sin esta
configuración producirá un ``ValueError``.

