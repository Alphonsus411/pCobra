Caracteristicas principales de Cobra
=====================================

- **Sintaxis en espanol**: Todas las palabras clave y estructuras del lenguaje estan en español, para facilitar su uso por hablantes nativos.
- **Gestion de memoria automatica**: Cobra incorpora un sistema de manejo de memoria basado en algoritmos genéticos que optimiza el uso de los recursos durante la ejecución.
- **Soporte para holobits**: Un tipo de dato multidimensional que permite trabajar con datos de alta complejidad.
- **Transpilación oficial a 8 backends**: Los programas escritos en Cobra pueden transpilarse a ``python``, ``rust``, ``javascript``, ``wasm``, ``go``, ``cpp``, ``java`` y ``asm``.
- **Clasificación por tiers**: ``python``, ``rust``, ``javascript`` y ``wasm`` son Tier 1; ``go``, ``cpp``, ``java`` y ``asm`` son Tier 2.
- **Separación explícita de runtime**: el runtime oficial verificable cubre ``python``, ``rust``, ``javascript`` y ``cpp``; ``go`` y ``java`` permanecen en best-effort no público; ``wasm`` y ``asm`` son de solo transpilación.
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
# ``escalar`` y ``mover`` son helpers del runtime Python y no forman parte del contrato Holobit multi-backend.
# Con ``holobit-sdk`` >= 1.0.8 delegan en el SDK; si esa versión no expone los métodos,
# Cobra calcula internamente un equivalente local.

# Graficar el holobit
graficar(x)

# Bucles de ejemplo
var contador = 0
mientras contador < 2 :
    imprimir(contador)
    contador += 1

para var i en rango(2) :
    imprimir(i)
