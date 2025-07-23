# Estructura del AST en Cobra

Este documento describe brevemente las clases base que conforman el árbol de sintaxis abstracta (AST) y cómo se recorren utilizando el patrón *Visitor*.

## `NodoAST`

Tal y como se explica en `frontend/docs/design_patterns.rst`, todas las clases de nodos heredan de `NodoAST`. Esta clase define el método `aceptar` que delega la operación en una instancia de `NodeVisitor`:

```python
@dataclass
class NodoAST:
    """Clase base para todos los nodos del AST."""

    def aceptar(self, visitante):
        """Acepta un visitante y delega la operación a éste."""
        return visitante.visit(self)
```

Gracias a esta interfaz común, cualquier nodo puede ser procesado de forma uniforme por los diferentes componentes del compilador.

## `NodeVisitor`

El recorrido de los nodos se realiza mediante la clase `NodeVisitor`, mencionada tanto en `frontend/docs/design_patterns.rst` como en `frontend/docs/arquitectura.rst`. Su método `visit` despacha automáticamente al método `visit_<nodo>` correspondiente según el tipo de cada objeto:

```python
class NodeVisitor:
    """Recorre nodos del AST despachando al método adecuado."""

    def visit(self, node):
        method_name = f"visit_{self._camel_to_snake(node.__class__.__name__)}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
```

Los transpiladores y otras herramientas derivan de esta clase para implementar sólo las funciones de visita que necesitan.

## Diagramas de referencia

A continuación se muestran los diagramas principales del AST y la arquitectura general. Para evitar incluir archivos binarios en el repositorio, se incrustan las definiciones originales de Graphviz y PlantUML. Al generar la documentación, Sphinx convertirá automáticamente estos bloques en imágenes.

```{graphviz}
digraph classes {
    node [shape=record, fontname="Helvetica"];
    Lexer [label="{Lexer|+tokenize()}"];
    Parser [label="{Parser|+parse()}"];
    AST [label="{AST|+Node classes}"];
    Interpreter [label="{Interpreter|+execute()}"];
    Transpilers [label="{Transpilers|+to_python()|+to_js()|...}"];

    Lexer -> Parser;
    Parser -> AST;
    AST -> Interpreter;
    AST -> Transpilers;
}
```

```{uml}
@startuml
Lexer --> Parser
Parser --> AST
AST --> Transpiladores
Transpiladores --> Python
Transpiladores --> JS
Transpiladores --> ASM
Transpiladores --> Rust
Transpiladores --> "C++"
Transpiladores --> Go
Transpiladores --> Kotlin
Transpiladores --> Swift
Transpiladores --> R
Transpiladores --> Julia
Transpiladores --> Java
Transpiladores --> COBOL
Transpiladores --> Fortran
Transpiladores --> Pascal
Transpiladores --> VisualBasic
Transpiladores --> Ruby
Transpiladores --> PHP
Transpiladores --> Perl
Transpiladores --> Matlab
Transpiladores --> Mojo
Transpiladores --> LaTeX
@enduml
```
