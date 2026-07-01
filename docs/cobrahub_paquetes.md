# CobraHub y paquetes `.co`

La guía de uso actualizada para crear, construir, validar, inspeccionar y extraer paquetes está en [`docs/frontend/paquetes.rst`](frontend/paquetes.rst).


## Arquitectura sin cambios gramaticales

Los paquetes `.co` son contenedores ZIP con manifiesto `cobra.pkg.json`. La detección usa `zipfile` y comprueba la presencia de `cobra.pkg.json` en la raíz del contenedor; los archivos `.cobra` o `.co` incluidos dentro del ZIP se tratan como recursos hasta que el usuario decida ejecutarlos o editarlos explícitamente.

Esta capacidad vive en `pcobra.cobra.packaging` como capa independiente de empaquetado y distribución. No introduce palabras clave, tokens ni reglas gramaticales nuevas; por tanto no se modifica `src/pcobra/core/lexer.py`, `src/pcobra/core/parser.py` ni los módulos canónicos bajo `src/pcobra/cobra/core/`.

## Fuente de verdad del empaquetado `.co`

`pcobra.cobra.packaging` es el contrato público y la fuente de verdad para paquetes Cobra `.co`. Las funciones públicas son `crear_paquete`, `validar_paquete`, `construir_paquete`, `extraer_paquete`, `inspeccionar_paquete`, `verificar_integridad` y `es_paquete_cobra`; CLI, IDLE y CobraHub deben importarlas y delegar en ellas en vez de duplicar la lógica de ZIP, manifiestos o checksums.

## APIs CobraHub: legacy y recomendada

- **Legacy de módulos:** `src/pcobra/cobra/cli/cobrahub_client.py` mantiene el cliente HTTP base y la fachada compatible para publicar/descargar módulos sueltos con los endpoints `/modulos`. El comando `modulos` sigue apuntando a este flujo para no romper scripts existentes.
- **Ruta recomendada para paquetes:** `src/pcobra/cobra/cli/cobrahub_packages.py` concentra la API de paquetes publicables `.co`: publicación, búsqueda, instalación, caché local y lectura de metadatos. El comando `cobra hub publicar|buscar|instalar` usa esta capa.
- **Compatibilidad:** los métodos `publicar_paquete`, `buscar_paquetes` e `instalar_paquete` siguen disponibles en `CobraHubClient`, pero delegan en `CobraHubPackages`. El código nuevo debería importar `CobraHubPackages` directamente.


## Contrato `PackageRepository`

`PackageRepository` es el contrato interno que desacopla las operaciones de repositorio de paquetes del transporte concreto y del resto del lenguaje. La capa de comandos de CobraHub delega en esta interfaz para publicar, buscar, descargar y leer metadatos de paquetes `.co`, mientras Lexer y Parser permanecen ajenos al formato de distribución.

La interfaz actual expone cuatro operaciones:

- `publish(package_path, metadata, checksum)`: publica un paquete local ya validado. `package_path` apunta al artefacto `.co`, `metadata` contiene los metadatos normalizados que se indexarán y `checksum` identifica el contenido esperado para verificar integridad durante la publicación.
- `search(query)`: busca paquetes a partir de una consulta textual y devuelve resultados normalizados para que la CLI pueda mostrarlos o usarlos en flujos posteriores.
- `download(name, version=None)`: descarga un paquete por nombre canónico. `version` es opcional; si no se proporciona, el repositorio puede resolver la versión por defecto o más reciente según su política actual.
- `read_metadata(package_path)`: lee y normaliza los metadatos de un paquete `.co` local, validando que sea un paquete Cobra antes de exponer su manifiesto.

La implementación HTTP actual (`HttpCobraHubRepository`) usa endpoints provisionales mientras el servicio evoluciona:

- `POST /paquetes` para `publish(package_path, metadata, checksum)`.
- `GET /paquetes?q=...` para `search(query)`.
- `GET /paquetes/{nombre}` para `download(name, version=None)`, con `version` como parámetro opcional cuando se quiere una versión concreta.

`read_metadata(package_path)` es una operación local: reutiliza la validación del paquete `.co` y no requiere endpoint HTTP.

Quedan fuera de alcance por ahora la resolución transitiva de dependencias, la autenticación compleja, las firmas criptográficas, un índice global completo, el yanking o deprecación de versiones y los mirrors. Esas capacidades podrán incorporarse detrás de nuevas implementaciones de `PackageRepository` o de extensiones compatibles del contrato, sin cambiar el Lexer ni el Parser. Esta separación permite evolucionar CobraHub hacia un repositorio tipo PyPI manteniendo estable la sintaxis del lenguaje y aislando el formato de distribución en la capa de empaquetado/repositorio.

## Contrato HTTP mínimo

Esta especificación define el contrato HTTP mínimo que debe implementar un
servicio CobraHub para publicar, buscar y descargar paquetes Cobra `.co`. Es
una especificación provisional: describe el intercambio estable necesario para
los clientes actuales, pero deja espacio para evolucionar hacia una
infraestructura de índice y distribución más completa, compatible con un modelo
tipo PyPI (metadatos enriquecidos, versiones múltiples, mirrors, autenticación,
firmas y APIs adicionales).

### `POST /paquetes`

Publica un paquete Cobra `.co` en CobraHub. La petición debe enviarse como
`multipart/form-data` e incluir:

- Campo multipart `file`: archivo binario `.co` que se quiere publicar.
- Campo multipart `metadata`: metadatos serializados, preferentemente JSON, con
  la información del paquete que el servidor necesite indexar (por ejemplo
  `name`, `version`, `description` o etiquetas).
