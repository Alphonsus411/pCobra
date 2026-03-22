# [EXPERIMENTAL] Mapeo de construcciones Cobra a LLVM IR

> **Estado:** experimental.
> **Ámbito:** diseño exploratorio fuera de los 8 targets oficiales de salida.
> **Política:** este documento no define soporte oficial ni contrato de compatibilidad.

Este documento inventaria las construcciones actuales del lenguaje Cobra y propone una representación aproximada en LLVM IR. Además, se incluyen diagramas de flujo y ejemplos de código intermedio.

| Construcción Cobra | Descripción | Representación en LLVM IR |
| --- | --- | --- |
| Variables | Declaración y asignación de identificadores | `alloca`, `store`, `load` |
| Expresiones aritméticas | Operaciones numéricas básicas | `add`, `sub`, `mul`, `sdiv`, `fadd`, `fsub` |
| Condicionales | Bloques `si` / `sino` | `icmp` + `br` condicional |
| Bucles | `mientras` y `para` | bloques básicos y saltos explícitos |
| Funciones | `func` con parámetros y retorno | `define`, `call`, `ret` |
| Clases | Objetos y métodos | modelado pendiente |
| Excepciones | `intentar` / `capturar` | modelado pendiente |

## Observaciones

- La tabla anterior es orientativa y no contractual.
- No existe hoy un backend LLVM registrado en la CLI pública.
- Cualquier implementación futura debe pasar antes por la política oficial de targets.
