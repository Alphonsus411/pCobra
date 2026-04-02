# Auditoría CI: paridad de `standard_library`

## Resumen

- Símbolos públicos auditados en `standard_library.__all__`: **121**.
- Decoradores auditados en detalle: **9**.
- Errores: **0**.
- Warnings: **0**.

## Tabla de paridad (funcionalidad / python / javascript / rust / go / cpp / java / wasm / asm)

| funcionalidad | python | javascript | rust | go | cpp | java | wasm | asm | severidad | notas |
|---|---|---|---|---|---|---|---|---|---|---|
| memoizar | full | full | full | partial | full | partial | partial | partial | ok | - |
| dataclase | full | full | full | partial | full | partial | partial | partial | ok | - |
| temporizar | full | full | full | partial | full | partial | partial | partial | ok | - |
| depreciado | full | full | full | partial | full | partial | partial | partial | ok | - |
| sincronizar | full | full | full | partial | full | partial | partial | partial | ok | - |
| reintentar | full | full | full | partial | full | partial | partial | partial | ok | - |
| reintentar_async | full | full | full | partial | full | partial | partial | partial | ok | - |
| orden_total | full | full | full | partial | full | partial | partial | partial | ok | - |
| despachar_por_tipo | full | full | full | partial | full | partial | partial | partial | ok | - |

## Hallazgos

Sin hallazgos: contrato de paridad consistente.
