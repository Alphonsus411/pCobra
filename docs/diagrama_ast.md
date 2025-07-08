# Diagrama general del AST

A continuación se muestra una vista simplificada de la jerarquía de nodos que componen el árbol de sintaxis abstracta.

```{uml}
@startuml
class Programa
class Declaracion
class Expresion
class Asignacion
class Funcion
class Llamada

Programa --> "*" Declaracion
Declaracion <|-- Asignacion
Declaracion <|-- Funcion
Declaracion <|-- Expresion
Expresion <|-- Llamada
@enduml
```
