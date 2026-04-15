# Ecosistema unificado de Cobra

Este documento formaliza la arquitectura de alto nivel en **5 capas** para el ecosistema unificado de Cobra.

## Diagrama de 5 capas

```text
+-------------------------------------------------------------------+
| 1) CLI pública                                                    |
|    cobra run | cobra build | cobra test | cobra mod               |
+-------------------------------+-----------------------------------+
                                |
                                v
+-------------------------------------------------------------------+
| 2) Orquestador                                                     |
|    - Resolución de comandos                                        |
|    - Pipeline de compilación/transpilación                         |
|    - Aplicación de políticas de backend                            |
+-------------------------------+-----------------------------------+
                                |
                                v
+-------------------------------------------------------------------+
| 3) Adapters                                                        |
|    - Adapter Python                                                |
|    - Adapter JavaScript                                            |
|    - Adapter Rust                                                  |
+-------------------------------+-----------------------------------+
                                |
                                v
+-------------------------------------------------------------------+
| 4) Transpilers internos                                            |
|    - Lexer / Parser / AST / IR                                     |
|    - Transpiladores internos por backend                           |
+-------------------------------+-----------------------------------+
                                |
                                v
+-------------------------------------------------------------------+
| 5) Bindings / Runtime                                              |
|    - Python runtime                                                |
|    - Node.js runtime                                               |
|    - Rust toolchain                                                |
+-------------------------------------------------------------------+
```

## Contrato público

La superficie pública estable para esta fase es:

- CLI: `run`, `build`, `test`, `mod`.
- Backends oficiales: `python`, `javascript`, `rust`.
- Módulos stdlib públicos: `cobra.core`, `cobra.datos`, `cobra.web`, `cobra.system`.

## Estabilidad contractual en esta fase

Se declara explícitamente que **lexer, parser, AST y transpiladores internos no cambian su contrato externo** durante esta fase.

Eso implica que cualquier evolución en estos componentes se considera de implementación interna mientras no altere la API pública estable declarada.
