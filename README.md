## Cobra

Cobra es un lenguaje de programación experimental completamente en español, diseñado para ser versátil y adecuado para tareas de alto, medio y bajo nivel. Su objetivo es proporcionar un entorno amigable para la simulación, visualización y manipulación de datos complejos, como los holobits, así como para la programación estándar en entornos modernos.

## Características principales:

- **Sintaxis en español**: Todas las palabras clave y estructuras del lenguaje están en español, para facilitar su uso por hablantes nativos.
- **Gestión de memoria automática**: Cobra incorpora un sistema de manejo de memoria basado en algoritmos genéticos que optimiza el uso de los recursos durante la ejecución.
- **Soporte para holobits**: Un tipo de dato multidimensional que permite trabajar con datos de alta complejidad.
- **Transpiler a Python y JavaScript**: Los programas escritos en Cobra pueden ser transpilados a Python o JavaScript, lo que permite su ejecución en una variedad de plataformas.

## Ejemplo básico:

````cobra
var x = holobit([0.8, -0.5, 1.2])

# Proyección en 2D
var proyeccion = proyectar(x, '2D')
imprimir(proyeccion)

# Rotar 45 grados
var rotado = transformar(x, 'rotar', 45)
imprimir(rotado)

# Graficar el holobit
graficar(x)
````

## Sintaxis actual de Cobra

### 1. Declaración de variables:

- Utilizamos ```var``` para declarar una variable:

````cobra
var nombre = "Cobra"
var numero = 10
````
### 2. Funciones:
- Se define una función con la palabra clave ```func``` y se utiliza ```:``` para marcar el cuerpo de la función:

````cobra
func sumar(a, b) :
    return a + b
````

### 3. Función relativa (rel):

- Una función que se puede usar en contextos temporales específicos:

````cobra
rel calculo_temporal(x) :
    return x * 2
````

### 4. Condicionales:

- Se usan ```si``` y ```sino``` para manejar condiciones:

````cobra
si x > 10 :
    imprimir("x es mayor que 10")
sino :
    imprimir("x es menor o igual a 10")
````

### 5. Bucles:

- Cobra soporta bucles ```mientras``` y ```para```:

````cobra
mientras x < 5 :
    imprimir(x)
    x += 1

para var i en rango(5) :
    imprimir(i)
````

## Avances hasta el momento

- **Lexer y Parser funcionales**: El sistema léxico y sintáctico está completamente implementado y es capaz de procesar asignaciones de variables, funciones, condicionales, bucles y operaciones de holobits.
- **Holobits**: Tipo de dato especial para trabajar con información multidimensional, con soporte para operaciones como proyecciones, transformaciones y visualización.
- **Gestión de memoria automatizada**: Cobra incluye un sistema de manejo de memoria optimizado que se ajusta automáticamente utilizando algoritmos genéticos.
- **Transpilación a otros lenguajes**: Se ha implementado un transpilador que convierte el código Cobra a Python y JavaScript.
- **Pruebas unitarias**: Se han creado pruebas para validar el correcto funcionamiento del lexer y el parser.

## Próximos pasos
- Expandir las funcionalidades para holobits.
- Mejorar el sistema de simulación y visualización.
- Implementar nuevas optimizaciones para un mejor rendimiento en simulaciones complejas.

