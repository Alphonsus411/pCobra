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


## Códigos de salida CLI

`cobra installer build` y el alias `cobra build --installer` comparten la misma implementación de la capa CLI, por lo que devuelven los mismos códigos de salida para los mismos fallos. Los códigos públicos son:

| Código | Nombre | Significado |
|---:|---|---|
| `0` | éxito | El artefacto se generó correctamente. |
| `10` | proyecto inválido | La estructura del proyecto, `cobra.toml` o el entrypoint no son válidos. |
| `11` | dependencia inexistente | Falta una ruta, recurso, paquete CobraHub o dependencia requerida. |
| `12` | conflicto de versiones | Versiones declaradas, transitivas o bloqueadas son incompatibles. |
| `13` | hash incorrecto | Un hash, checksum o SHA-256 no coincide con el valor esperado. |
| `14` | PyInstaller no disponible | PyInstaller no está instalado o no puede importarse en el Python activo. |
| `15` | target inválido | El sistema operativo objetivo solicitado no es válido o no está soportado. |
| `70` | error interno inesperado | Fallo no clasificado en la frontera CLI del instalador. |

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

## Checklist de aceptación QA

Este checklist valida que Cobra Installer funciona de extremo a extremo sin exponer detalles internos de PyInstaller al usuario final y sin introducir regresiones en otros subsistemas. Debe ejecutarse antes de cerrar una entrega funcional del empaquetador o de publicar artefactos generados por `cobra installer`.

### Entradas de usuario y puentes

- [ ] `cobra installer build .` construye correctamente un artefacto desde la raíz de un proyecto Cobra válido.
- [ ] `cobra build --installer .` funciona como alias público y produce el mismo resultado observable que `cobra installer build .`.
- [ ] El botón **Empaquetar** del IDLE invoca el puente `pcobra.cobra_installer.idle_bridge.package_current_project()` y no llama directamente a PyInstaller ni duplica lógica de manifiesto.
- [ ] PyInstaller queda oculto para el usuario: los flujos CLI e IDLE hablan de empaquetado Cobra, muestran errores accionables y no requieren que el usuario conozca el `.spec` ni el comando interno de PyInstaller salvo en logs técnicos o metadatos de diagnóstico.

### Proyectos y recursos

- [ ] Un proyecto mínimo con `main.cobra` o `cobra.toml` empaqueta correctamente.
- [ ] Un proyecto con assets, configuración, documentación o recursos auxiliares empaqueta correctamente y conserva esos recursos en el artefacto final.
- [ ] Las dependencias CobraHub declaradas se resuelven, se copian al runtime preparado y quedan reflejadas en el manifiesto.
- [ ] La caché del instalador se usa cuando contiene un paquete CobraHub válido, evitando descargas innecesarias.
- [ ] El lockfile `cobra.lock` se genera cuando no existe o se valida cuando ya existe.
- [ ] Un paquete CobraHub con hash incorrecto falla con el código/diagnóstico público de hash incorrecto.
- [ ] Un conflicto de versiones directo o transitivo falla con el código/diagnóstico público de conflicto de versiones.

### Modos de salida, targets y manifiesto

- [ ] `--mode onefile` genera un artefacto OneFile ejecutable en el sistema operativo objetivo.
- [ ] `--mode onedir` genera una carpeta OneDir ejecutable con sus bibliotecas y recursos.
- [ ] Un intento de cross-compilation muestra una advertencia clara indicando la limitación de PyInstaller y recomendando construir en el sistema operativo objetivo o en un builder nativo.
- [ ] Se genera `dist/cobra_build_manifest.json` y contiene, como mínimo, entrypoint, target, modo, versión de Cobra, versión de PyInstaller, hashes disponibles, recursos incluidos y dependencias resueltas.

### Regresión de subsistemas Cobra

- [ ] Lexer sigue pasando sus pruebas existentes.
- [ ] Parser sigue pasando sus pruebas existentes.
- [ ] AST sigue pasando sus pruebas existentes.
- [ ] Runtime sigue pasando sus pruebas existentes.
- [ ] Corelibs/standard library siguen pasando sus pruebas existentes.
- [ ] Transpiladores siguen pasando sus pruebas existentes.
- [ ] CobraHub sigue pasando sus pruebas existentes.
- [ ] IDLE sigue pasando sus pruebas existentes, incluido el flujo del botón **Empaquetar**.

### Evidencia mínima sugerida

- [ ] Adjuntar salida de `cobra installer build .` sobre un proyecto mínimo.
- [ ] Adjuntar salida de `cobra build --installer .` sobre el mismo proyecto o un fixture equivalente.
- [ ] Adjuntar rutas del artefacto OneFile, artefacto OneDir y `dist/cobra_build_manifest.json`.
- [ ] Adjuntar evidencia de cache hit, generación/validación de `cobra.lock`, hash incorrecto y conflicto de versiones.
- [ ] Adjuntar lista de comandos de regresión ejecutados para Lexer, Parser, AST, runtime, corelibs, transpiladores, CobraHub e IDLE.

## Checklist rápido antes de publicar

- Ejecuta el artefacto en una máquina limpia del mismo sistema operativo objetivo.
- Conserva `cobra_build_manifest.json` con el binario.
- Prefiere `onedir` para depurar y `onefile` solo cuando un único archivo sea prioritario.
- Usa CI con matriz de SO para releases multiplataforma.
- Si hay recursos externos, verifica que aparezcan en `assets_included` o en las secciones de recursos del manifiesto.