- Cabecera `X-Content-Checksum`: checksum esperado del contenido enviado,
  calculado por el cliente para que el servidor pueda verificar integridad antes
  de aceptar la publicación. Se recomienda SHA-256 en formato hexadecimal.
- Cabecera `Idempotency-Key`: identificador único de la operación de
  publicación. El servidor debe usarlo para evitar publicaciones duplicadas si
  el cliente reintenta la misma petición por errores de red o timeouts.

Respuesta mínima recomendada:

```json
{
  "name": "demo",
  "version": "0.1.0",
  "filename": "demo-0.1.0.co",
  "checksum": "sha256:...",
  "download_url": "https://cobrahub.example/paquetes/demo?version=0.1.0",
  "remote_id": "pkg_..."
}
```

### `GET /paquetes?q=consulta`

Busca paquetes publicados. El parámetro `q` contiene la consulta textual que
se aplicará sobre el índice del servidor. La respuesta esperada es JSON y debe
contener una lista de resultados normalizados. Para mantener compatibilidad con
clientes sencillos, el servidor puede devolver directamente una lista o envolver
la lista en un objeto con la clave `results`.

Formato recomendado:

```json
{
  "results": [
    {
      "name": "demo",
      "version": "0.1.0",
      "filename": "demo-0.1.0.co",
      "checksum": "sha256:...",
      "download_url": "https://cobrahub.example/paquetes/demo?version=0.1.0",
      "remote_id": "pkg_..."
    }
  ]
}
```

Campos normalizados por resultado:

- `name`: nombre canónico del paquete.
- `version`: versión publicada del paquete.
- `filename`: nombre del archivo `.co` disponible para descarga.
- `checksum`: checksum del artefacto descargable, preferentemente SHA-256.
- `download_url`: URL absoluta o relativa que el cliente puede usar para
  descargar el paquete.
- `remote_id`: identificador interno estable asignado por el servidor.

### `GET /paquetes/{nombre}`

Descarga el artefacto binario asociado a un paquete. `{nombre}` identifica el
paquete por su nombre canónico. La petición acepta el parámetro opcional
`version` para seleccionar una versión concreta:

```text
GET /paquetes/demo?version=0.1.0
```

Si `version` no se proporciona, el servidor puede devolver la versión marcada
como más reciente o la versión por defecto de acuerdo con su política de índice.
La respuesta debe ser el binario `.co` sin envolver en JSON. Se recomienda usar
`Content-Type: application/octet-stream` o un tipo específico de paquete Cobra
si el servidor lo define en el futuro.

Cabeceras esperadas en la respuesta:

- `X-Content-Checksum`: checksum del cuerpo binario devuelto, para que el
  cliente pueda verificar la integridad tras la descarga.
- `X-Package-Version` (opcional): versión exacta del paquete devuelto. Es útil
  cuando el cliente no envió `version` y el servidor resolvió automáticamente
  una versión.

## Auditoría inicial

- La implementación previa de CobraHub estaba en `src/pcobra/cobra/cli/cobrahub_client.py` y se centraba en publicar/descargar módulos sueltos `.co` mediante endpoints `/modulos`.
- La integración del IDLE está en `src/pcobra/gui/idle.py`, con lógica compartida en `src/pcobra/gui/runtime.py`.
- Antes de esta evolución, `src/pcobra/cobra/cli/commands/package_cmd.py` creaba ZIPs simples con `cobra.pkg`, solo aceptaba `.co` y no preservaba documentación, Dockerfile ni recursos arbitrarios.
- La documentación contenía una inconsistencia: indicaba que `.cobra` representaba paquetes completos y `.co` scripts individuales, mientras otras secciones, tests y ejemplos usan ambos como fuentes Cobra. Ahora los paquetes publicables `.co` se gestionan como contenedores en la capa de herramientas.

## Diseño

La funcionalidad se implementa en `pcobra.cobra.packaging`, una capa independiente que no importa ni ejecuta Lexer/Parser y que actúa como fuente de verdad del formato. El paquete `.co` es un archivo ZIP con:

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


## Contrato de validación e integridad CLI

- `cobra paquete validar <artefacto.co>` comprueba que el archivo sea un paquete
  Cobra válido: ZIP legible con `cobra.pkg.json`, manifiesto completo, lista de
  archivos coherente y checksums declarados para el contenido.
- `cobra paquete verificar <artefacto.co>` es el alias explícito para integridad:
  recalcula y compara los hashes SHA-256 de los archivos declarados en el
  manifiesto antes de publicar, instalar o confiar en el artefacto.
- `cobra paquete integridad <artefacto.co>` se conserva como alias legacy de
  `verificar` para no romper scripts existentes; el código nuevo debe preferir
  `verificar`.

## Regla de detección de paquetes `.co`

Un archivo `.co` solo se considera paquete Cobra cuando cumple ambas condiciones estructurales:

1. El archivo es un ZIP legible.
2. El ZIP contiene `cobra.pkg.json` en la raíz.

La extensión `.co` por sí sola no basta: un `.co` de texto sigue siendo fuente Cobra, y un ZIP `.co` sin `cobra.pkg.json` no es un paquete Cobra válido. Esta comprobación vive en `pcobra.cobra.packaging.es_paquete_cobra()` y no invoca Lexer ni Parser. Los comandos de empaquetado y CobraHub usan esta regla antes de validar, publicar, instalar o leer metadatos de paquetes.

## Por qué no se toca Lexer ni Parser

El cambio opera exclusivamente sobre archivos, ZIPs, manifiestos y transporte CobraHub. No añade tokens, reglas gramaticales ni sintaxis Cobra. Los archivos fuente incluidos se tratan como bytes hasta que el usuario decida ejecutarlos con los comandos existentes.
