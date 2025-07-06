Optimizaciones del AST
======================

El proyecto incluye un conjunto de visitantes que mejoran el \ *performance\* del código generado o ejecutado. Actualmente existen cuatro optimizaciones sencillas:

Plegado de constantes
---------------------
``optimize_constants`` recorre el AST evaluando expresiones cuyos operandos son valores literales. De esta forma, operaciones como ``2 + 3`` se reemplazan por ``5`` antes de la interpretación o de la transpilación.

Eliminación de código muerto
----------------------------
``remove_dead_code`` elimina instrucciones que nunca se ejecutarán. Por ejemplo, todo lo que aparezca después de ``return`` dentro de una función se descarta y, si un condicional tiene una condición constante, solo se conserva la rama correspondiente.

Integración de funciones simples
--------------------------------
``inline_functions`` identifica funciones sin parámetros y con un único ``return`` para sustituir sus llamadas por el valor retornado, eliminando además la definición original cuando es posible.

Eliminación de subexpresiones comunes
------------------------------------
``eliminate_common_subexpressions`` detecta expresiones idénticas que se repiten dentro de una misma función o en el nivel global. Dichas expresiones se calculan una única vez asignándose a una variable temporal y las repeticiones se reemplazan por el identificador generado.

Estas optimizaciones se aplican automáticamente antes de ejecutar el intérprete y en los transpiladores a Python, JavaScript, ensamblador, Rust, C++, Go, R, Julia, Java, COBOL, Fortran, Pascal, Ruby, PHP, Matlab y LaTeX.

Decoradores de rendimiento (``smooth-criminal``)
------------------------------------------------
Se incorporó la biblioteca ``smooth-criminal`` al núcleo para facilitar la optimización de funciones de usuario. Desde ``src.core`` se exponen los ayudantes ``optimizar`` y ``perfilar`` que utilizan dicha librería para aplicar decoradores como ``auto_boost`` y obtener métricas de ejecución.
