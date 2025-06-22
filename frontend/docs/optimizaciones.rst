Optimizaciones del AST
======================

El proyecto incluye un conjunto de visitantes que mejoran el \ *performance\* del c\ódigo generado o ejecutado. Actualmente existen dos optimizaciones sencillas:

Plegado de constantes
---------------------
``optimize_constants`` recorre el AST evaluando expresiones cuyos operandos son valores literales. De esta forma, operaciones como ``2 + 3`` se reemplazan por ``5`` antes de la interpretación o de la transpilación.

Eliminación de código muerto
----------------------------
``remove_dead_code`` elimina instrucciones que nunca se ejecutarán. Por ejemplo, todo lo que aparezca después de ``return`` dentro de una función se descarta y, si un condicional tiene una condición constante, solo se conserva la rama correspondiente.

Estas optimizaciones se aplican automáticamente antes de ejecutar el intérprete y en los transpiladores a Python y JavaScript.
