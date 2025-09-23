# Guía básica de Cobra

Este documento presenta un recorrido introductorio por el lenguaje Cobra con veinte ejemplos sencillos.

## Descargas

Puedes obtener binarios precompilados desde la sección de [Releases](https://github.com/Alphonsus411/pCobra/releases).

| Versión | Plataforma | Enlace |
| --- | --- | --- |
| 10.0.9 | Linux x86_64 | [cobra-linux](https://github.com/Alphonsus411/pCobra/releases/download/v10.0.9/cobra-linux) |
| 10.0.9 | Windows x86_64 | [cobra.exe](https://github.com/Alphonsus411/pCobra/releases/download/v10.0.9/cobra.exe) |
| 10.0.9 | macOS arm64 | [cobra-macos](https://github.com/Alphonsus411/pCobra/releases/download/v10.0.9/cobra-macos) |

Para verificar la integridad del archivo descargado calcula su hash SHA256 y compáralo con el valor publicado:

```bash
sha256sum cobra-linux
```

En Windows ejecuta:

```powershell
CertUtil -hashfile cobra.exe SHA256
```

## Ejecución y transpilación

Para ejecutar un archivo Cobra desde la línea de comandos:

```bash
cobra archivo.co
```

También puedes transpilar el programa a otros lenguajes usando la opción `--to`:

```bash
cobra archivo.co --to python
```

### Ejecución en GitHub Codespaces

1. En la página del repositorio en GitHub pulsa **Code** y luego la pestaña **Codespaces**.
2. Selecciona **Create codespace on work** (o la rama por defecto del repositorio) para lanzar un entorno basado en el contenedor de desarrollo.
3. Durante el arranque se instalarán las dependencias de `requirements-dev.txt` y se configurará la CLI de Cobra.
4. El archivo `examples/main.cobra` se abrirá automáticamente y se transpilará gracias a la tarea `Transpilar ejemplo`.

### Ejecución en Replit

1. Abre [Replit](https://replit.com/) e importa este repositorio desde GitHub.
2. Al cargarse el entorno, se instalarán las dependencias indicadas en `requirements.txt` gracias al archivo `replit.nix`.
3. El archivo `.replit` ya define el comando de ejecución `python -m cobra examples/replit/main.cobra`.
4. Presiona **Run** para ejecutar el ejemplo inicial ubicado en `examples/replit/main.cobra`.

### Ejecución en Binder

1. Haz clic en el badge de Binder del README o visita [este enlace](https://mybinder.org/v2/gh/Alphonsus411/pCobra/HEAD?labpath=notebooks/playground.ipynb).
2. Espera a que se construya el entorno; puede tardar unos minutos.
3. Cuando se abra JupyterLab, abre el cuaderno `notebooks/playground.ipynb` si no se abrió automáticamente.
4. Ejecuta las celdas una a una para transpilar el programa de Cobra a Python y ver el resultado.

### Edición y transpile en tiempo real

![Edición y transpile en tiempo real](data:image/gif;base64,R0lGODlh4AHwAIcAAP////7+/v39/fz8/Pv7+/r6+vn5+fj4+Pf39/b29vT09PPz8/Ly8vHx8fDw8O/v7+7u7u3t7evr6+rq6unp6ejo6Ofn5+bm5uXl5eTk5OPj4+Li4uHh4eDg4N7e3t3d3dzc3Nvb29ra2tfX19TU1NPT09LS0tHR0c3NzcvLy8nJycjIyMfHx8bGxsPDw8LCwsHBwb+/v76+vr29vbu7u7i4uLe3t7a2trS0tLKysrGxsa+vr66urq2traysrKmpqaioqKampqWlpaSkpKOjo6KioqGhoZ+fn56enp2dnZubm5qampeXl5aWlpWVlZKSkpGRkY6Ojo2NjYyMjIuLi4mJiYeHh4aGhoWFhYSEhIODg4GBgX9/f35+fn19fXh4eHd3d3Z2dnR0dGhoaGNjY2FhYWBgYF9fX15eXl1dXVxcXFtbW1paWllZWVNTU1FRUVBQUE5OTk1NTUtLS0pKSklJSUhISEdHR0VFRUNDQ0JCQj8/Pz4+Pj09PTw8PDs7OzU1NTQ0NC8vLysrKyoqKiUlJSQkJCIiIiEhIR4eHhwcHBsbGxoaGhkZGRgYGBcXFxYWFhMTExISEg8PDw0NDQsLCwoKCgkJCQgICAcHBwYGBgMDAwEBAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH/C05FVFNDQVBFMi4wAwEAAAAh+QQAZAAAACwAAAAA4AHwAAAI/wABCBxIsKDBgwgTKlzIsKHDhxAjSpxIsaLFixgzatzIsaPHjyBDihxJsqTJkyhTqlzJsqXLlzBjypxJs6bNmzhz6tzJs6fPn0CDCh1KtKjRo0iTKl3KtKnTp1CjSp1KtarVq1izat3KtavXr2DDih1LtqzZs2jTql0rcBIAEk0EWrnolq3du3gV1h24l2LfvIADg4WwJk8fFQAqyPFzpq7bLpvwWKjTp44FAJPMQBEo4c0ePBQmV748SYyfPh4waybxZ1AUwbBjPyWzAgAHQQDUDAGwI1Pb32yKACiyBgCmGgPRBAGAZEzw4cUxAQFABI5x5GNeRGgku7t3o4r2iP83NEDRAQAELP3GDIDR+QOMAFQSMHCRAQADHLgHAB/ApfsHPCIffQwsEUYl3yWoYE+OIACAADAAAMl5BlyynluNvBdfX46cJ1CG/MVXyQD8JcIeAHcsoQElC7boIk1uLIeDHQDA8QMAQGCyHiUCsLHbEGycuAAAcdyoxBc+AgAkAJnkQN0ZJ0biQAiavGjllSttYAcfenwAgAd99AGGYwLRMQcGdvRhxwUn4gEACHvwIccDaKrJ5iRn9CHHBCd6QUgbE2Ip6KCEFmrooYgmquiijDbq6KOQRirppJRWaumlmGaq6aacdurpp6CGKuqopJZq6qmopqrqqqy26uqrsMb/KuustNZq66245qrrrrz26uuvwAY7EQ4FaFTADcImCxFcFDGbkLMEVRAkZm719dd6BU0yCRsVKOttTVgI0Va1BF17YraTDHHFt+wi5FgZhzCxBiKvYWYaaqpt9m6889brmGYA4AsAIICcy55olrHHmmsCEQwCH+1GXK5AmazAAScqdMCdcdNVd916FV+c8cZ1HSfQIyROzBcAzxHHXnbbEUSAIxLXXNclJGZC380ACjjfejgzufN6PwMgiUGXiCeehfv151aBBxZ0dM0Rk3liXSOWeK7VXGNbCAPZTgyi0yiqyOJADRRCddUXguwkEVDu1fXV2KbRQtgrJ7mkW1JS/0lQC2ms3e7cjuW559Zt032uDVzg/VudawIQyBV+AuohAF0gJ/jmK28UABvFZlSAGpyXbrDpqKeu+uqst+7667DHLvvstNdu++2456777rz37vvvwAcv/PDEF2/88cgnr/zyzDfv/PPQRy/99NRXb/312Gev/fbcd+/99+CHL/745Jdv/vnop6/++uy37/778Mcv//z012///fjnr//+/Pfv//8ADKAAB0jA8s1lAikQiAsiMpcCUqqBA4GgQyToQEMhoAdGQEIGAKCAICBhBw2cSwy2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)

Los ejemplos de **Hello World** se encuentran en la carpeta [`examples/hello_world`](../examples/hello_world) con un subdirectorio por lenguaje. En esa misma carpeta hay un `README.md` que muestra cómo transpilar cada archivo `.co` a su lenguaje destino y contiene los resultados pre-generados. Algunos de ellos son:

- [ASM](../examples/hello_world/asm)
- [C](../examples/hello_world/c)
- [COBOL](../examples/hello_world/cobol)
- [C++](../examples/hello_world/cpp)
- [Fortran](../examples/hello_world/fortran)
- [Go](../examples/hello_world/go)
- [Java](../examples/hello_world/java)
- [JavaScript](../examples/hello_world/javascript)
- [Julia](../examples/hello_world/julia)
- [Kotlin](../examples/hello_world/kotlin)
- [LaTeX](../examples/hello_world/latex)
- [Matlab](../examples/hello_world/matlab)
- [Mojo](../examples/hello_world/mojo)
- [Pascal](../examples/hello_world/pascal)
- [Perl](../examples/hello_world/perl)
- [PHP](../examples/hello_world/php)
- [Python](../examples/hello_world/python)
- [R](../examples/hello_world/r)
- [Ruby](../examples/hello_world/ruby)
- [Rust](../examples/hello_world/rust)
- [Swift](../examples/hello_world/swift)
- [Visual Basic](../examples/hello_world/visualbasic)
- [WebAssembly](../examples/hello_world/wasm)


## 1. Hola mundo
```cobra
imprimir("Hola mundo")
```

## 2. Variables y operaciones
```cobra
x = 5
y = 3
imprimir x + y
```

## 3. Condicionales
```cobra
si x > y:
    imprimir "x es mayor"
sino si x == y:
    imprimir "son iguales"
sino:
    imprimir "y es mayor"
fin
```

Los operadores lógicos aceptan `y`, `o` y `no` como alias de `&&`, `||` y `!` respectivamente.

### Sentencia `garantia`

Cuando una condición debe cumplirse antes de continuar, la palabra clave `garantia`
proporciona una verificación temprana. Si la condición es falsa se ejecuta el
bloque `sino`, que debe terminar la ejecución con `retorno`, `lanzar`,
`continuar` o una acción equivalente, y la ejecución normal sigue en el bloque
principal. También es posible usar el alias `guard`.

```cobra
garantia entrada is not None:
    procesar(entrada)
sino:
    retorno Error("Falta la entrada")
fin
```

Esta estructura se transpila como un `if not condicion` en lenguajes como
Python, JavaScript o C++, lo que facilita patrones de salida temprana.

## 4. Bucle mientras
```cobra
contador = 0
mientras contador < 3:
    imprimir contador
    contador = contador + 1
fin
```

## 5. Bucle para
```cobra
para i en [1, 2, 3]:
    imprimir i
fin
```

## 6. Funciones
```cobra
func cuadrado(n):
    regresar n * n
fin
imprimir cuadrado(4)
```

## 7. Listas
```cobra
numeros = [1, 2, 3]
imprimir longitud(numeros)
```

## 8. Diccionarios
```cobra
mapa = {"a": 1, "b": 2}
imprimir mapa["a"]
```

## 9. Lectura de archivos
```cobra
from archivo importar leer
contenido = leer("ejemplo.txt")
imprimir contenido
```

## 10. Escritura de archivos
```cobra
from archivo importar escribir
escribir("salida.txt", "datos")
```

## 11. Definición de clases
```cobra
clase Persona:
    metodo __init__(self, nombre):
        atributo self nombre = nombre
fin
```

También puedes usar alias descriptivos que se traducen automáticamente al
método especial correspondiente:

```cobra
clase Coleccion:
    metodo iterar(self):
        pasar
fin
```

En el código generado por los transpiladores se obtendrá `__iter__`, por lo que
el objeto funciona como iterable en los distintos backends. Si declaras dos
métodos que colisionan tras la traducción (por ejemplo, `inicializar` y
`__init__`), Cobra mostrará una advertencia durante el parseo.

### Decorador `@registro`

Para clases que solo almacenan datos puedes utilizar `@registro`. Cobra genera
automáticamente los métodos especiales de inicialización, representación y
comparación en cada backend de destino.

```cobra
@registro
clase Persona:
    var nombre = ""
    var edad = 0
fin
```

El constructor acepta los campos declarados (utilizando los valores asignados
como parámetros opcionales), `toString`/`__repr__` devuelve una cadena con los
atributos y `equals`/`__eq__` compara instancia a instancia.

## 12. Herencia múltiple
```cobra
clase Volador:
    metodo mover(self):
        imprimir "vuelo"
    fin
fin

clase Nadador:
    metodo mover(self):
        imprimir "nado"
    fin
fin

clase Pato(Volador, Nadador):
    metodo mover(self):
        imprimir "camino"
    fin
fin

p = Pato()
p.mover()
```

El intérprete busca el método `mover` primero en `Pato`. Si no existe, recorre `Volador` y luego `Nadador` siguiendo el orden de las bases.

## 13. Creación de objetos
```cobra
p = Persona("Eva")
```

## 14. Uso de `metodo`
```cobra
clase Animal:
    metodo sonido(self):
        imprimir "???"
    fin
fin
```

## 15. Uso de `atributo`
```cobra
p = Persona("Luis")
imprimir atributo p nombre
```

## 16. Importar módulos
```cobra
import fecha
imprimir(fecha.hoy())
```

## 17. Manejo de errores
```cobra
intentar:
    abrir("no_existe.txt")
capturar ErrorComoE:
    imprimir("fallo")
fin
```

## 18. Expresiones lógicas
La biblioteca estándar ofrece puertas lógicas listas para usar. Se pueden combinar para expresar reglas complejas sin escribir expresiones manuales.

```cobra
imprimir conjuncion(True, False)      # False
imprimir disyuncion(False, False)     # False
imprimir xor(True, False)             # True cuando solo uno es verdadero
imprimir implicacion(True, False)     # False porque el antecedente se cumple pero el consecuente no
imprimir equivalencia(True, True)     # True cuando ambos valores coinciden
imprimir nand(True, True)             # False, negación de la conjunción
```

## 19. Comprensión de listas
```cobra
cuadrados = [x * x para x en [1,2,3]]
```

## 20. Uso de la API `util`
```cobra
from util importar es_vacio
imprimir es_vacio([])
```

## 21. Programa principal
```cobra
func principal():
    imprimir "Listo"
fin
```

## 22. Funciones asincrónicas
```cobra
asincronico func saluda():
    imprimir 1
fin

asincronico func principal():
    esperar saluda()
fin

esperar principal()
```

Además de funciones, Cobra permite trabajar con contextos y bucles asíncronos.

```cobra
asincronico con abrir_recurso() como recurso:
    esperar recurso.procesar()
fin

asincronico para elemento in flujo_asincronico:
    imprimir elemento
fin
```

Para coordinar varias tareas en paralelo puedes usar los helpers del módulo
``standard_library.asincrono``:

```cobra
from standard_library.asincrono importar esperar_todo

asincronico func principal():
    resultados = esperar esperar_todo(tarea_a(), tarea_b())
    imprimir resultados
fin
```

## 23. Decoradores
```cobra
@mi_decorador
func saluda():
    imprimir "Hola"
fin
```

## 24. Manejo de excepciones
```cobra
intentar:
    abrir("noexiste.txt")
capturar e:
    imprimir "Error:" + e
fin
```

## 25. Suma de matrices
```cobra
func sumar_matriz():
    var a11 = 1
    var a12 = 2
    var a21 = 3
    var a22 = 4

    var b11 = 5
    var b12 = 6
    var b21 = 7
    var b22 = 8

    imprimir a11 + b11
    imprimir a12 + b12
    imprimir a21 + b21
    imprimir a22 + b22
fin

sumar_matriz()
```

## 26. Factorial recursivo
```cobra
func factorial(n):
    si n <= 1:
        retorno 1
    sino:
        retorno n * factorial(n - 1)
    fin
fin

imprimir factorial(5)
```

## 27. Comando verify
El subcomando `cobra verificar` (`cobra verify`) comprueba que un programa
genere la misma salida en distintos lenguajes.

## 28. Enumeraciones
```cobra
enum Color:
    ROJO, VERDE, AZUL
fin
```

La expresión `coincidir` permite desempaquetar enums y otras estructuras de
forma declarativa. Cada brazo se inicia con `cuando` y utiliza `=>` para
indicar el resultado.

```cobra
var descripcion = coincidir color:
    cuando Color.ROJO => "caliente"
    cuando Color.AZUL => "frío"
    sino => "neutro"
fin
```

Si se omite `sino`, Cobra puede verificar opcionalmente que todos los miembros
de un `enum` estén cubiertos antes de la transpilación.

## 29. Entrada y salida de datos tabulares
```cobra
import standard_library.datos as datos

var ventas = datos.leer_csv('datos/ventas.csv', separador=';')
var ventas_limpias = datos.filtrar(ventas, lambda fila: fila['monto'] != None)

datos.escribir_csv(
    ventas_limpias,
    'salida/ventas_filtradas.csv',
    separador=';',
)

datos.escribir_json(
    ventas_limpias,
    'salida/ventas.jsonl',
    lineas=True,
    aniadir=True,
)
```

Las funciones de `standard_library.datos` crean directorios intermedios cuando es necesario, limpian los valores especiales de `NaN`
antes de serializar y permiten anexar nuevos registros sin reescribir archivos completos.

### Ejemplo: limpiar texto y detectar palíndromos

```cobra
import pcobra.corelibs as core
import standard_library.texto as texto

var titulo = core.titulo("crónicas de cobra")
imprimir(titulo)  # 'Crónicas De Cobra'

var limpio = core.quitar_espacios("  hola\t mundo \n")
imprimir(limpio)  # 'hola mundo'

imprimir(texto.quitar_acentos("Canción"))  # 'Cancion'
imprimir(texto.es_palindromo("Sé verlas al revés"))  # True

intentar:
    texto.codificar("Señal", encoding="ascii")
capturar error:
    imprimir("falló la codificación:", error)
fin

var datos = texto.codificar("hola€", encoding="ascii", errores="ignore")
imprimir(texto.decodificar(datos, encoding="ascii"))  # 'hola'
```

Este fragmento muestra cómo combinar las utilidades de `corelibs.texto` con los atajos de `standard_library.texto` para trabajar con Unicode sin perder legibilidad.

La misma tanda de utilidades incorporó `intercambiar_mayusculas` y `expandir_tabulaciones` para alternar casos y homogeneizar indentaciones mezcladas, además de `es_titulo` y `es_digito` que validan títulos con acentos y dígitos Unicode sin complicaciones.

### Ejemplo: recopilar datos con la interfaz enriquecida

Las nuevas utilidades de `standard_library.interfaz` permiten construir pequeños asistentes de consola sin manejar directamente las API de `rich`. El siguiente fragmento muestra una conversación típica en la terminal:

```python
from standard_library import (
    preguntar_texto,
    preguntar_opcion,
    preguntar_entero,
)

nombre = preguntar_texto("¿Cómo te llamas?", por_defecto="Ada")
lenguaje = preguntar_opcion(
    "¿Qué lenguaje prefieres?",
    ["Cobra", "Python", "Rust"],
    por_defecto="Cobra",
)
anios = preguntar_entero("¿Cuántos años llevas programando?", minimo=0)

print(f"{nombre} lleva {anios} años programando y hoy experimenta con {lenguaje}.")
```

En pantalla se muestran las opciones formateadas por `rich` y se reaprovecha el estilo de colores de Cobra. Cada pregunta valida automáticamente el tipo de entrada y guía a la persona usuaria con mensajes descriptivos.

## 30. Atajos numéricos de la biblioteca estándar

Las utilidades numéricas ofrecen envoltorios con nombres en español para cálculos frecuentes sin sacrificar precisión.

```python
from standard_library import (
    absoluto,
    redondear,
    redondear_arriba,
    redondear_abajo,
    potencia,
    dividir_entero,
    resto_division,
    limitar,
    signo,
)

print(absoluto(-8))               # 8
print(redondear(2.5))             # 2 → redondeo al par más cercano
print(redondear_arriba(-1.2))     # -1
print(redondear_abajo(1.8))       # 1
print(potencia(9, 0.5))           # 3.0
print(dividir_entero(-7, 2))      # -4
print(resto_division(-7, 2))      # 1
print(limitar(1.5, 0.0, 1.0))     # 1.0
print(signo(-3))                  # -1
```

`limitar` acota un valor a un intervalo cerrado, mientras que `signo` devuelve `-1`, `0` o `1` según la dirección del número recibido. Los redondeos delegan en las implementaciones de Python para conservar la semántica de banca y permitir especificar la cantidad de decimales deseada.

## 31. Aplazar acciones al salir de un bloque

```cobra
func procesar_archivo(ruta):
    recurso = abrir(ruta)
    aplazar recurso.cerrar()
    si recurso.tiene_datos():
        aplazar registrar_lectura(ruta)
        imprimir "procesando"
    fin
    imprimir "listo"
fin
```

La palabra clave `aplazar` registra una llamada para que se ejecute cuando se abandona el bloque actual. Resulta útil para liberar recursos o garantizar tareas de limpieza incluso si el flujo termina con un `retorno`, una excepción o un `romper`. Cobra ejecuta las acciones diferidas en orden inverso al de su registro, emulando `defer` en Go, un bloque `try/finally` en Python o una guardia RAII en Rust.
