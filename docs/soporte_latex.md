# Soporte LaTeX

El transpilador inverso **ReverseFromLatex** permite convertir fragmentos
básicos de pseudocódigo escritos en LaTeX al AST de Cobra. El objetivo es
facilitar prototipos sencillos donde se utilice el entorno `algorithmic` o
comandos similares.

## Alcance

- Comando `\STATE` con asignaciones y expresiones matemáticas simples.
- Condicionales `\IF`/`\ELSE`/`\ENDIF`.
- Bucles `\WHILE`/`\ENDWHILE`.
- Bucles `\FOR{$i=1 \TO n$}`/`\ENDFOR` con límites numéricos o
  expresiones aritméticas.
- Las expresiones se analizan mediante [`sympy`](https://www.sympy.org/),
  lo que habilita operadores como `+`, `-`, `*`, `/`, `^` y comparaciones.

## Limitaciones

- No se soportan macros personalizadas ni entornos de LaTeX distintos al
  pseudocódigo mencionado.
- El formato del bucle `\FOR` debe seguir exactamente la forma
  `\FOR{$i=1 \TO n$}`. Otras variantes no son reconocidas.
- No se manejan estructuras adicionales del paquete `algorithmic` como
  `\REPEAT`, `\UNTIL` o funciones definidas en LaTeX.
- El análisis ignora todo texto ajeno a los comandos anteriores.

Este soporte es experimental y está destinado a ejemplos mínimos; la
complejidad completa del lenguaje LaTeX queda fuera del alcance actual.

