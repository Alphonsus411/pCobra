# Arquitectura de Cobra Installer

Este documento describe la arquitectura actual de `cobra installer build` y del empaquetado desde el IDLE. Los nombres de módulos, clases y funciones se mantienen alineados con la implementación real de `pcobra.cobra_installer` y con los puntos de entrada CLI/GUI existentes.

## Diagrama textual del flujo

```text
Usuario CLI
  ├─ cobra installer build <proyecto>
  │    └─ pcobra.cobra.cli.commands_v2.installer_cmd.InstallerCommandV2.run()
  │       └─ run_installer_build(args)
  │          └─ pcobra.cobra_installer.build_project(project_path, BuildOptions)
  └─ cobra build --installer <proyecto>
       └─ pcobra.cobra.cli.commands_v2.build_cmd.BuildCommandV2.run()
          └─ run_installer_build(args)
             └─ pcobra.cobra_installer.build_project(project_path, BuildOptions)

Usuario IDLE
  └─ pcobra.gui.idle.main()
     └─ diálogo de empaquetado
        └─ pcobra.cobra_installer.idle_bridge.package_current_project()
           └─ pcobra.cobra_installer.runtime_builder.build_project()

build_project()
  ├─ validate_build_options(BuildOptions)
  ├─ resolve_build_backend(options.builder)
  ├─ discover_project(project_root)
  │  ├─ collect_project_resources(root)
  │  ├─ find_entrypoint(root)
  │  └─ lectura de cobra.toml
  ├─ validate_project(CobraProject)
  ├─ resolve_project_dependencies(root)
  │  ├─ read_declared_dependencies(cobra.toml)
  │  ├─ detect_cobra_imports(root)
  │  ├─ read_lockfile(cobra.lock), si existe
  │  ├─ CobraHubResolver.resolve(name, version, expected_sha256, source)
  │  │  ├─ CobraInstallerCache.candidates()/validate()
  │  │  ├─ PackageRepository.download(), si hay repositorio configurado
  │  │  └─ es_paquete_cobra()/validar_paquete()/inspeccionar_paquete()
  │  └─ write_lockfile(cobra.lock), si no existía
  ├─ transpile_project(project, build_dir, options, dependencies)
  │  ├─ prevalidar_y_parsear_codigo(source)
  │  ├─ PythonAdapter().compile(ast, metadata)
  │  └─ copia runtime, paquetes, assets, config, docs y recursos auxiliares
  ├─ _runtime_from_transpile(TranspileResult)
  ├─ write_spec(SpecBuildContext)
  ├─ BuildBackend.run_pyinstaller(spec_path, options, logger)
  │  └─ LocalPyInstallerBuilder → pyinstaller_runner.run_pyinstaller()
  ├─ create_manifest(options, entrypoint, output_dir, name)
  └─ BuildResult(success=True, artifact_path=..., metadata=..., logs=...)
```

## Responsabilidades por módulo

