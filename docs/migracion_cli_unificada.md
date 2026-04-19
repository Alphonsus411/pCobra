# Guía de migración a la CLI unificada

Esta guía ayuda a migrar desde comandos legacy y flujos dependientes de flags de backend hacia la superficie oficial de Cobra.

## Objetivo

Adoptar el modelo unificado:

- `cobra --ui v2 run`
- `cobra --ui v2 build`
- `cobra --ui v2 test`
- `cobra --ui v2 mod`

Con backends públicos oficiales:

- `python`
- `javascript`
- `rust`

## Mapeo de comandos legacy

| Legacy | Nuevo comando recomendado |
|---|---|
| `cobra archivo.co` | `cobra --ui v2 run archivo.co` |
| `cobra compilar archivo.co --backend <target>` | `cobra --ui v2 build archivo.co` |
| `cobra modulos listar` | `cobra --ui v2 mod list` |
| `cobra modulos instalar ruta/al/modulo.co` | `cobra --ui v2 mod install ruta/al/modulo.co` |
| `cobra modulos remover modulo.co` | `cobra --ui v2 mod remove modulo.co` |

## Migración de selección de backend

1. Identifica usos de backends no públicos en scripts/CI (`go`, `cpp`, `java`, `wasm`, `asm`).
2. En `cobra --ui v2 build`, elimina `--backend`: la selección se resuelve internamente por el orquestador.
3. Alinea artefactos/pipelines hacia uno de los oficiales según necesidad:
   - `python`: máxima cobertura SDK.
   - `javascript`: integración Node/web.
   - `rust`: compilación nativa y rendimiento.
4. Estandariza pipelines para que `build` y validaciones apunten al conjunto oficial `python`, `javascript` o `rust`.

## Plan de migración recomendado (paso a paso)

1. **Inventario**: lista comandos legacy usados en repositorio y CI.
2. **Sustitución**: aplica mapeo a `--ui v2` con `run/build/test/mod`.
3. **Backends**: elimina flags `--backend` en comandos v2 y retira targets no públicos de pipelines.
4. **Validación**: ejecuta pruebas/regresión del proyecto.
5. **Limpieza**: documenta fecha de retiro interno de aliases legacy.

## Compatibilidad legacy (proyectos antiguos)

Para evitar bloqueos en proyectos históricos:

- Mantén temporalmente aliases legacy en scripts críticos.
- Conserva solo el mínimo de rutas legacy mientras se completa la migración.
- Define una fecha de corte para remover comandos/flags antiguos.

La compatibilidad legacy debe tratarse como **transición controlada**, no como interfaz principal.
