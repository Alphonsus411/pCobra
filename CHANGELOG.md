## v10.0.13 - 2026-03-29
- Fix: la CLI ya no depende de `scripts.benchmarks` en tiempo de ejecución.
- RuntimeManager ahora centraliza la validación de seguridad+ABI para `run`, `test` y `build` en CLI v2 mediante `validate_command_runtime`, evitando atajos directos fuera del manager.
- Se unificaron los mensajes de error por ruta contractual de bindings (`Python direct import`, `JavaScript runtime bridge`, `Rust compiled FFI`) con un prefijo canónico.
- Nuevas pruebas de contrato ABI que validan `abi_by_backend` y `backend_abi` leyendo `cobra.toml`/`pcobra.toml`.
- **Breaking changes de ABI (gobernanza):** cualquier cambio incompatible de ABI debe anunciarse explícitamente en changelog y registrarse con ADR dedicado antes de su liberación.

## v10.1.0 - 2025-08-24
- Integración completa de Hololang como lenguaje intermedio oficial del compilador.
- Reestructuración de la cadena de transpilación para emitir Hololang antes de despachar a cada backend.
- Incorporación del generador de ensamblador basado en el IR de Hololang y documentación asociada.

## v10.0.10 - Pendiente de liberación
- Saneamiento interno del Lexer/Parser: se eliminaron entradas duplicadas exactas en especificaciones y factories, sin introducir gramática nueva ni alterar precedencias.
- Refactor de `src/pcobra/__init__.py` para exponer submódulos con carga perezosa (`__getattr__`) y evitar imports ansiosos en `import pcobra`, manteniendo `activar_aliases_legacy()` para compatibilidad con rutas legacy (`cobra`, `core`) bajo activación explícita.
- Nuevas pruebas de import liviano para garantizar que `import pcobra` no requiere dependencias opcionales (como Flet) ni carga submódulos pesados de forma anticipada.
- **Breaking changes (política de targets retirados)**
  - Se define ventana formal de deprecación para nombres retirados/legacy: inicio en `v10.0.10` y eliminación definitiva en `v10.2.0`.
  - Alias históricos de CLI (`c++`, `ensamblador`) siguen funcionando temporalmente, pero ahora emiten `DeprecationWarning` con versión de retirada.
  - Nombres legacy/ambiguos retirados (`js`, `py`, `node`, `golang`, `jvm`, etc.) siguen rechazados y el error ahora incluye alternativa recomendada y fecha de eliminación definitiva.
  - Se añade `scripts/audit_retired_targets.py` para detectar proyectos/documentación/CI que todavía usen nombres retirados.
  - Migración recomendada: normalizar todo a nombres canónicos (`python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`) en scripts, docs y pipelines.
- Migración de la caché incremental a SQLitePlus con base en `~/.cobra/sqliteplus/core.db`.
- Nuevas variables de entorno `SQLITE_DB_KEY` (obligatoria) y `COBRA_DB_PATH` (opcional) documentadas para configurar la base de datos.
- Actualización de la dependencia `agix` para requerir al menos la versión 1.4
  (con soporte confirmado para ``PADState``) y mantener compatibilidad con la
  serie 1.x.
- Mejora de rendimiento y compatibilidad derivada de esta actualización.
- Actualización de `holobit-sdk` a la versión 1.0.9 y ajuste de `graficar`/`proyectar` al nuevo API.
- Ampliación de `corelibs.texto` y nuevas utilidades en `standard_library.texto` con soporte Unicode y pruebas asociadas.
- Validadores `es_*` alineados con `str.is*` disponibles tanto en `pcobra.corelibs.texto` como en `standard_library.texto`, con equivalentes nativos para JavaScript.
- `standard_library.datos` incorpora lectura y escritura de archivos Parquet y Feather detectando automáticamente los motores opcionales requeridos.
- `corelibs.numero` añade `es_finito`, `es_infinito`, `es_nan` y `copiar_signo`, reexportados en la biblioteca estándar y con equivalentes nativos que respetan IEEE-754.
- `corelibs.numero` suma `interpolar` (lerp saturado al estilo de Rust/Kotlin) y `envolver_modular` (residuo euclidiano compatible con `rem_euclid`/`mod`), expuestos también desde `standard_library.numero` y documentados con nuevos ejemplos.
- `corelibs.asincrono` incorpora `grupo_tareas`, un administrador compatible con
  versiones anteriores que replica la semántica de `asyncio.TaskGroup` y se
  expone también desde la biblioteca estándar.
