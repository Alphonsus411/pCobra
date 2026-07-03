# Cobra Installer: empaquetado de proyectos Cobra

`cobra installer` construye ejecutables o carpetas distribuibles de proyectos Cobra usando la capa `pcobra.cobra_installer` y PyInstaller. Es el flujo recomendado para convertir un proyecto con `main.cobra` o `cobra.toml` en un artefacto instalable.

## Uso desde el IDLE gráfico

1. Abre el IDLE con `cobra gui`.
2. Crea o abre un proyecto Cobra.
3. Comprueba que el proyecto tenga un `main.cobra` en la raíz o un `entrypoint`/`main`/`source`/`script` configurado en `cobra.toml`.
4. Pulsa el botón **Empaquetar**.
5. En el diálogo, elige el modo de salida:
   - `onedir`: carpeta distribuible con el ejecutable y sus recursos.
   - `onefile`: ejecutable único.
6. Confirma con **Empaquetar** y revisa el progreso en el panel de salida.

El IDLE usa un puente delgado hacia `pcobra.cobra_installer.idle_bridge`; la interfaz no duplica la lógica de PyInstaller ni del manifiesto. Si no hay proyecto o ruta activa, el IDLE debe mostrar un mensaje indicando que primero hay que abrir o indicar un proyecto.

## Uso desde CLI

Flujo básico desde la raíz del proyecto:

```bash
cobra installer build .
```

Alias integrado en `cobra build`:

```bash
cobra build --installer .
```

Seleccionar sistema operativo objetivo declarado:

```bash
cobra installer build . --target windows
cobra installer build . --target linux
cobra installer build . --target macos
```

Opciones útiles:

```bash
cobra installer build . --mode onedir
cobra installer build . --mode onefile
cobra installer build . --name mi_app
cobra installer build . --icon assets/icon.ico
cobra installer build . --install-pyinstaller
cobra installer build . --builder docker
cobra installer build . --builder vm
cobra installer build . --builder ci
cobra installer build . --builder remote
```

Valores principales:

| Opción | Valores | Uso |
|---|---|---|
| `--target` | `current`, `windows`, `linux`, `macos` | Declara el sistema operativo objetivo. |
| `--mode` | `onedir`, `onefile` | Controla si el resultado es carpeta o ejecutable único. |
| `--builder` | `local`, `docker`, `vm`, `ci`, `remote` | Documenta la estrategia de construcción recomendada. |
| `--name` | texto | Nombre del ejecutable. |
| `--icon` | ruta | Icono del artefacto, si PyInstaller lo soporta para la plataforma. |
| `--install-pyinstaller` | bandera | Permite instalar PyInstaller automáticamente si no está disponible. |

## OneDir y OneFile

### OneDir (`--mode onedir`)

`onedir` crea una carpeta dentro de `dist/` con el ejecutable, bibliotecas, módulos Python y recursos necesarios. Es el modo predeterminado y suele ser el más transparente para depurar.

Ventajas:

- Arranque más rápido que `onefile` en muchos casos.
- Errores de recursos faltantes más fáciles de diagnosticar.
- Permite inspeccionar qué archivos quedaron incluidos.

Costes:

- Distribuyes una carpeta completa, no un único archivo.
- Es más fácil que usuarios borren accidentalmente archivos necesarios.

### OneFile (`--mode onefile`)

`onefile` empaqueta el proyecto como un único ejecutable. PyInstaller extrae internamente los recursos en una ubicación temporal al iniciar.

Ventajas:

- Distribución sencilla: un archivo principal.
- Útil para demos, herramientas pequeñas y entregas manuales.

Costes:

- Inicio más lento por la extracción temporal.
- Diagnóstico más difícil si faltan datos o imports dinámicos.
- Antivirus o políticas corporativas pueden bloquear la extracción temporal.

## Limitaciones de cross-compilation con PyInstaller

PyInstaller no ofrece cross-compilation general entre sistemas operativos. En la práctica, un ejecutable de Windows debe construirse en Windows, uno de Linux en Linux y uno de macOS en macOS. La opción `--target` documenta la intención del build y ayuda a nombrar/rutar el artefacto, pero no convierte automáticamente un host Linux en compilador nativo de Windows o macOS.

Recomendación operativa:

- Para Windows: construir en Windows, una VM Windows, un runner CI Windows o un builder remoto Windows.
- Para Linux: construir en Linux, contenedor Docker Linux, runner CI Linux o builder remoto Linux.
- Para macOS: construir en macOS o runner CI macOS; la firma/notarización de Apple requiere pasos adicionales fuera de Cobra Installer.

