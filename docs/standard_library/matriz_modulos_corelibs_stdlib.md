# Matriz de módulos corelibs/standard_library

## logica
- **Funciones actuales**: `es_verdadero`, `es_falso`, `conjuncion`, `disyuncion`, `negacion`, `entonces`, `si_no`, `coalescer`, `condicional`, `xor`, `nand`, `nor`, `implica`, `equivale`, `xor_multiple`, `todas`, `alguna`, `ninguna`, `solo_uno`, `conteo_verdaderos`, `paridad`, `mayoria`, `exactamente_n`, `tabla_verdad`, `diferencia_simetrica`.
- **Faltantes prioritarias**: sin faltantes críticos para la API canónica.
- **Nombres españoles objetivo**: alineados con contrato canónico (`coalescer`, `condicional`, `conteo_verdaderos`).

## asincrono
- **Funciones actuales**: `grupo_tareas`, `limitar_tiempo`, `proteger_tarea`, `ejecutar_en_hilo`, `reintentar_async`, `recolectar`, `carrera`, `primero_exitoso`, `esperar_timeout`, `crear_tarea`, `iterar_completadas`, `mapear_concurrencia`, `recolectar_resultados`, `dormir_async`.
- **Faltantes prioritarias**: se cubren los helpers expuestos por `corelibs.asincrono`.
- **Nombres españoles objetivo**: `recolectar`, `carrera`, `primero_exitoso`, `mapear_concurrencia`.

## sistema
- **Funciones actuales**: `obtener_os`, `ejecutar`, `ejecutar_async`, `ejecutar_stream`, `obtener_env`, `listar_dir`, `directorio_actual`, `ejecutar_comando_async`.
- **Faltantes prioritarias**: sin faltantes críticos; se conserva modelo de lista blanca y timeout.
- **Nombres españoles objetivo**: `ejecutar`, `obtener_env`, `directorio_actual`.

## archivo
- **Funciones actuales**: `leer`, `escribir`, `adjuntar`, `existe`, `eliminar`, `leer_lineas`, `anexar`.
- **Faltantes prioritarias**: sin faltantes críticos, manteniendo sandbox de rutas.
- **Nombres españoles objetivo**: `adjuntar` (canónico), `anexar` (compatibilidad), `leer_lineas`.

## tiempo
- **Funciones actuales**: `ahora`, `formatear`, `dormir`, `epoch`, `desde_epoch`.
- **Faltantes prioritarias**: sin faltantes críticos.
- **Nombres españoles objetivo**: `ahora`, `formatear`, `desde_epoch`.

## red
- **Funciones actuales**: `obtener_url`, `enviar_post`, `obtener_url_async`, `enviar_post_async`, `descargar_archivo`, `obtener_json`, `obtener_url_texto`.
- **Faltantes prioritarias**: sin faltantes críticos; se preserva whitelist de hosts y HTTPS obligatorio.
- **Nombres españoles objetivo**: `obtener_url`, `descargar_archivo`, `obtener_json`.
