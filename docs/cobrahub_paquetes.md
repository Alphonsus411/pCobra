# CobraHub y paquetes `.co`

La guía de uso actualizada para crear, construir, validar, inspeccionar y extraer paquetes está en [`docs/frontend/paquetes.rst`](frontend/paquetes.rst).

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
4. Ampliar el cliente CobraHub con publicación, búsqueda, instalación y caché local.
5. Añadir acciones del IDLE que reutilizan la misma lógica de empaquetado.
6. Añadir pruebas unitarias de construcción, validación, inspección y extracción.

## Por qué no se toca Lexer ni Parser

El cambio opera exclusivamente sobre archivos, ZIPs, manifiestos y transporte CobraHub. No añade tokens, reglas gramaticales ni sintaxis Cobra. Los archivos fuente incluidos se tratan como bytes hasta que el usuario decida ejecutarlos con los comandos existentes.