| Módulo | Responsabilidad principal |
| --- | --- |
| `pcobra.cobra_installer.__init__` | Fachada pública del paquete; exporta `BuildOptions`, `BuildResult`, `build_project`, `package_current_project`, `prepare_runtime`, builders, targets, manifest y validadores. |
| `pcobra.cobra_installer.project` | Modelos base (`CobraProject`, `BuildOptions`, `BuildResult`, `ProjectResources`), error controlado `CobraInstallerError`, descubrimiento de proyecto (`discover_project`), entrypoint (`find_entrypoint`) y recursos (`collect_project_resources`). |
| `pcobra.cobra_installer.validator` | Validación de `BuildOptions` y `CobraProject`; normaliza target/modo/builder antes de construir. |
| `pcobra.cobra_installer.targets` | Contrato de targets (`TargetOS`), modos (`BuildMode`), builders reservados (`BuilderKind`/`Builder`), configuración (`BuilderConfig`), artefactos esperados y advertencia de cross-compilation. |
| `pcobra.cobra_installer.dependency_resolver` | Contrato de dependencias Cobra: lee `cobra.toml`, detecta imports, valida `cobra.lock`, resuelve transitivas, detecta conflictos y escribe lock cuando procede. |
| `pcobra.cobra_installer.hub_resolver` | Contrato CobraHub por paquete: cache/ruta explícita/repositorio, validación `.co`, nombre, versión, SHA-256 y dependencias declaradas por el paquete. |
| `pcobra.cobra_installer.cache` | Caché local de paquetes para el instalador; provee candidatos y validación usada por `CobraHubResolver`. |
| `pcobra.cobra_installer.transpile` | Transpilación oficial a Python mediante `prevalidar_y_parsear_codigo()` y `PythonAdapter().compile()`; genera `python/<entrypoint>.py`, `python/__main__.py` y copia runtime/recursos. |
| `pcobra.cobra_installer.runtime_builder` | Orquestador principal. `build_project()` coordina validación, dependencias, transpilación, runtime, `.spec`, PyInstaller, manifiesto y `BuildResult`. `package_current_project()` es la entrada programática simple. |
| `pcobra.cobra_installer.spec_writer` | Traduce el runtime preparado y `BuildOptions` a un `.spec` de PyInstaller mediante `SpecBuildContext` y `write_spec()`. |
| `pcobra.cobra_installer.pyinstaller_runner` | Ejecución concreta de PyInstaller, detección/instalación opcional y resultado `PyInstallerRunResult`. |
| `pcobra.cobra_installer.builders` | Abstracción `BuildBackend`; implementación actual `LocalPyInstallerBuilder`; reserva explícita para `docker`, `vm`, `ci` y `remote` mediante `resolve_build_backend()`. |
| `pcobra.cobra_installer.manifest` | Generación de `dist/cobra_build_manifest.json`, alias heredado y cálculo de la ruta de artefacto esperada. |
| `pcobra.cobra_installer.logger` | Eventos de progreso (`BuildLogger`, `ProgressEvent`) y compatibilidad con callbacks legados. |
| `pcobra.cobra_installer.idle_bridge` | Puente delgado IDLE → instalador: traduce opciones de UI a `BuildOptions`, conecta callbacks y convierte errores a mensajes de usuario. |
| `pcobra.cobra_installer.cli` | CLI mínima directa `cobra-installer`; el flujo público Cobra usa los comandos v2 de `pcobra.cobra.cli.commands_v2`. |
| `pcobra.cobra.cli.commands_v2.installer_cmd` | Comando público `cobra installer build`; construye `BuildOptions`, llama `cobra_installer.build_project()` y mapea errores a códigos de salida. |
| `pcobra.cobra.cli.commands_v2.build_cmd` | Alias público `cobra build --installer`; reutiliza los argumentos y `run_installer_build()` de `installer_cmd`. |
| `pcobra.gui.idle` | Interfaz gráfica: muestra diálogo de empaquetado, recopila nombre/target/modo/icono/instalación de PyInstaller y delega en `idle_bridge.package_current_project()`. |

## Contrato entre CLI, IDLE y `build_project`

### Entrada CLI

- `InstallerCommandV2` registra `cobra installer build` y `register_installer_build_arguments()` define el contrato de opciones públicas: `project_path`, `--target`, `--mode`, `--name`, `--icon`, `--builder`, `--install-pyinstaller` y `--no-open-dist`.
- `BuildCommandV2` expone `cobra build --installer` como alias. Cuando `--installer` está activo, asigna `args.project_path = args.file or "."` y delega en el mismo `run_installer_build(args)`.
- `run_installer_build()` debe ser la única frontera CLI hacia el instalador moderno: crea un `BuildOptions`, llama `pcobra.cobra_installer.build_project(args.project_path, options)`, imprime el artefacto final y transforma errores controlados en códigos `CobraExitCode`.

### Entrada IDLE

- `pcobra.gui.idle` no ejecuta PyInstaller ni interpreta manifiestos. Su responsabilidad es detectar el proyecto activo, presentar controles de usuario y llamar a `pcobra.cobra_installer.idle_bridge.package_current_project()`.
- `idle_bridge.package_current_project(project_path, ui_options, progress_callback, error_callback)` acepta opciones en forma de `Mapping` u objeto, traduce aliases de UI (`nombre`, `salida`, `objetivo`, `modo`, `instalar_pyinstaller`, etc.) a campos de `BuildOptions`, conecta `progress_callback` como `log_callback` y devuelve `IdlePackageResult(executable_path, dist_dir)`.
- Los errores `CobraInstallerError` no se filtran crudos al usuario del IDLE: el puente los convierte a `RuntimeError` con el prefijo `No se pudo empaquetar el proyecto Cobra:` y opcionalmente llama `error_callback`.

