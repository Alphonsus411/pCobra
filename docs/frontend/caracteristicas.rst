Caracteristicas principales de Cobra
=====================================

- **Sintaxis en espanol**: Todas las palabras clave y estructuras del lenguaje estan en español, para facilitar su uso por hablantes nativos.
- **Gestion de memoria automatica**: Cobra incorpora un sistema de manejo de memoria basado en algoritmos genéticos que optimiza el uso de los recursos durante la ejecución.
- **Soporte para holobits**: Un tipo de dato multidimensional que permite trabajar con datos de alta complejidad.
- **Transpiler a Python, JavaScript, ensamblador, Rust, C++, Go, Kotlin, Swift, R, Julia, Java, COBOL, Fortran, Pascal, Ruby, PHP, Perl, VisualBasic, Matlab, Mojo, LaTeX, C y WebAssembly**: Los programas escritos en Cobra pueden ser transpilados a estos lenguajes, lo que permite su ejecucion en una variedad de plataformas.
- **Nombres Unicode**: Los identificadores aceptan caracteres como `á`, `ñ` o `Ω`.

**Ejemplo basico**

var x = holobit([0.8, -0.5, 1.2])

# Proyección en 2D
var proyeccion = proyectar(x, '2D')
imprimir(proyeccion)

# Rotar 45 grados
var rotado = transformar(x, 'rotar', 45)
imprimir(rotado)

# Escalar y trasladar
escalar(x, 2)
mover(x, 1, 0, -1)
# ``escalar`` y ``mover`` requieren ``holobit-sdk`` >= 1.0.8; si no está
# disponible se calcula internamente.

# Graficar el holobit
graficar(x)

# Bucles de ejemplo
var contador = 0
mientras contador < 2 :
    imprimir(contador)
    contador += 1

para var i en rango(2) :
    imprimir(i)
