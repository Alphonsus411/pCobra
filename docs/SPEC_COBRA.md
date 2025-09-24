# Especificación del Lenguaje Cobra

## Introducción
Cobra es un lenguaje de programación en español. Está orientado a la creación de herramientas, simulaciones y análisis en áreas como biología, computación y astrofísica. El proyecto incluye un lexer, un parser y transpiladores a múltiples lenguajes como Python, JavaScript, C++, Go o Rust.

Para visualizar de manera esquemática el proceso completo de compilación y la estructura general del AST, consulta los diagramas de `docs/flujo_compilacion.md` y `docs/diagrama_ast.md`.

## Gramática EBNF
```ebnf
?start: statement*

?statement: asignacion
          | funcion
          | clase
          | bucle_mientras
          | bucle_para
          | condicional
          | garantia
          | importacion
          | usar
          | macro
          | impresion
          | retorno
          | hilo
          | llamada
          | switch
          | try_catch
          | expr

asignacion: ("var"|"variable")? IDENTIFICADOR "=" expr
funcion: "func" IDENTIFICADOR "(" parametros? ")" ":" cuerpo "fin"
clase: ("clase"|"estructura"|"registro") IDENTIFICADOR ":" cuerpo "fin"
bucle_mientras: "mientras" expr ":" cuerpo "fin"
bucle_para: "para" IDENTIFICADOR "in" expr ":" cuerpo "fin"
condicional: "si" expr ":" cuerpo (("sino si"|"elseif") expr ":" cuerpo)* ("sino" ":" cuerpo)? "fin"
garantia: ("garantia"|"guard") expr ":" cuerpo "sino" ":" cuerpo "fin"
importacion: "import" CADENA
usar: "usar" CADENA
macro: "macro" IDENTIFICADOR "{" statement* "}"
impresion: "imprimir" "(" argumentos? ")"
retorno: "retorno" expr
hilo: "hilo" llamada
switch: "switch" expr ":" case+ "fin"
case: ("case" expr ":" cuerpo)+
try_catch: ("try"|"intentar") ":" cuerpo ("catch"|"capturar") IDENTIFICADOR ":" cuerpo "fin"
llamada: IDENTIFICADOR "(" argumentos? ")"
cuerpo: statement*
parametros: IDENTIFICADOR ("," IDENTIFICADOR)*
argumentos: expr ("," expr)*
?expr: valor (operador valor)*
?valor: CADENA
      | ENTERO
      | FLOTANTE
      | IDENTIFICADOR
      | llamada
      | holobit
holobit: "holobit" "(" "[" [expr ("," expr)*] "]" ")"
operador: "+"|"-"|"*"|"/"|">="|"<="|">"|"<"|"=="|"!="|"&&"|"||"|"y"|"o"

CADENA: /"[^"\n]*"|'[^'\n]*'/
ENTERO: /[0-9]+/
FLOTANTE: /[0-9]+\.[0-9]+/
IDENTIFICADOR: /[^\W\d_][\w]*/

%ignore /\s+/
```
Cada regla define construcciones del lenguaje: por ejemplo `asignacion` utiliza `var` para crear variables, `funcion` agrupa parámetros y un cuerpo, y `try_catch` permite atrapar errores con `try` o `intentar` y `catch` o `capturar`.

## Tokens y palabras reservadas
El lexer de `src/pcobra/cobra/lexico/lexer.py` define todos los tokens. Las principales palabras clave son:
- `var`, `variable`, `func`, `metodo`, `atributo`
- `si`, `sino`, `sino si`/`elseif`, `garantia`/`guard`, `mientras`, `para`, `import`, `usar`, `macro`, `hilo`, `asincronico`
- `switch`, `case`, `clase`/`estructura`/`registro`, `enum`/`enumeracion`, `in`, `holobit`, `proyectar`, `transformar`, `graficar`
- `try`/`intentar`, `catch`/`capturar`, `throw`/`lanzar`
- `&&`/`y`, `||`/`o`, `!`/`no`
- `imprimir`, `yield`, `esperar`, `romper`, `continuar`, `pasar`, `afirmar`, `eliminar`,
  `global`, `nolocal`, `lambda`, `con`, `finalmente`, `desde`, `como`, `retorno`, `fin`, `hilo`

Las cascadas condicionales admiten la sintaxis compacta `sino si` (o su alias `elseif`), que el parser reescribe internamente como nodos anidados equivalentes a `sino: si ... fin`.

La sentencia `garantia` introduce un guard clause: evalúa la condición y, si es
falsa, ejecuta el bloque `sino`, el cual debe finalizar la ejecución actual
(`retorno`, `throw`/`lanzar`, `continuar` o `romper`). Tras superar la
verificación, el bloque principal continúa con el flujo normal.