- `corelibs.asincrono` suma `reintentar_async`, que aplica reintentos con
  *backoff* exponencial y *jitter* opcional, reexportado en la biblioteca
  estándar junto con documentación y pruebas que validan los tiempos de espera.
- `corelibs.texto` suma `prefijo_comun` y `sufijo_comun`, inspirados en Kotlin y
  Swift, con opciones para ignorar mayúsculas o normalizar Unicode; se
  reexportan en la biblioteca estándar y cuentan con versiones nativas para JavaScript.
- `corelibs.logica` añade `condicional`, un selector de ramas inspirado en ``when`` (Kotlin) y `case_when` (R) con evaluación perezosa; se reexporta en la biblioteca estándar junto con ejemplos y pruebas actualizadas.
- `standard_library.datos` incorpora los helpers `pivotar_ancho`, `pivotar_largo` y `mutar_columna` para transformar registros y calcular columnas derivadas.

## v10.0.9 - 2025-08-17
- Ajuste en `SafeUnpickler` para aceptar los módulos `core.ast_nodes` y `cobra.core.ast_nodes`.
- `corelibs.sistema.ejecutar` ahora exige una lista blanca de comandos
  mediante el parámetro `permitidos` o la variable de entorno
  `COBRA_EJECUTAR_PERMITIDOS`. Invocarlo sin esta configuración produce
  `ValueError` y la lista de la variable de entorno se fija al importar
  el módulo, evitando modificaciones en tiempo de ejecución.
- Reemplazo del uso de `pickle` por serialización JSON segura en la caché
  de AST y tokens.
- Actualización a Agix 1.4.0.

## v10.0.8 - Pendiente de liberación
- Integración de la biblioteca **holobit** para la creación y manipulación de holobits.
- Pruebas en `tests` que verifican la funcionalidad de holobit.
- `tests/unit/test_holobit_generation.py` construye holobits de diferentes tamaños y valida la conversión a JSON.
- `tests/unit/test_benchmark_execution.py` ejecuta los comandos de benchmark y comprueba que los tiempos se mantienen dentro de un rango razonable utilizando `time.perf_counter`.

## v10.0.7 - Pendiente de liberación
- Nota: versión en desarrollo, sin cambios liberados.

## v10.0.6 - 2025-07-26
- Actualización de documentación y archivos de configuración.

## v10.0.0 - 2025-07-25
- Incremento de versión principal a 10.0.0.
- Actualización de documentación y ejemplos.

## v9.1.0 - 2025-07-16
- Incremento de versión menor a 9.1.0.
- Actualización de documentación y ejemplos.
- Ajustes en el empaquetado y generación de binarios.

## v9.0.0 - 2025-07-13
- Mejoras de empaquetado que simplifican la distribución.
- Integración de notebooks de ejemplo en el paquete.
- Otros ajustes menores.
- Requisito mínimo de Python actualizado a la versión 3.9.

## v8.0.0 - 2025-07-08
- Incremento de versión principal a 8.0.0.
- Documentación y pruebas actualizadas.

## v7.2.0 - 2025-07-06
- Incremento de versión menor a 7.2.0.
- Documentación y pruebas actualizadas.

## v7.1.0 - 2025-07-06
- Se actualiza la versión del proyecto y del kernel de Jupyter.
- Documentación actualizada con nuevas referencias de versión.

