# Guía de migración a la CLI unificada

Esta guía ayuda a migrar desde comandos legacy y flujos dependientes de flags de backend hacia la superficie oficial de Cobra.

## Objetivo

Adoptar el modelo unificado:

- `cobra run`
- `cobra build`
- `cobra test`
- `cobra mod`
- `cobra paquete` para empaquetado local de artefactos `.co`
- `cobra hub` para publicación, búsqueda e instalación en CobraHub

Con backends públicos oficiales:

- `python`
- `javascript`
- `rust`

## Terminología unificada

- **Interfaz pública**: comandos `cobra run/build/test/mod` y backends oficiales `python`, `javascript`, `rust`.
- **Compatibilidad interna**: aliases legacy y backends internos usados solo para migración controlada.

## Matriz de comandos (públicos vs internos vs obsoletos)

| Clase | Comandos |
|---|---|
| **Públicos (UI v2)** | `run`, `build`, `test`, `mod`, `paquete`, `hub` |
| **Internos (UI v2 / development)** | `legacy`, `debug`, `devops` |
| **Legacy públicos (UI v1, migración)** | `interactive`, `compilar`, `ejecutar`, `modulos`, `verificar`, `docs`, `plugins`, `init`, `crear` |
| **Legacy internos (UI v1)** | `cache`, `contenedor`, `gui`, `jupyter`, `qualia`, `agix` |
| **Legacy obsoletos (UI v1)** | `dependencias`, `empaquetar`, `bench`, `benchmarks`, `benchmarks2`, `benchtranspilers`, `benchthreads`, `profile`, `transpilar-inverso`, `validar-sintaxis`, `qa-validar` |

> Fuente de verdad de superficie pública: `PUBLIC_COMMANDS=("run","build","test","mod")`.

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
| `cobra modulos buscar nombre` | `cobra mod search nombre` para módulos sueltos históricos; `cobra hub buscar nombre` para paquetes CobraHub |
| `cobra modulos publicar ruta/al/modulo.co` | Compatibilidad histórica de módulos sueltos; usa `cobra hub publicar dist/paquete.co` para paquetes `.co` con `cobra.pkg.json` |
| `cobra interactive archivo.co` | `cobra run archivo.co` |
| `cobra init` | `cobra mod init` |
| `cobra crear` | `cobra mod init` |
| `cobra paquete crear <dir>` | Flujo local moderno de paquetes: crea `cobra.pkg.json` |
| `cobra paquete construir <dir> <salida.co>` | Flujo local moderno de paquetes: construye el ZIP `.co` con manifiesto |
| `cobra paquete validar <salida.co>` | Flujo local moderno de paquetes: valida estructura y manifiesto |
| `cobra paquete inspeccionar <salida.co>` | Flujo local moderno de paquetes: muestra metadatos y contenido |
| `cobra paquete extraer <salida.co> <destino>` | Flujo local moderno de paquetes: extracción local explícita |
| `cobra paquete instalar <salida.co> [destino]` | Alias legacy de `cobra paquete extraer` para extracción/instalación local |
| `cobra hub publicar <salida.co>` | Flujo moderno de CobraHub para paquetes `.co` con manifiesto |
| `cobra hub buscar <nombre>` | Flujo moderno de CobraHub para descubrir paquetes |
| `cobra hub instalar <nombre>` | Flujo moderno de CobraHub para descargar e instalar paquetes |

### Nota sobre paquetes `.co` y Lexer/Parser

No se toca el Lexer ni el Parser para soportar paquetes `.co`: un paquete publicable se detecta en la capa de herramientas como un ZIP legible que contiene `cobra.pkg.json` en la raíz, no como una nueva sintaxis Cobra. Por eso, no migres paquetes `.co` con manifiesto hacia `cobra mod publish`; usa `cobra paquete crear|construir|validar|inspeccionar|extraer` para el ciclo local y `cobra hub publicar|buscar|instalar` para CobraHub. `cobra modulos publicar|buscar` queda reservado a compatibilidad histórica de módulos sueltos.

## Plan de migración recomendado (paso a paso)

1. **Inventario**: lista comandos legacy usados en repositorio y CI.
2. **Sustitución**: aplica mapeo a `run/build/test/mod`.
3. **Backends**: elimina targets no públicos en flags `--backend`.
4. **Validación**: ejecuta pruebas/regresión del proyecto.
5. **Limpieza**: documenta fecha de retiro interno de aliases legacy.

## Compatibilidad interna/migración (proyectos antiguos)

Para evitar bloqueos en proyectos históricos:

- Mantén temporalmente aliases legacy en scripts críticos.
- Conserva solo el mínimo de rutas legacy mientras se completa la migración.
- Si no hay alternativa inmediata, habilita temporalmente `COBRA_INTERNAL_LEGACY_TARGETS=1`.
- Define una fecha de corte para remover comandos/flags antiguos.

La compatibilidad legacy debe tratarse como **transición controlada**, no como interfaz principal.

> **Nota contractual:** aliases legacy (`cli`, `cobra`, `core`, `bindings`) se mantienen solo como shims de migración deprecados. No forman parte del contrato público de imports ni del artefacto publicado en PyPI.