Además existen tokens para operadores (`+`, `-`, `*`, `/`, `==`, `&&`/`y`, `||`/`o`, `!`/`no`, etc.), delimitadores como paréntesis, corchetes y llaves, y literales (`ENTERO`, `FLOTANTE`, `CADENA`, `BOOLEANO`).

## Variables y tipos básicos
```cobra
x = 10
nombre = "Ana"
lista = [1, 2, 3]
mapa = {"a": 1, "b": 2}
```

## Definición de funciones, clases y métodos
```cobra
func sumar(a, b):
    regresar a + b
fin

clase Persona:
    metodo __init__(self, nombre):
        atributo self nombre = nombre
    metodo saludar(self):
        imprimir "Hola", atributo self nombre
    fin
fin
```

Los métodos especiales admiten alias legibles que se transpilan automáticamente
al nombre mágico correspondiente. Los alias incorporados son:

| Alias        | Método generado |
|--------------|-----------------|
| `inicializar`| `__init__`      |
| `representar`| `__repr__`      |
| `iterar`     | `__iter__`      |
| `longitud`   | `__len__`       |
| `contener`   | `__contains__`  |
| `comparar`   | `__eq__`        |
| `ordenar`    | `__lt__`        |
| `entrar`     | `__enter__`     |
| `salir`      | `__exit__`      |

Si dos alias producen el mismo nombre dentro de una clase (por ejemplo,
`inicializar` y `__init__`), el parser conserva ambos nodos y emite una
advertencia de choque para facilitar la depuración.

Las clases pueden declararse con las palabras clave `clase`, `estructura` o
`registro`. Las enumeraciones aceptan `enum` o `enumeracion`. El parser trata
estos términos como sinónimos y registra una advertencia si en un mismo
archivo se mezclan varios alias, para favorecer un estilo consistente.

## Control de flujo
```cobra
si x > 0:
    imprimir "positivo"
sino si x == 0:
    imprimir "cero"
sino:
    imprimir "negativo"
fin

para var i en rango(5):
    imprimir(i)

mientras x < 5:
    imprimir(x)
    x += 1

switch valor:
case 1:
    imprimir "uno"
fin
```

## Módulos e importaciones
```cobra
importar utilidades
```

## Manejo de errores
```cobra
try:
    throw "problema"
catch e:
    imprimir(e)
fin
```
Las excepciones también pueden escribirse con `intentar`/`capturar` y `lanzar`.

## Otras construcciones
```cobra
var h = holobit([0.8, -0.5, 1.2])
hilo trabajo()

@temporizador
func saluda():
    imprimir('hola')
fin
```

## Reporte de errores
El intérprete define la excepción `ExcepcionCobra`. Al ejecutar un `throw` se lanza esta excepción y el bloque `try_catch` captura el valor mediante `catch` o `capturar`. Si se produce un error inesperado, el intérprete genera mensajes utilizando excepciones de Python.

## Ejemplos mínimos
Los ejemplos de `frontend/sintaxis.rst` muestran el uso básico del lenguaje: declaraciones con `var`, funciones `func`, condicionales `si`/`sino`, bucles `mientras` y `para`, holobits, importaciones, manejo de excepciones con `try`/`catch`, hilos y decoradores con `@`.

## Biblioteca estándar

El paquete `standard_library.numero` reexporta los atajos numéricos de
`pcobra.corelibs` con nombres idiomáticos en español. Entre ellos destacan
`signo`, que devuelve `-1`, `0` o `1` y preserva ceros con signo o `NaN` cuando
se trabaja con flotantes, y `limitar`, que valida que `minimo` no supere a
`maximo` y propaga `NaN` si alguno de los extremos no es un número válido.

```cobra
import standard_library.numero as numero

var direccion = numero.signo(-0.0)        # -0.0 conserva el signo del cero
var brillo = numero.limitar(1.5, 0.0, 1.0)  # 1.0: el valor queda dentro del rango
```

El módulo `standard_library.datos` usa `pandas` para trabajar con tablas desde Cobra y expone utilidades de lectura y escritura
que devuelven listas de diccionarios. Las funciones `leer_csv`/`leer_json` normalizan valores perdidos como `None`, mientras que
`escribir_csv` y `escribir_json` permiten controlar el separador, la codificación, anexar información y producir archivos en JSON
Lines sin duplicar encabezados.

```cobra
import standard_library.datos as datos

var registros = datos.leer_csv('datos/ventas.csv')
datos.escribir_csv(registros, 'salida/ventas.csv', separador=';')
datos.escribir_json(registros, 'salida/ventas.jsonl', lineas=True, aniadir=True)
```
