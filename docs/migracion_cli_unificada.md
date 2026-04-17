# Guía de migración a la CLI unificada

Esta guía ayuda a migrar desde comandos legacy y flujos dependientes de flags de backend hacia la superficie oficial de Cobra.

## Objetivo

Adoptar el modelo unificado:

- `cobra run`
- `cobra build`
- `cobra test`
- `cobra mod`

Con backends públicos oficiales:

- `python`
- `javascript`
- `rust`

## Terminología unificada

- **Interfaz pública**: comandos `cobra run/build/test/mod` y backends oficiales `python`, `javascript`, `rust`.
- **Compatibilidad interna**: aliases legacy y backends internos usados solo para migración controlada.

## Mapeo de comandos legacy (equivalencia viejo → nuevo)

| Comando legacy (viejo) | Comando unificado (nuevo) |
|---|---|
| `cobra archivo.co` | `cobra run archivo.co` |
| `cobra compilar archivo.co --backend <target>` | `cobra build archivo.co --backend <target>` |
| `cobra ejecutar archivo.co` | `cobra run archivo.co` |
| `cobra verificar archivo.co -l python,javascript,rust` | `cobra test archivo.co --langs python javascript rust` |
| `cobra modulos listar` | `cobra mod list` |
| `cobra modulos instalar ruta/al/modulo.co` | `cobra mod install ruta/al/modulo.co` |
| `cobra modulos remover modulo.co` | `cobra mod remove modulo.co` |
| `cobra modulos buscar nombre` | `cobra mod search nombre` |
| `cobra modulos publicar ruta/al/modulo.co` | `cobra mod publish ruta/al/modulo.co` |
| `cobra interactive archivo.co` | `cobra run archivo.co` |
| `cobra init` | `cobra mod init` |
| `cobra crear` | `cobra mod init` |
| `cobra paquete` | `cobra mod publish` |

## Migración de flags `--backend`

1. Identifica usos de backends no públicos en scripts/CI (`go`, `cpp`, `java`, `wasm`, `asm`).
2. Sustituye por uno de los oficiales según necesidad:
   - `python`: máxima cobertura SDK.
   - `javascript`: integración Node/web.
   - `rust`: compilación nativa y rendimiento.
3. Estandariza pipelines para que `build` y validaciones usen exclusivamente `python`, `javascript` o `rust`.

## Plan de migración recomendado (paso a paso)

1. **Inventario**: lista comandos legacy usados en repositorio y CI.
2. **Sustitución**: aplica mapeo a `run/build/test/mod`.
3. **Backends**: elimina targets no públicos en flags `--backend` (`go`, `cpp`, `java`, `wasm`, `asm` son internal-only).
4. **Validación**: ejecuta pruebas/regresión del proyecto.
5. **Limpieza**: documenta fecha de retiro interno de aliases legacy.

## Compatibilidad interna/migración (proyectos antiguos)

Para evitar bloqueos en proyectos históricos:

- Mantén temporalmente aliases legacy en scripts críticos.
- Conserva solo el mínimo de rutas legacy mientras se completa la migración.
- Si no hay alternativa inmediata, habilita temporalmente `COBRA_INTERNAL_LEGACY_TARGETS=1`.
- Define una fecha de corte para remover comandos/flags antiguos.

La compatibilidad legacy debe tratarse como **transición controlada**, no como interfaz principal.
