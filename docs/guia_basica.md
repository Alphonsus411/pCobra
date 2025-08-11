# Guía básica de Cobra

Este documento presenta un recorrido introductorio por el lenguaje Cobra con veinte ejemplos sencillos.

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
2. Selecciona **Create codespace on main** para lanzar un entorno basado en el contenedor de desarrollo.
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
sino:
    imprimir "y es mayor"
fin
```

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

## 12. Creación de objetos
```cobra
p = Persona("Eva")
```

## 13. Uso de `metodo`
```cobra
clase Animal:
    metodo sonido(self):
        imprimir "???"
    fin
fin
```

## 14. Uso de `atributo`
```cobra
p = Persona("Luis")
imprimir atributo p nombre
```

## 15. Importar módulos
```cobra
import fecha
imprimir(fecha.hoy())
```

## 16. Manejo de errores
```cobra
intentar:
    abrir("no_existe.txt")
capturar ErrorComoE:
    imprimir("fallo")
fin
```

## 17. Expresiones lógicas
```cobra
imprimir conjuncion(True, False)
```

## 18. Comprensión de listas
```cobra
cuadrados = [x * x para x en [1,2,3]]
```

## 19. Uso de la API `util`
```cobra
from util importar es_vacio
imprimir es_vacio([])
```

## 20. Programa principal
```cobra
func principal():
    imprimir "Listo"
fin
```

## 21. Funciones asincrónicas
```cobra
asincronico func saluda():
    imprimir 1
fin

asincronico func principal():
    esperar saluda()
fin

esperar principal()
```

## 22. Decoradores
```cobra
@mi_decorador
func saluda():
    imprimir "Hola"
fin
```

## 23. Manejo de excepciones
```cobra
intentar:
    abrir("noexiste.txt")
capturar e:
    imprimir "Error:" + e
fin
```

## 24. Suma de matrices
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

## 25. Factorial recursivo
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

## 26. Comando verify
El subcomando `cobra verificar` (`cobra verify`) comprueba que un programa
genere la misma salida en distintos lenguajes.

## 27. Enumeraciones
```cobra
enum Color:
    ROJO, VERDE, AZUL
fin
```