## Docker, VM, CI y builder remoto

Usa `--builder` para dejar explícita la estrategia de construcción:

```bash
cobra installer build . --target linux --builder docker
cobra installer build . --target windows --builder vm
cobra installer build . --target macos --builder ci
cobra installer build . --target windows --builder remote
```

Recomendaciones:

- **Docker**: ideal para builds Linux reproducibles y para fijar versiones de Python, PyInstaller y dependencias.
- **VM**: útil para Windows/macOS cuando necesitas controlar una máquina completa o probar instaladores manualmente.
- **CI**: recomendado para publicar artefactos por release usando matrices de `windows`, `linux` y `macos`.
- **Builder remoto**: apropiado cuando el equipo local no tiene el sistema operativo objetivo, credenciales de firma o dependencias pesadas.

Aunque el builder sea remoto, conserva el manifiesto generado en `dist/cobra_build_manifest.json` junto al artefacto para auditoría y soporte.

## `cobra_build_manifest.json`

Cada build genera `dist/cobra_build_manifest.json`. También se escribe el alias heredado `cobra-installer-manifest.json` para integraciones antiguas.

El manifiesto registra información reproducible y de diagnóstico, incluyendo:

- `project`, `project_root` y `entrypoint`.
- `version`, `name` y `executable_name`.
- `target`, `architecture`, `mode` y `build_mode`.
- `cobra_version` y `pyinstaller_version`.
- `dist_dir`, `temp_dir`, `executable_path` e `icon`.
- `hashes` SHA-256 de entradas y artefactos disponibles.
- `dependencies` y `cobrahub_dependencies`.
- `assets`, `assets_included`, `co_packages`, `documentation`, `config_dirs` y `auxiliary_resources`.
- `generated_at`, `build_duration_seconds`, `runtime_included`, `final_size_bytes` e `include_dependencies`.

Usos recomendados:

- Adjuntarlo a releases junto al ejecutable.
- Comparar builds entre CI y entorno local.
- Diagnosticar qué entrypoint, recursos y versiones participaron en la construcción.
- Validar hashes antes de redistribuir binarios.

## Errores comunes y solución

| Error o síntoma | Causa habitual | Solución |
|---|---|---|
| `PyInstaller no disponible` | PyInstaller no está instalado o no es importable en el Python activo. | Ejecuta `pip install pyinstaller` o usa `cobra installer build . --install-pyinstaller`. |
| `No se encontró entrypoint Cobra` | No existe `main.cobra` y `cobra.toml` no declara entrada. | Crea `main.cobra` o configura un único `entrypoint`/`main`/`source`/`script` en `cobra.toml`. |
| `No se pudo determinar un entrypoint único` | Hay varios `.cobra` o varias entradas configuradas. | Deja solo una entrada explícita en `cobra.toml` o crea `main.cobra`. |
| `La ruta del proyecto no existe` | Se pasó una ruta incorrecta. | Ejecuta el comando desde la raíz correcta o usa una ruta absoluta válida. |
| `cobra.toml no es válido` | TOML mal formado. | Valida comillas, secciones y claves duplicadas antes de reconstruir. |
| `Permiso denegado` | Carpeta `build/` o `dist/` bloqueada, antivirus o permisos insuficientes. | Cierra ejecutables previos, limpia `build/`/`dist/`, revisa permisos y exclusiones de antivirus. |
| `Falta un archivo requerido` | Un recurso referenciado por el spec, icono o configuración no existe. | Corrige rutas y vuelve a ejecutar desde la raíz del proyecto. |
| `failed to execute script` al abrir el binario | Imports dinámicos o datos no incluidos. | Prueba `--mode onedir`, revisa recursos incluidos y añade configuración/spec si procede. |
| Build para otro SO no produce binario nativo | Limitación de cross-compilation de PyInstaller. | Construye en el mismo SO mediante Docker Linux, VM, CI o builder remoto. |
| El ejecutable tarda en arrancar | Modo `onefile` extrae datos temporalmente. | Usa `--mode onedir` para distribución interna o depuración. |

## Checklist rápido antes de publicar

- Ejecuta el artefacto en una máquina limpia del mismo sistema operativo objetivo.
- Conserva `cobra_build_manifest.json` con el binario.
- Prefiere `onedir` para depurar y `onefile` solo cuando un único archivo sea prioritario.
- Usa CI con matriz de SO para releases multiplataforma.
- Si hay recursos externos, verifica que aparezcan en `assets_included` o en las secciones de recursos del manifiesto.
