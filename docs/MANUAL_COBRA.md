# Manual del Lenguaje Cobra

Versión 10.0.9

Este manual presenta en español los conceptos básicos para programar en Cobra. Se organiza en tareas que puedes seguir paso a paso.

## 1. Preparación del entorno

1. Clona el repositorio y entra en el directorio `pCobra`.
2. Crea y activa un entorno virtual de **Python 3.9 o superior**.
3. Instala las dependencias con `./scripts/install_dev.sh`.
   Este script instala tanto las dependencias de ejecución como las de desarrollo.
   Aseg\u00farate tambi\u00e9n de tener disponible la herramienta `cbindgen`:

   ```bash
   cargo install cbindgen
   ```
4. Instala la herramienta de forma editable con `pip install -e .`.


### Instalación con pipx

Puedes instalar Cobra utilizando [pipx](https://pypa.github.io/pipx/), una herramienta que permite ejecutar aplicaciones de Python aisladas y requiere Python 3.9 o superior.

```bash
pipx install pcobra
```

También puedes instalar Cobra directamente desde PyPI con

```bash
pip install pcobra
```

## 2. Estructura básica de un programa

- Declara variables con `var`.
- Define funciones con `func nombre(parametros) :` y finaliza con `fin` si la función es multilinea.
- Puedes anteponer líneas con `@decorador` para aplicar decoradores a la función.
- Utiliza `imprimir` para mostrar datos en pantalla.
- El intérprete detecta y evita referencias circulares entre variables.

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

## 3. Clases y objetos

- Define una clase con `clase Nombre:` y finaliza con `fin`.
- Las clases pueden declarar atributos y métodos.

```cobra
clase Persona:
    var nombre = ''

    func saludar():
        imprimir('Hola ' + nombre)
    fin
fin

var juan = Persona()
juan.nombre = 'Juan'
juan.saludar()
```

**Herencia múltiple**

Cobra permite que una clase herede de varias bases listándolas entre paréntesis.
El intérprete resuelve los métodos de izquierda a derecha según el orden de las bases.

```cobra
clase Volador:
    func volar():
        imprimir('vuelo')
    fin
fin

clase Nadador:
    func nadar():
        imprimir('nado')
    fin
fin

clase Pato(Volador, Nadador):
    fin

var p = Pato()
p.volar()
p.nadar()
```

## 4. Control de flujo

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

## 5. Manejo de errores

- `try` agrupa código que puede fallar. Su alias en español es `intentar`.
- `catch` intercepta las excepciones generadas; también puede escribirse `capturar`.
- `throw` lanza una excepción y admite el alias `lanzar`.
- `finally` ejecuta un bloque sin importar el resultado. Su equivalente en español es `finalmente`.

`ExcepcionCobra` es la excepción genérica del intérprete. Al lanzarse, la ejecución se detiene y el error se propaga a través de las funciones llamadoras hasta que un bloque `catch`/`capturar` lo maneja. Si nadie lo controla, el programa termina mostrando el mensaje de error.

Ejemplo sin alias:

```cobra
try:
    throw ExcepcionCobra('falló')
catch ExcepcionCobra:
    imprimir('error controlado')
finally:
    imprimir('siempre se ejecuta')
```

Ejemplo con alias en español:

```cobra
intentar:
    lanzar ExcepcionCobra('falló')
capturar ExcepcionCobra:
    imprimir('error controlado')
finalmente:
    imprimir('siempre se ejecuta')
```

## 6. Trabajar con módulos

- Usa `import` para cargar archivos `.co` o módulos nativos.
- Los módulos nativos ofrecen funciones de E/S y estructuras de datos.

```cobra
import 'modulo.co'
imprimir(saludo)
```

## 7. Paquetes Cobra

- Agrupa varios módulos en un archivo con manifest ``cobra.pkg``.
- Crea un paquete con ``cobra paquete crear carpeta paquete.cobra``.
- Instálalo posteriormente con ``cobra paquete instalar paquete.cobra``.
- Los archivos ``.cobra`` corresponden a paquetes completos, mientras que los scripts usan la extensión ``.co``.

## 8. Macros

Permiten reutilizar fragmentos de código mediante la directiva `macro`.

```cobra
macro saluda { imprimir(1) }
saluda()
```
## 9. Concurrencia

- Ejecuta funciones en paralelo con la palabra clave `hilo`.

```cobra
func tarea():
    imprimir('trabajo')
fin

hilo tarea()
imprimir('principal')
```

## 10. Funciones asincrónicas

- Declara funciones asíncronas con `asincronico func`.
- Usa `esperar` para aguardar su resultado.

```cobra
asincronico func tarea():
    esperar 1
    imprimir('listo')
fin

func principal():
    esperar tarea()
    imprimir('fin')
fin
```

## 11. Transpilación y ejecución

- Compila a Python, JavaScript, ensamblador, Rust o C++ con `cobra compilar archivo.co --tipo python`.
- Ejecuta directamente con `cobra ejecutar archivo.co`.

### Ejemplo de transpilación a Python

```bash
cobra compilar ejemplo.co --tipo python
```

Si prefieres usar las clases del proyecto, llama al módulo
[`src/pcobra/cobra/transpilers/transpiler`](src/pcobra/cobra/transpilers/transpiler)
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

## 12. Modo seguro

El modo seguro se encuentra activado por defecto y evita operaciones peligrosas
como `leer_archivo` o `hilo`. Para desactivarlo:

```bash
cobra ejecutar programa.co --no-seguro
```

## 13. Próximos pasos

Revisa la documentación en `docs/frontend` para profundizar en la arquitectura, validadores y más ejemplos.
También puedes consultar ejemplos prácticos en la carpeta `examples/casos_reales/` ubicada en la raíz del repositorio.

## 14. Novedades

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

## 15. Uso de Qualia

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

## 16. Bibliotecas compartidas con ctypes

Puedes cargar funciones escritas en C mediante ``cargar_funcion``. Solo
compila una biblioteca compartida y proporciona la ruta y el nombre de la
función:

```cobra
var triple = cargar_funcion('libtriple.so', 'triple')
imprimir(triple(3))
```

## 17. Perfilado de programas

Para analizar el rendimiento de un script utiliza `cobra profile`. Puedes guardar
el resultado en un archivo `.prof` y abrirlo con herramientas como `snakeviz`:

```bash
cobra profile ejemplo.co --output ejemplo.prof --ui snakeviz
```

Si no indicas `--ui`, se mostrará un resumen en la consola. `snakeviz` se instala junto con las dependencias de desarrollo.

## 18. Funciones del sistema

La biblioteca estándar expone `corelibs.sistema.ejecutar` para lanzar
procesos del sistema. Por motivos de seguridad es **obligatorio**
proporcionar una lista blanca de ejecutables permitidos mediante el
parámetro ``permitidos`` o definiendo la variable de entorno
``COBRA_EJECUTAR_PERMITIDOS`` separada por ``os.pathsep``. La lista se
captura al importar el módulo, por lo que modificar la variable de
entorno después no surte efecto. Invocar la función sin esta
configuración producirá un ``ValueError``.

## 19. Limitaciones de recursos en Windows

En sistemas Windows los límites de memoria y de CPU pueden no aplicarse
correctamente. Si Cobra no logra establecer las restricciones solicitadas
mostrará advertencias como:

```
No se pudo establecer el límite de memoria en Windows; el ajuste se omitirá.
No se pudo establecer el límite de CPU en Windows; el ajuste se omitirá.
```

Para garantizar estos límites se recomienda ejecutar Cobra dentro de un
contenedor como Docker o bajo WSL2, donde sí es posible aplicar las
restricciones de recursos.

## 20. Alcance y utilidades

El lenguaje ofrece palabras clave para controlar el alcance de las
variables y utilidades comunes al escribir programas.

- `global` permite modificar una variable definida en el módulo.
- `nolocal` accede a variables de un contexto externo distinto al
  global.
- `afirmar` verifica condiciones y detiene la ejecución si no se cumple.
- `eliminar` borra nombres o elementos de estructuras.

```cobra
var contador = 0

func incrementar():
    global contador
    contador += 1
fin

func crear():
    var total = 0

    func sumar():
        nolocal total
        total += 1
    fin

    sumar()
    afirmar(total > 0, 'Total debe ser positivo')
fin

var numeros = [1, 2, 3]
eliminar numeros[1]
eliminar contador
```

**Buenas prácticas**

- Emplea `global` y `nolocal` con moderación para reducir efectos
  secundarios y favorecer un diseño modular.
- Usa `afirmar` para documentar invariantes del código; ayuda a detectar
  errores temprano.
- `eliminar` sirve para liberar recursos o mantener limpio el espacio de
  nombres; evita su abuso para que el flujo del programa sea predecible.

## 21. Construcciones avanzadas

### Lambda

`lambda` define funciones an\u00f3nimas de una sola expresi\u00f3n. Se
emplea para crear callbacks r\u00e1pidos o para pasar l\u00f3gica a
funciones de orden superior como `map` o `filter`.

```cobra
var duplicar = lambda x: x * 2
var datos = [1, 2, 3]
var resultado = map(duplicar, datos)
```

Suelen combinarse con otras estructuras como `si` o `mientras` para
realizar operaciones en l\u00ednea sin definir funciones completas.

### Contextos con `con`/`with`

`con` (o `with` en ingl\u00e9s) crea un contexto que garantiza liberar
recursos al finalizar el bloque `fin`, incluso cuando ocurre una
excepci\u00f3n.

```cobra
con abrir_archivo('datos.txt') como archivo:
    archivo.escribir('hola')
fin
```

Es habitual usarlo para manejar archivos, conexiones o bloqueos.
Puede anidarse con `try`, `si` o bucles para un control m\u00e1s fino del
flujo.

### Option `nombre = valor`

La construcci\u00f3n `option` declara valores opcionales que pueden o no
contener un dato. La sintaxis b\u00e1sica es:

```cobra
option resultado = obtener()
option sin_valor = None
```

Se usa para representar retornos que pueden estar ausentes. Puede
combinarse con `si` o `switch` para comprobar su contenido y con `con`
cuando la disponibilidad del recurso es condicional.


## 22. Manipulación de texto y Unicode

El módulo `pcobra.corelibs.texto` se amplió con herramientas inspiradas en `str` de Python y `String` de ECMAScript. Además de `mayusculas`, `minusculas`, `invertir` y `concatenar`, ahora dispones de:

- `capitalizar` y `titulo` para aplicar estilos de texto comunes.
- `quitar_espacios`, `dividir` y `unir` para recortar y recomponer cadenas de forma precisa, incluso con caracteres personalizados.
- `reemplazar`, `empieza_con`, `termina_con` e `incluye` para búsquedas y sustituciones expresivas.
- `rellenar_izquierda` y `rellenar_derecha` para completar cadenas con cualquier patrón.
- `normalizar_unicode` que acepta las formas `NFC`, `NFD`, `NFKC` y `NFKD` para trabajar con Unicode de forma predecible.

En la biblioteca estándar (`standard_library.texto`) se añadieron utilidades de mayor nivel como `quitar_acentos`, `normalizar_espacios`, `es_palindromo` y `es_anagrama`. Estas funciones combinan las primitivas anteriores para resolver tareas frecuentes como limpiar entrada de usuarios, validar palíndromos independientemente de acentos o comparar cadenas ignorando espacios.

```cobra
import pcobra.corelibs as core
import standard_library.texto as texto

imprimir(core.titulo("guía de cobra"))          # 'Guía De Cobra'
imprimir(core.dividir("uno   dos\ttres"))       # ['uno', 'dos', 'tres']
imprimir(texto.quitar_acentos("Canción"))       # 'Cancion'
imprimir(texto.es_palindromo("Sé verlas al revés"))  # True
```

Estas herramientas están disponibles al transpirar tanto a Python como a JavaScript y respetan los casos borde como cadenas vacías o entradas Unicode combinadas.

## 23. Operaciones con colecciones

El módulo `pcobra.corelibs.coleccion` ahora ofrece funciones pensadas para transformar y analizar listas sin perder el orden de los elementos ni sacrificar seguridad de tipos. Las más destacadas son:

- `mapear`, `filtrar` y `reducir` para aplicar funciones, quedarte con elementos relevantes y sintetizar resultados.
- `encontrar` y `tomar` para acceder rápidamente a elementos puntuales.
- `aplanar`, `zip_listas` y `mezclar` para reorganizar la información manteniendo copias y sin modificar la entrada original.
- `agrupar_por` y `particionar` para clasificar datos de acuerdo a una clave o predicado.

En paralelo, `standard_library.lista` incorpora capas de mayor nivel:

- `mapear_seguro` captura las excepciones durante la transformación y te indica qué elementos fallaron.
- `ventanas` crea ventanas deslizantes de cualquier tamaño y paso.
- `chunk` divide una secuencia en bloques regulares con la opción de descartar los incompletos.

### Receta paso a paso

El siguiente ejemplo encadena todas las piezas anteriores para procesar una lista de registros de sensores:

```cobra
import pcobra.corelibs as core
import standard_library.lista as lista

var lecturas = [
    {"sensor": "temperatura", "valor": 18},
    {"sensor": "temperatura", "valor": 23},
    {"sensor": "humedad", "valor": None},
    {"sensor": "temperatura", "valor": 21},
]

# 1. Nos quedamos con valores numéricos y los convertimos a grados Fahrenheit.
var depurados, errores = lista.mapear_seguro(
    lecturas,
    lambda item: item["valor"] * 9 / 5 + 32,
    valor_por_defecto=None,
)

# 2. Filtramos las lecturas válidas y agrupamos por sensor.
var validas = core.filtrar(depurados, lambda valor: valor != None)
var grupos = core.agrupar_por(lecturas, "sensor")

# 3. Calculamos el promedio del sensor de temperatura.
var temperaturas = grupos["temperatura"]
var promedio_temperatura = core.promedio(
    core.mapear(
        core.filtrar(temperaturas, lambda item: item["valor"] != None),
        lambda item: item["valor"],
    )
)

# 4. Recorremos los datos en ventanas de dos en dos para detectar cambios bruscos.
var ventanas = lista.ventanas(validas, 2, paso=1)

# 5. Mezclamos las lecturas para probar un algoritmo aleatorio de manera reproducible.
var muestra = core.mezclar(validas, semilla=42)

imprimir(depurados)
imprimir(errores)
imprimir(promedio_temperatura)
imprimir(ventanas)
imprimir(muestra)
```

Cada paso mantiene el orden de entrada y devuelve nuevas listas, de modo que puedes reutilizar la variable original más adelante. `mezclar` acepta un parámetro `semilla` para producir barajados reproducibles en pruebas o demostraciones.

Las funciones están disponibles tanto al ejecutar Cobra directamente como al transpirar a Python o JavaScript: la semántica se conserva gracias a las implementaciones equivalentes en `core/nativos/coleccion.js`.

### Operaciones lógicas reutilizables

`pcobra.corelibs.logica` reúne operadores booleanos con validaciones explícitas de tipo. Las versiones de `standard_library.logica` reutilizan la misma implementación para ofrecer una API homogénea en cualquier backend.

- `conjuncion`, `disyuncion` y `negacion` cubren las puertas clásicas.
- `xor`, `nand`, `nor`, `implica` y `equivale` facilitan construir tablas de verdad completas.
- `xor_multiple` acepta un número arbitrario de argumentos y exige al menos dos valores.
- `todas` y `alguna` validan colecciones de booleanos antes de aplicar `all`/`any`.

Los parámetros no booleanos producen un `TypeError` descriptivo, lo cual ayuda a detectar errores lógicos tempranamente. Además, la versión en JavaScript (`core/nativos/logica.js`) replica la semántica para mantener el comportamiento al transpirar.

```cobra
import pcobra.corelibs.logica as logica
import standard_library.logica as logica_alto_nivel

imprimir(logica.xor(True, False))                 # True
imprimir(logica.implica(True, False))             # False
imprimir(logica_alto_nivel.xor_multiple(True, False, False))  # True

var sensores = [True, True, False]
imprimir(logica_alto_nivel.alguna(sensores))      # True

# Lanzan errores al recibir datos que no son booleanos
logica.todas([True, 1])  # -> TypeError
```

> **Recomendación:** al combinar `xor_multiple` con colecciones calculadas dinámicamente verifica previamente la longitud de la entrada para evitar el `ValueError` que se lanza cuando se proporcionan menos de dos argumentos.

## 24. Procesamiento de datos tabulares

El módulo `standard_library.datos` añade una capa ligera sobre `pandas` que permite trabajar con tablas desde Cobra sin exponerse a los detalles internos del `DataFrame`. Las funciones devuelven listas de diccionarios o diccionarios de listas, estructuras fáciles de manipular desde Cobra o al transpirar a Python.

- `leer_csv` y `leer_json` cargan archivos en disco y devuelven registros con valores `None` cuando la fuente contiene datos perdidos.
- `describir` calcula estadísticas básicas (`count`, `mean`, `std`, percentiles) para cada columna.
- `seleccionar_columnas` y `filtrar` permiten aislar subconjuntos antes de seguir procesando los datos.
- `agrupar_y_resumir` aplica agregaciones (`sum`, `mean`, funciones personalizadas) agrupando por columnas clave.
- `a_listas` y `de_listas` convierten entre lista de registros y diccionario de columnas, facilitando la interoperabilidad con librerías externas.

```cobra
usar pandas

ventas = pandas.leer_csv('ventas.csv')
ventas_limpias = pandas.filtrar(ventas, lambda fila: fila['monto'] != None)
resumen = pandas.agrupar_y_resumir(
    ventas_limpias,
    por=['region'],
    agregaciones={'monto': 'sum'}
)
columnas = pandas.a_listas(resumen)
imprimir(columnas['region'])
```

> **Diferencias entre backends:** las funciones de lectura y estadística solo están disponibles cuando el objetivo de ejecución es Python, ya que dependen de `pandas`. En JavaScript puedes seguir usando `seleccionar_columnas`, `filtrar`, `a_listas` y `de_listas`, pero las operaciones avanzadas dispararán un error explicando la limitación.