### Núcleo `build_project`

- Firma estable: `build_project(project_path: Path | str | BuildOptions | None = None, options: BuildOptions | None = None, **overrides) -> BuildResult`.
- Compatibilidad: si el primer argumento es `BuildOptions` y `options` es `None`, se usa esa instancia como base; en caso contrario, `project_path` sobreescribe `options.project_root`. `**overrides` se aplica mediante `dataclasses.replace()`.
- `build_project()` es responsable de emitir progreso por `BuildOptions.log_callback` mediante `BuildLogger`; CLI e IDLE sólo consumen mensajes, no inspeccionan pasos internos.
- Resultado estable: `BuildResult` debe indicar `success`, `artifact_path`, `project_root`, `output_dir`, `target`, `architecture`, `builder`, `mode`, `executable_name`, `temp_dir`, `dist_dir`, `pyinstaller_version`, `metadata` (`entrypoint`, `generated_code`, `manifest`, `spec`, `name`, `pyinstaller_command`) y `logs`.

## Contrato de resolución CobraHub

- La resolución de proyecto empieza en `resolve_project_dependencies(project_root, resolver=None, fail_on_unused_declared=False)`.
- Declaraciones admitidas por `read_declared_dependencies()`:
  - `[dependencies] paquete = "1.2.3"`
  - `[cobra.dependencies] paquete = "1.2.3"`
  - `[project] dependencies = ["paquete==1.2.3"]`
- `detect_cobra_imports()` detecta imports Cobra usados en archivos del proyecto y exige que todo import usado esté declarado; si falta alguno, lanza `CobraDependencyError`.
- Si existe `cobra.lock`, `read_lockfile()` valida versión, fuente y SHA-256 esperados. Si no existe, `write_lockfile()` persiste el resultado resuelto.
- `CobraHubResolver.resolve()` normaliza nombre y versión, prueba primero `source` explícito y caché local (`CobraInstallerCache`), y sólo descarga por `PackageRepository.download()` si hay repositorio configurado.
- Cada paquete `.co` resuelto debe pasar `es_paquete_cobra()`, `validar_paquete()` e `inspeccionar_paquete()`; el manifiesto interno debe declarar el mismo nombre y versión solicitados.
- Si se proporciona `expected_sha256`, el digest del paquete debe coincidir exactamente después de quitar un prefijo opcional `sha256:`.
- Las dependencias transitivas declaradas por paquetes CobraHub se incorporan a la cola de resolución; versiones incompatibles producen `CobraDependencyError` con cadena de dependencia.
- El resultado estable es `DependencyResolutionResult(declared, used_imports, resolved, lockfile_path, lockfile_created, conflicts, missing_declarations)`.

## Contrato de transpilación oficial

- La única transpilación usada por Cobra Installer es `pcobra.cobra_installer.transpile.transpile_project()`.
- El target de generación es Python oficial: se parsea con `prevalidar_y_parsear_codigo(source)` y se compila con `PythonAdapter().compile(ast, {"source_file": entrypoint, "project_root": root})`.
- Este contrato no modifica Lexer, Parser, AST ni transpiladores; sólo consume el pipeline público existente.
- La salida mínima de transpilación es:
  - `build_dir/python/<entrypoint>.py` con el código generado.
  - `build_dir/python/__main__.py` como entrypoint ejecutable por `runpy`.
  - `build_dir/runtime/pcobra` con runtime/corelibs/standard_library necesarios.
  - `build_dir/packages`, `assets`, `config`, `docs` y `resources` con paquetes y recursos copiados.
- Si `include_dependencies=True`, `transpile_project()` recibe o genera `DependencyResolutionResult` y copia los paquetes CobraHub resueltos junto a paquetes `.co` locales.
- El resultado estable es `TranspileResult`, que además conserva `copied_resources`, `dependency_resolution` y mensajes `logs` para el orquestador.

