# Arquitectura del Parser y los Transpiladores

Este documento resume la relaci\u00f3n entre los m\u00f3dulos principales del compilador de Cobra y c\u00f3mo cooperan para transformar el c\u00f3digo fuente.

## M\u00f3dulos principales

### `lexer`
Se encarga de leer el texto fuente y convertirlo en una secuencia de *tokens*. Cada token registra informaci\u00f3n sobre su tipo y su posici\u00f3n en el archivo para que el parser pueda procesarlo correctamente.

### `parser`
Consume los tokens generados por el lexer y construye el \u00c1rbol de Sintaxis Abstracta (**AST**). El parser valida la estructura del programa y crea los nodos que representar\u00e1n instrucciones, expresiones y declaraciones.

### `transpilers`
Una vez disponible el AST, los transpiladores recorren cada nodo mediante el patr\u00f3n *Visitor* para generar c\u00f3digo en otros lenguajes. Cobra incluye transpiladores a Python, JavaScript, ensamblador, Rust, C++, Go, Kotlin, Swift, R, Julia, Java, COBOL, Fortran, Pascal, Ruby, PHP, Perl, VisualBasic, Matlab y LaTeX.

## Interacci\u00f3n general
El proceso habitual comienza con el lexer, sigue con el parser y finaliza en el int\u00e9rprete o en alguno de los transpiladores. La siguiente gr\u00e1fica resume dicho flujo.

```{graphviz}
digraph pipeline {
    rankdir=LR;
    Lexer -> Parser -> AST;
    AST -> Interprete;
    AST -> Transpiladores;
}
```

```{uml}
@startuml
Lexer --> Parser
Parser --> AST
AST --> "Interprete"
AST --> Transpiladores
Transpiladores --> Python
Transpiladores --> JS
Transpiladores --> ASM
Transpiladores --> Rust
@enduml
```

Para detalles sobre la estructura de nodos consulta [docs/estructura_ast.md](estructura_ast.md).
