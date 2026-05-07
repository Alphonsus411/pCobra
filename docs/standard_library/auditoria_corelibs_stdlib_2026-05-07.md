# Auditoría de superficie pública: `corelibs/` y `standard_library/`

Fecha: 2026-05-07

## Validación de alcance

Se confirma explícitamente que **no se tocarán Lexer ni Parser** en esta fase. Este entregable solo audita superficie pública y prioriza funciones por módulo.

## Matriz por módulo

> Columnas: función actual (implementación real), nombre expuesto (`__all__`), idioma, estado.

### `corelibs`

| módulo | función actual | nombre expuesto | idioma | estado |
|---|---|---|---|---|
| archivo | `leer` | `leer` | ES | ok |
| archivo | `escribir` | `escribir` | ES | ok |
| archivo | `existe` | `existe` | ES | ok |
| archivo | `eliminar` | `eliminar` | ES | ok |
| archivo | `anexar` | `anexar` | ES | ok |
| archivo | `leer_lineas` | `leer_lineas` | ES | ok |
| asincrono | `crear_tarea` | `crear_tarea` | ES | ok |
| asincrono | *(varias con alias dinámico)* | `limitar_tiempo`, `ejecutar_en_hilo`, `recolectar`, `carrera`, `primero_exitoso`, `esperar_timeout`, `reintentar_async`, `grupo_tareas`, `iterar_completadas`, `mapear_concurrencia`, `recolectar_resultados`, `dormir_async` | ES | ok |
| coleccion | — | — | — | falta |
| datos | — | — | — | falta |
| holobit | `crear_holobit` | `crear_holobit` | ES+interno | ok |
| logica | `es_verdadero` ... | `es_verdadero` ... | ES | ok |
| numero | `absoluto` ... | `absoluto` ... | ES | ok |
| red | `obtener_url` | `obtener_url` | ES | ok |
| seguridad | — | — | — | falta |
| sistema | `obtener_os` | `obtener_os` | ES | ok |
| texto | `mayusculas` ... | `mayusculas` ... | ES | ok |
| tiempo | `ahora` | `ahora` | ES | ok |

### `standard_library`

| módulo | función actual | nombre expuesto | idioma | estado |
|---|---|---|---|---|
| archivo | `leer` | `leer` | ES | ok |
| archivo | `escribir` | `escribir` | ES | ok |
| archivo | `adjuntar` | `adjuntar` | ES | ok |
| archivo | *(no se detecta función canónica)* | `existeeliminar` | mezclado/error | no canónico |
| asincrono | `grupo_tareas` ... | `grupo_tareas` ... | ES | ok |
| datos | `leer_csv` ... | `leer_csv` ... | ES | ok |
| datos | `mapear` | `mapear` | ES raíz backend (map) | no canónico |
| decoradores | `memoizar` ... | `memoizar` ... | ES | ok |
| fecha | `hoy` | `hoy` | ES | ok |
| holobit | *(reexport)* | `crear_holobit` ... | ES+interno | ok |
| interfaz | `mostrar_codigo` ... | `mostrar_codigo` ... | ES | ok |
| lista | `mapear_seguro` | `mapear_seguro` | ES raíz backend (map) | no canónico |
| logica | `coalesce` | `coalesce` | EN | no canónico |
| numero | `clamp` | `clamp` | EN | no canónico |
| red | `obtener_url` ... | `obtener_url` ... | ES | ok |
| sistema | `ejecutar_comando_async` | `ejecutar_comando_async` | ES | ok |
| texto | `minusculas` ... | `minusculas` ... | ES | ok |
| tiempo | `ahora` | `ahora` | ES | ok |
| util | `rel` | `rel` | interno/abreviado | no canónico |

## Símbolos backend o prohibidos detectados

### Prohibidos explícitos a vigilar
Lista de prohibidos solicitada: `append`, `map`, `filter`, `unwrap`, `expect`, `self`, dunders.

### Hallazgos
- **Raíz semántica `map`** en API pública:
  - `standard_library.datos.mapear`
  - `standard_library.lista.mapear_seguro`
  - `standard_library.lista.mapear_aplanado`
  - `corelibs.asincrono.mapear_concurrencia`
- **Nombre inglés expuesto**:
  - `standard_library.logica.coalesce`
  - `standard_library.numero.clamp`
- **Dunder en superficie puente**:
  - `__getattr__`, `__dir__`, `__all__`, `__path__` en módulos puente de compatibilidad (esperable a nivel módulo, no API funcional de usuario).
- **No detectados en `__all__`**: `append`, `filter`, `unwrap`, `expect`, `self`.

## Lista priorizada de funciones a completar/normalizar por módulo

Prioridad basada en impacto de UX/API y coherencia canónica, **sin cambiar semántica runtime existente**.

1. `standard_library.archivo`
   - Corregir/exportar canónicamente `existe` y `eliminar` (evitar `existeeliminar`).
2. `standard_library.logica`
   - Deprecar alias inglés `coalesce` y promover `coalescer` como canónico.
3. `standard_library.numero`
   - Deprecar alias inglés `clamp` y promover `limitar`.
4. `standard_library.util`
   - Renombrar/documentar `rel` a nombre semántico en español (mantener alias por compatibilidad).
5. `corelibs.coleccion`, `corelibs.datos`, `corelibs.seguridad`
   - Definir `__all__` y primera superficie mínima canónica en español.
6. Familia `mapear*` (múltiples módulos)
   - Revisar naming para que no replique términos backend en usuario final (manteniendo compatibilidad mediante alias).
7. `holobit` (corelibs/stdlib)
   - Confirmar contrato público y documentación (dominio interno válido, pero requiere criterios de estabilidad).

## Notas de método

- Auditoría centrada en símbolos exportados mediante `__all__` por módulo.
- Se clasificó “no canónico” cuando el nombre expuesto está en inglés, es ambiguo/interno o fusiona operaciones.
