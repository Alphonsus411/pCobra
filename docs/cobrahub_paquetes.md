# CobraHub y paquetes `.co`

La guía de uso actualizada para crear, construir, validar, inspeccionar y extraer paquetes está en [`docs/frontend/paquetes.rst`](frontend/paquetes.rst).

## APIs CobraHub: legacy y recomendada

- **Legacy de módulos:** `src/pcobra/cobra/cli/cobrahub_client.py` mantiene el cliente HTTP base y la fachada compatible para publicar/descargar módulos sueltos con los endpoints `/modulos`. El comando `modulos` sigue apuntando a este flujo para no romper scripts existentes.
- **Ruta recomendada para paquetes:** `src/pcobra/cobra/cli/cobrahub_packages.py` concentra la API de paquetes publicables `.co`: publicación, búsqueda, instalación, caché local y lectura de metadatos. El comando `cobra hub publicar|buscar|instalar` usa esta capa.
- **Compatibilidad:** los métodos `publicar_paquete`, `buscar_paquetes` e `instalar_paquete` siguen disponibles en `CobraHubClient`, pero delegan en `CobraHubPackages`. El código nuevo debería importar `CobraHubPackages` directamente.

## Auditoría inicial

- La implementación previa de CobraHub estaba en `src/pcobra/cobra/cli/cobrahub_client.py` y se centraba en publicar/descargar módulos sueltos `.co` mediante endpoints `/modulos`.
- La integración del IDLE está en `src/pcobra/gui/idle.py`, con lógica compartida en `src/pcobra/gui/runtime.py`.
- Antes de esta evolución, `src/pcobra/cobra/cli/commands/package_cmd.py` creaba ZIPs simples con `cobra.pkg`, solo aceptaba `.co` y no preservaba documentación, Dockerfile ni recursos arbitrarios.
- La documentación contenía una inconsistencia: indicaba que `.cobra` representaba paquetes completos y `.co` scripts individuales, mientras otras secciones, tests y ejemplos usan ambos como fuentes Cobra. Ahora los paquetes publicables `.co` se gestionan como contenedores en la capa de herramientas.

## Diseño

La funcionalidad se implementa en `pcobra.cobra.packaging`, una capa independiente que no importa ni ejecuta Lexer/Parser. El paquete `.co` es un archivo ZIP con:

- `cobra.pkg.json` como manifiesto.
- Lista de archivos conservando carpetas.
- Checksums SHA-256 por archivo.
- Soporte para `.cobra`, `.co`, `.md`, `.txt`, `Dockerfile` y recursos.

## Tareas implementadas

1. Crear módulo independiente de empaquetado.
2. Sustituir el comando `cobra paquete` por acciones crear/validar/construir/inspeccionar/extraer e instalar como alias legacy.
3. Añadir `cobra hub publicar|buscar|instalar` para paquetes.
4. Separar la API CobraHub de paquetes en `pcobra.cobra.cli.cobrahub_packages`, con publicación, búsqueda, instalación, caché local y lectura de metadatos.
5. Mantener `pcobra.cobra.cli.cobrahub_client` como cliente HTTP base/fachada compatible y `modulos` en el flujo legacy de módulos.
6. Añadir acciones del IDLE que reutilizan la misma lógica de empaquetado.
7. Añadir pruebas unitarias de construcción, validación, inspección y extracción.

## Por qué no se toca Lexer ni Parser

El cambio opera exclusivamente sobre archivos, ZIPs, manifiestos y transporte CobraHub. No añade tokens, reglas gramaticales ni sintaxis Cobra. Los archivos fuente incluidos se tratan como bytes hasta que el usuario decida ejecutarlos con los comandos existentes.
