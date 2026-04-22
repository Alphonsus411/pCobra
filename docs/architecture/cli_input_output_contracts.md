# Contrato de entrada/salida de servicios CLI (run/test/mod)

Este documento define el **Single Source of Truth** para la entrada de servicios de aplicación usados por:

- CLI pública v2 (`cobra run`, `cobra test`, `cobra mod`)
- CLI legacy (`ejecutar`, `verificar`, `modulos`)
- grupo `legacy` en UI v2
- invocaciones programáticas (scripts internos/REPL)

## Objetivo

Evitar divergencias entre capas de parsing (`argparse`) y capa de aplicación.  
Los servicios **no consumen `argparse.Namespace`**, consumen DTOs estables.

## DTOs canónicos

Ubicación: `src/pcobra/cobra/cli/services/contracts.py`.

- `RunRequest`
  - Entrada mínima: `archivo`
  - Campos opcionales/defaults: `debug=False`, `sandbox=False`, `contenedor=None`, `formatear=False`, `modo="mixto"`, `seguro=True`, `verbose=0`, `depurar=False`, `extra_validators=None`, `allow_insecure_fallback=False`, `backend_reason=None`.

- `TestRequest`
  - Entrada mínima: `archivo`, `lenguajes`
  - Campos opcionales/defaults: `modo="mixto"`, `backend_reason=None`.

- `ModRequest`
  - Entrada mínima: `accion`
  - Reglas por acción:
    - `instalar|publicar` requieren `ruta`
    - `remover|buscar` requieren `nombre`

## Normalización (una función por DTO)

- `normalize_run_request(...)`
- `normalize_test_request(...)`
- `normalize_mod_request(...)`

Cada función aplica:

1. validación de obligatorios,
2. defaults,
3. coerción básica de tipos,
4. compatibilidad de alias de parser (`file`/`archivo`, `langs`/`lenguajes`, etc.).

## Flujo recomendado

1. El comando CLI parsea argumentos (`argparse`).
2. El comando mapea explícitamente a DTO canónico.
3. El servicio invoca su normalizador (defensa en profundidad).
4. El servicio ejecuta la lógica y retorna código de salida (`int`).

## Contrato de salida

Los servicios `RunService`, `TestService`, `ModService` retornan:

- `0`: éxito.
- `1`: error funcional/validación/runtime manejado.

No retornan estructuras ad-hoc; el canal de detalle es logging/mensajes CLI.

