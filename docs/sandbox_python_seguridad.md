# Sandbox Python: garantías y limitaciones reales

Este documento describe el comportamiento actual de `pcobra.core.sandbox` para ejecución Python.

## Garantías actuales

- La sandbox aplica una validación AST previa (`_verificar_codigo_prohibido`) para bloquear:
  - `eval`, `exec`, `open` y accesos equivalentes por alias.
  - importaciones fuera de una **allowlist explícita**.
  - uso de helpers de carga dinámica o reflexión peligrosa, incluyendo patrones con `__loader__` y recuperación de `__builtins__` por introspección.
- El import runtime (`_safe_import`) también aplica la misma política de **allowlist** para evitar bypasses indirectos con `__import__`.
- Se expone un conjunto restringido de builtins (`_SANDBOX_BASE_BUILTINS`) con funciones básicas de cálculo/colecciones, en lugar de exponer el mapa completo.
- La ejecución ocurre en un proceso hijo con timeout y, en POSIX, límite opcional de memoria.

## Allowlist de imports

Solo se permiten módulos cuyo root está en `_SANDBOX_IMPORT_ALLOWLIST`:

- `math`
- `statistics`
- `decimal`
- `fractions`
- `random`
- `itertools`
- `functools`
- `collections`
- `re`
- `string`
- `datetime`
- `json`

Cualquier import directo o indirecto fuera de esta lista se rechaza.

## Limitaciones (importantes)

- Esta sandbox **reduce superficie de ataque**, pero no equivale a aislamiento de sistema operativo completo.
- La robustez depende de `RestrictedPython`; sin él, por defecto se rechaza ejecutar código seguro.
- Las políticas AST son por patrones: nuevas técnicas de evasión pueden requerir endurecimientos adicionales.
- Para escenarios de alta criticidad, se recomienda combinar con aislamiento fuerte (contenedor, usuario sin privilegios, seccomp/AppArmor, límites cgroups).

## Recomendaciones operativas

- Tratar la sandbox como capa de defensa en profundidad, no como único control.
- Revisar periódicamente allowlist y tests de evasión.
- Mantener dependencias de seguridad al día.
