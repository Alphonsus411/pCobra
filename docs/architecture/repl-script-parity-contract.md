# Contrato de paridad REPL ↔ Script (ExecuteCommand)

## Objetivo

Definir un contrato explícito para asegurar que la ejecución de snippets Cobra sea
equivalente entre:

- Ruta **script**: `ExecuteCommand` (ejecución desde archivo).
- Ruta **REPL**: `InteractiveCommand.ejecutar_codigo` (ejecución interactiva).

Este contrato se valida con una **matriz mínima de paridad** en tests.

## Matriz mínima cubierta

La matriz de validación incluye cinco categorías semánticas mínimas:

1. Asignación.
2. Condicional.
3. Bucle.
4. Función.
5. Error semántico.

Cada caso reutiliza un estado inicial compartido (`persistente = 10`) para comprobar no
solo resultado visible, sino también la continuidad del contexto de ejecución.

## Reglas del contrato

Para cada snippet de la matriz, ambas rutas deben cumplir:

1. **Misma salida observable (`stdout`)**.
2. **Mismo tipo de error** (clasificación funcional equivalente):
   - `analisis`: errores de lexer/parser.
   - `semantico`: errores de evaluación/ejecución.
   - `None`: ejecución exitosa sin error.
3. **Mismo efecto en estado persistente**:
   - En REPL, la variable persistente (`persistente`) debe seguir accesible tras ejecutar
     el snippet y el `probe`.
   - En script, la verificación se hace dentro del mismo archivo ejecutado (misma
     unidad de ejecución completa).

## Implementación de referencia en tests

La cobertura del contrato vive en:

- `tests/unit/test_cli_execution_pipeline_contract.py`:
  - `test_matriz_minima_paridad_execute_script_vs_repl`
  - helpers `_run_execute_via_script`, `_run_repl`,
    `_clasificar_error_execute`, `_clasificar_error_repl`.

## Motivación arquitectónica

El pipeline compartido (`execution_pipeline.py`) centraliza análisis, validación y
ejecución canónica. Este contrato agrega una garantía de regresión orientada al
comportamiento externo entre fronteras de entrada distintas (archivo vs REPL),
evitando divergencias sutiles al evolucionar la CLI.
