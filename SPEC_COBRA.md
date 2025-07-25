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
clase: "clase" IDENTIFICADOR ":" cuerpo "fin"
bucle_mientras: "mientras" expr ":" cuerpo "fin"
bucle_para: "para" IDENTIFICADOR "in" expr ":" cuerpo "fin"
condicional: "si" expr ":" cuerpo ("sino" ":" cuerpo)? "fin"
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
operador: "+"|"-"|"*"|"/"|">="|"<="|">"|"<"|"=="|"!="|"&&"|"||"

CADENA: /"[^"\n]*"|'[^'\n]*'/
ENTERO: /[0-9]+/
FLOTANTE: /[0-9]+\.[0-9]+/
IDENTIFICADOR: /[^\W\d_][\w]*/

%ignore /\s+/
```
Cada regla define construcciones del lenguaje: por ejemplo `asignacion` utiliza `var` para crear variables, `funcion` agrupa parámetros y un cuerpo, y `try_catch` permite atrapar errores con `try` o `intentar` y `catch` o `capturar`.

## Tokens y palabras reservadas
El lexer de `src/cobra/lexico/lexer.py` define todos los tokens. Las principales palabras clave son:
- `var`, `variable`, `func`, `metodo`, `atributo`, `rel`
- `si`, `sino`, `mientras`, `para`, `import`, `usar`, `macro`, `hilo`, `asincronico`
- `switch`, `case`, `clase`, `in`, `holobit`, `proyectar`, `transformar`, `graficar`
- `try`/`intentar`, `catch`/`capturar`, `throw`/`lanzar`
- `imprimir`, `yield`, `esperar`, `romper`, `continuar`, `pasar`, `afirmar`, `eliminar`,
  `global`, `nolocal`, `lambda`, `con`, `finalmente`, `desde`, `como`, `retorno`, `fin`, `hilo`

Además existen tokens para operadores (`+`, `-`, `*`, `/`, `==`, `&&`, etc.), delimitadores como paréntesis, corchetes y llaves, y literales (`ENTERO`, `FLOTANTE`, `CADENA`, `BOOLEANO`).

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

## Control de flujo
```cobra
si x > 0:
    imprimir "positivo"
sino:
    imprimir "no positivo"
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
Los ejemplos de `frontend/docs/sintaxis.rst` muestran el uso básico del lenguaje: declaraciones con `var`, funciones `func`, condicionales `si`/`sino`, bucles `mientras` y `para`, holobits, importaciones, manejo de excepciones con `try`/`catch`, hilos y decoradores con `@`.
