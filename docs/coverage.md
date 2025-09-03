# Informe de cobertura

Este informe recoge los resultados de `coverage run -m pytest` y `coverage report`.

## Resumen

- Cobertura total: 22 % (por debajo del objetivo del 85 %).
- Durante la recolección de pruebas se produjeron 49 errores de importación, lo que limita la cobertura actual.

## Módulos con cobertura inferior al 85 %

A continuación se listan algunos de los módulos con menor cobertura detectados:

| Módulo | Cobertura |
| --- | --- |
| `src/pcobra/cobra/cli/cli.py` | 13 % |
| `src/pcobra/cobra/cli/cobrahub_client.py` | 16 % |
| `src/pcobra/cobra/core/parser.py` | 9 % |
| `src/pcobra/cobra/transpilers/feature_inspector.py` | 0 % |
| `src/pcobra/cobra/transpilers/reverse/from_c.py` | 3 % |
| `src/pcobra/cobra/transpilers/transpiler/to_python.py` | 33 % |
| `src/pcobra/core/ast_nodes.py` | 81 % |
| `src/pcobra/core/interpreter.py` | 6 % |
| `src/pcobra/gui/app.py` | 0 % |

Estos resultados indican que gran parte del código aún carece de cobertura de pruebas suficiente.

## Áreas que requieren atención

- Mejorar la cobertura de los comandos de la CLI.
- Añadir pruebas para los distintos transpiladores y el intérprete central.
- Resolver los errores de importación que impiden ejecutar las pruebas.

