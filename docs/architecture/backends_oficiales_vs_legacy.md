# Arquitectura: backends oficiales activos vs legacy opcional

## Resumen ejecutivo

`pcobra` mantiene un **contrato público activo** enfocado exclusivamente en tres backends:

- `python`
- `javascript`
- `rust`

Estos tres backends se consideran oficiales para startup normal, comandos base y cobertura contractual de integración.

## Backends oficiales activos (ruta normal)

En ruta normal de ejecución (por ejemplo `import pcobra`, `python -m pcobra` y bootstrap CLI),
la arquitectura valida y expone solo el conjunto público oficial.

Implicaciones:

1. El contrato de producto y pruebas se centra en los tres backends oficiales.
2. La política pública rechaza targets fuera de contrato en comandos públicos.
3. El arranque evita cargar transpilers legacy para mantener startup predecible y mínimo.

## Backends legacy opcionales (desactivados por defecto)

Los transpilers legacy viven en:

- `src/pcobra/cobra/transpilers/transpiler/legacy/*`

Estos módulos existen para compatibilidad histórica y casos internos, pero:

- **no forman parte del contrato público activo**, y
- **no deben cargarse durante el startup normal**.

Su uso es opcional/controlado y fuera del flujo principal soportado de cara a usuario final.

## Relación con pruebas de contrato

Las pruebas de contrato público en `tests/integration/transpilers/test_official_backends_contracts.py`
permanecen intencionadamente acotadas a los 3 backends oficiales, para alinear:

- política arquitectónica,
- expectativas de soporte, y
- matriz de compatibilidad publicada.
