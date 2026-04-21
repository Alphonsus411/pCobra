# Auditoría runtime de shims (`core`, `cobra`, `bindings`) — 2026-04-21

## Objetivo
Documentar el estado actual de los shims legacy con patrón de reexport/alias y definir qué rutas siguen permitidas en runtime productivo vs. transición controlada.

## Resumen ejecutivo
- **Canónico en productivo**: `pcobra.*`.
- **Compatibilidad de transición explícita**: solo el fallback `core.sandbox` desde `execute_cmd`, protegido por la flag `PCOBRA_ENABLE_LEGACY_CORE_SANDBOX`.
- **Shims legacy permitidos solo transición**: `core`, `cobra`, `cobra.cli`, `bindings` y `bindings.contract`.

## Inventario auditado

| Shim / patrón | Implementación | Estado en runtime productivo | Estado transición | Notas de control |
|---|---|---|---|---|
| `pcobra.core.sandbox` (ruta canónica) | `src/pcobra/cobra/cli/commands/execute_cmd.py` | **Permitido** | **Permitido** | Ruta principal; se intenta primero siempre. |
| Fallback `core.sandbox` | `src/pcobra/cobra/cli/commands/execute_cmd.py` | **No permitido por defecto** | **Permitido solo con flag** | Requiere `PCOBRA_ENABLE_LEGACY_CORE_SANDBOX=1`. Emite warning estructurado `event=legacy_core_sandbox_fallback`. |
| `core` (shim paquete raíz) | `src/core/__init__.py` | **No recomendado** | **Permitido temporal** | Reexporta `pcobra.core` y mantiene alias en `sys.modules`. |
| `cobra` (shim paquete raíz) | `src/cobra/__init__.py` | **No recomendado** | **Permitido temporal** | Reexporta `pcobra.cobra`, inyecta alias `core`/`cobra.core`. |
| `cobra.cli` (shim compat) | `src/cobra/cli/__init__.py`, `src/cobra/cli/cli.py` | **No recomendado** | **Permitido temporal** | Marcado como `INTERNAL COMPATIBILITY ONLY`. |
| `bindings` | `src/bindings/__init__.py` | **No recomendado** | **Permitido temporal** | Deprecado explícitamente, sugiere `pcobra.cobra.bindings`. |
| `bindings.contract` | `src/bindings/contract.py` | **No recomendado** | **Permitido temporal** | Deprecado explícitamente, sugiere `pcobra.cobra.bindings.contract`. |
| `cli` (shim top-level) | `src/cli/__init__.py` | **No recomendado** | **Permitido temporal** | Activa compat legacy condicionada por mecanismo interno de `pcobra.cli`. |

## Política propuesta de operación
1. **Producción**: usar exclusivamente imports `pcobra.*` para rutas runtime críticas.
2. **Transición**:
   - habilitar fallback `core.sandbox` solo cuando sea estrictamente necesario,
   - registrar y monitorear warnings con `event=legacy_core_sandbox_fallback`,
   - planificar retiro de shims de alto nivel (`core`, `cobra`, `bindings`, `cli`) en ventanas controladas.
3. **Trazabilidad**:
   - conservar el nombre de la flag (`PCOBRA_ENABLE_LEGACY_CORE_SANDBOX`) en logs y runbooks,
   - revisar periódicamente uso real de fallback antes de eliminar compatibilidad.
