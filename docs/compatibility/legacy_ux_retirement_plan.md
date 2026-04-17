# Retiro de UX legacy para backends internal-only

Este plan aplica a los backends legacy mantenidos solo por compatibilidad interna:

- `go`
- `cpp`
- `java`
- `wasm`
- `asm`

## Fecha de retiro comprometida

- **Retiro total de compatibilidad legacy internal-only:** **30 de junio de 2027**.
- A partir de **1 de julio de 2027**, la CLI pública no debe aceptar rutas legacy ni feature flags de bypass.

## Flag temporal para equipos dependientes

Mientras dure la ventana de transición, se habilita la compatibilidad controlada con:

```bash
export COBRA_INTERNAL_LEGACY_TARGETS=1
```

Este flag es transitorio y no debe usarse en documentación pública ni en nuevos proyectos.

## Checklist de migración

1. **Inventario de uso**
   - Localizar comandos en CI/scripts que usen `go/cpp/java/wasm/asm`.
   - Identificar si usan `--backend` o `--tipo`.
2. **Cambio de targets**
   - Migrar pipelines a targets públicos: `python`, `javascript`, `rust`.
   - Para ejecución verificada, priorizar `python`/`javascript`/`rust`.
3. **Actualización de CLI**
   - Sustituir ejemplos/scripts `cobra compilar ... --backend <legacy>` por `--tipo <target-publico>`.
   - Eliminar dependencias del flag `COBRA_INTERNAL_LEGACY_TARGETS`.
4. **Validación técnica**
   - Ejecutar suites de transpilación/runtime de los targets públicos usados.
   - Verificar que no queden referencias legacy en docs públicas.
5. **Cierre**
   - Congelar nuevos cambios funcionales sobre UX legacy.
   - Confirmar readiness antes del 30/06/2027 y remover la ruta de compatibilidad.

Checklist operativo por fases: `docs/compatibility/internal_only_backend_removal_checklist.md`.