## v7.0.0 - 2025-07-06
- Se incrementa la versión principal del proyecto.
- Documentación y pruebas adaptadas a la nueva versión.

## v6.0.0 - 2025-07-04
- Actualización mayor del lenguaje Cobra y de las herramientas de desarrollo.
- Documentación reorganizada con nuevos ejemplos.
- Integración de procesos de lanzamiento automatizados a través de GitHub Actions.
- Los transpiladores exponen el método `generate_code` y permiten guardar el resultado con `save_file`.

## v5.6.3 - 2025-07-02
- Ajustes de documentación y versión.

## v5.6.2 - 2025-07-02
- Actualización de versión a 5.6.2 y ajustes de documentación y pruebas.

## v5.6 - 2025-06-29
- Paquete actualizado a la versión 5.6.
- Documentación y kernel reflejan la nueva versión.
- Prueba de plugins ajustada a "dummy 5.6".

## v5.5 - 2025-06-29
- Paquete actualizado a la versión 5.5.
- Documentación y kernel reflejan la nueva versión.
- Prueba de plugins ajustada a "dummy 5.5".

## v5.4 - 2025-06-29
- Paquete actualizado a la versión 5.4.
- Documentación y kernel reflejan la nueva versión.
- Prueba de plugins ajustada a "dummy 5.4".

## v5.2 - 2025-06-29
- Paquete actualizado a la versión 5.2.
- Documentación y kernel reflejan la nueva versión.
- Prueba de plugins ajustada a "dummy 5.2".

## v5.1 - 2025-06-28
- Paquete actualizado a la versión 5.1.
- Documentación y kernel reflejan la nueva versión.
- Prueba de plugins ajustada a "dummy 5.1".

## v5.0 - 2025-06-28
- Paquete actualizado a la versión 5.0.
- Documentación y kernel reflejan la nueva versión.
- Prueba de plugins ajustada a "dummy 5.0".

## v4.6 - 2025-06-28
- Paquete actualizado a la versión 4.6.
- Documentación y kernel reflejan la nueva versión.
- Prueba de plugins ajustada a "dummy 4.6".

## v4.5 - 2025-06-28
- Paquete actualizado a la versión 4.5.
- Documentación y kernel reflejan la nueva versión.
- Prueba de plugins ajustada a "dummy 4.5".

## v4.4 - 2025-06-28
- Paquete actualizado a la versión 4.4.
- Documentación y kernel reflejan la nueva versión.
- Prueba de plugins ajustada a "dummy 4.4".

## v4.3 - 2025-06-28
- Paquete actualizado a la versión 4.3.
- Documentación y kernel reflejan la nueva versión.
- Prueba de plugins ajustada a "dummy 4.3".

## v3.0 - 2025-06-27
- Paquete actualizado a la versión 3.0.
- Documentación y kernel reflejan la nueva versión.
- Prueba de plugins ajustada a "dummy 3.0".

## v2.2 - 2025-06-27
- Paquete actualizado a la versión 2.2.
- Documentación y kernel reflejan la nueva versión.
- Prueba de plugins ajustada a "dummy 2.2".

## v2.1 - 2025-06-27
- Actualización del paquete a la versión 2.1.
- Nuevos comandos `init` y `package`.
- Incorporación del puente ctypes y del helper de importación de transpiladores.
- Documentación y kernel actualizados.

## v2.0 - 2025-06-26
- Actualización de la versión del paquete a 2.0.
- Documentación y archivos de configuración actualizados a la versión 2.0.
- El kernel de Jupyter refleja la nueva versión.

## v1.4 - 2025-06-26
- Publicación en PyPI con metadata completa.
- Soporte de instalación mediante pipx.
- Inicio de la internacionalización en la CLI y documentación.

## v1.3 - 2024-06-01
- Versión inicial migrada al changelog.