## Contrato de generación PyInstaller

- `runtime_builder.build_project()` no invoca PyInstaller directamente: selecciona un backend con `resolve_build_backend(normalized.builder)`.
- El único backend implementado es `LocalPyInstallerBuilder`, que cumple el protocolo `BuildBackend` y delega en `pyinstaller_runner.run_pyinstaller(spec_path, options, logger)`.
- Antes de ejecutar PyInstaller, `write_spec(SpecBuildContext(options, runtime, output_dir, executable_name))` debe generar el `.spec` usando el entrypoint Python preparado, rutas de runtime/paquetes/recursos, modo `onefile` o `onedir`, icono opcional y directorios de salida/build.
- `pyinstaller_runner.run_pyinstaller()` es la frontera para detectar PyInstaller, instalarlo opcionalmente cuando `BuildOptions.install_pyinstaller=True`, ejecutar el comando y devolver `PyInstallerRunResult` con versión y comando usado.
- Después de PyInstaller, `create_manifest()` escribe el manifiesto de build y `expected_artifact_path()` calcula la ruta esperada del artefacto según target y modo.
- El comando CLI debe tratar ausencia de PyInstaller como error público accionable y mapearla a `CobraExitCode.PYINSTALLER_UNAVAILABLE` cuando corresponda.

## Límites conocidos de cross-compilation

- `TargetOS` admite `windows`, `linux`, `macos` y el alias `current`; `normalize_target()` convierte `current` al host detectado por `detect_host_os()`.
- `validate_target()` emite `RuntimeWarning` con `CROSS_COMPILATION_WARNING` cuando el target no coincide con el host.
- PyInstaller no soporta cross-compilation general entre sistemas operativos. Un binario Windows debe construirse en Windows; un binario Linux, en Linux; y un bundle/binario macOS, en macOS.
- En el estado actual, `--target` documenta intención y forma esperada de artefacto, pero no convierte el host en compilador de otro sistema operativo.
- `docker`, `vm`, `ci` y `remote` están reservados para aislar builds futuros. Hoy `resolve_build_backend()` falla explícitamente para esos valores y recomienda usar `builder='local'`.
- Para builds no nativos, la estrategia soportada conceptualmente es ejecutar Cobra Installer dentro del entorno nativo correspondiente: contenedor/runner Linux para Linux, VM o host Windows para Windows, runner macOS para macOS, y pasos externos de firma/notarización cuando apliquen.

## Puntos de extensión para builders futuros

- Implementar una nueva clase que cumpla `BuildBackend`: atributo `kind: BuilderKind` y método `run_pyinstaller(spec_path: Path, options: BuildOptions, logger: BuildLogger) -> PyInstallerRunResult`.
- Extender `resolve_build_backend()` para devolver la implementación concreta cuando `BuilderKind.DOCKER`, `BuilderKind.VM`, `BuilderKind.CI` o `BuilderKind.REMOTE` esté disponible.
- Usar `BuilderConfig` como contrato de configuración: `image` para Docker, `vm_name` para VM, `ci_runner` para CI/CD y `remote_url` para builders remotos.
- Mantener `BuildOptions.builder` y `BuildOptions.builder_config` como la única entrada de selección/configuración del builder. No añadir flags específicos al orquestador si pueden representarse en `BuilderConfig`.
- Preservar la frontera del orquestador: los builders futuros deben consumir el `.spec`, el árbol temporal y las opciones normalizadas; no deben duplicar `discover_project()`, `resolve_project_dependencies()`, `transpile_project()` ni `write_spec()` salvo que implementen una estrategia documentada equivalente.
- Devolver siempre un `PyInstallerRunResult` compatible para que `build_project()` pueda seguir escribiendo manifiesto, `BuildResult.metadata["pyinstaller_command"]` y `pyinstaller_version` sin ramas por backend.
- Si un builder remoto genera el artefacto fuera del host local, debe materializar o sincronizar el resultado final en `BuildOptions.output_dir`/`dist_dir` antes de regresar para mantener estable `BuildResult.artifact_path`.
