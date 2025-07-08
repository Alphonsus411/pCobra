# Diagrama de flujo de la compilación

Este diagrama resume las etapas principales del proceso de compilación de Cobra.

```{uml}
@startuml
start
:Archivo fuente (.co);
:Lexer;
:Parser;
:AST intermedio;
:Transpilador;
:Codigo destino (Python, JS, ...);
stop
@enduml
```
