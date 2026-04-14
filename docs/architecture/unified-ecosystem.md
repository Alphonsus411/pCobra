# Ecosistema unificado de Cobra

Este documento describe la arquitectura de alto nivel donde **Cobra** es la única interfaz pública de entrada y coordina, de forma interna, la ejecución sobre backends oficiales.

## Diagrama de capas

```text
+-----------------------------------------------------------+
|                    Frontend Cobra (CLI)                   |
|        Comandos: cobra run | cobra build | cobra test |   |
|                          cobra mod                        |
+-------------------------------+---------------------------+
                                |
                                v
+-----------------------------------------------------------+
|                 Orquestador interno de Cobra              |
|  - Resolución de comandos                                 |
|  - Pipeline AST/IR                                        |
|  - Validación y políticas de targets                      |
|  - Coordinación de ejecución y artefactos                 |
+-------------------------------+---------------------------+
                                |
                                v
+-----------------------------------------------------------+
|                    Adapters de backend                    |
|          python adapter | javascript adapter | rust       |
+-------------------------------+---------------------------+
                                |
                                v
+-----------------------------------------------------------+
|                    Runtimes / bindings                    |
|      Python runtime | Node.js runtime | Rust toolchain    |
+-----------------------------------------------------------+
```

## Contrato público

- **Interfaz pública única:** `cobra`.
- **Comandos simplificados oficiales:** `run`, `build`, `test`, `mod`.
- **Backends oficiales públicos:** `python`, `javascript`, `rust`.

## Nota de compatibilidad

Los componentes legacy existen para mantener proyectos antiguos, pero fuera del contrato público principal. La recomendación es migrar gradualmente a la CLI unificada y a los backends oficiales.
