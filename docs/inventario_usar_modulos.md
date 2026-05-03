# Inventario técnico de módulos `usar`

Fecha de actualización: 2026-05-03.

## 1) Lista canónica permitida para `usar` (contrato público)

La lista **canónica y permitida** para `usar` en REPL estricto se define en `REPL_COBRA_MODULE_MAP`.
Cualquier módulo fuera de esta lista se rechaza como import externo no soportado.

Módulos permitidos:

- `archivo`
- `asincrono`
- `datos`
- `decoradores`
- `fecha`
- `interfaz`
- `lista`
- `logica`
- `numero`
- `texto`
- `util`

## 2) Fuente runtime de resolución de `usar "modulo"`

La resolución en runtime de `usar` ocurre en dos capas:

1. **Ruta principal de ejecución**: `InterpretadorCobra.ejecutar_usar` en `src/pcobra/core/interpreter.py`.
   - Distingue entre REPL estricto y modo normal.
   - En REPL estricto, sólo acepta alias oficiales definidos en `REPL_COBRA_MODULE_MAP`.
   - Si el alias existe, carga con `obtener_modulo_cobra_oficial`; si no, rechaza módulo externo.

2. **Loader de módulos**: `src/pcobra/cobra/usar_loader.py`.
   - `obtener_modulo_cobra_oficial(nombre)`: intenta resolver desde `corelibs/` y luego `standard_library/`.
   - `obtener_modulo(nombre, permitir_instalacion=True)`: aplica whitelist, resolver de imports y fallback de import/instalación.

3. **Mapa de alias públicos Cobra (REPL estricto)**:
   - `src/pcobra/cobra/usar_policy.py` define `REPL_COBRA_MODULE_MAP`.

## 3) Tabla de nombres canónicos (español) y equivalencias internas no expuestas

> Política: la **API pública** de `usar` se expresa con nombres canónicos en español.
> Las rutas internas de implementación (Python/JS/Rust/Holobit SDK) son detalles de sustrato y **no son API pública**.

| Nombre canónico público (`usar`) | Equivalencia interna actual (no expuesta) | Observación |
|---|---|---|
| `archivo` | `standard_library/archivo.py` | Exporta `__all__` público.
| `asincrono` | `standard_library/asincrono.py` | Exporta `__all__` público.
| `datos` | `standard_library/datos.py` | Exporta `__all__` público.
| `decoradores` | `standard_library/decoradores.py` | Exporta `__all__` público.
| `fecha` | `standard_library/fecha.py` | Exporta `__all__` público.
| `interfaz` | `standard_library/interfaz.py` | Exporta `__all__` público.
| `lista` | `standard_library/lista.py` | Exporta `__all__` público.
| `logica` | `standard_library/logica.py` | Exporta `__all__` público.
| `numero` | `standard_library/numero.py` | Exporta `__all__` público.
| `texto` | `standard_library/texto.py` | Exporta `__all__` público.
| `util` | `standard_library/util.py` | Exporta `__all__` público.

### No API pública (solo sustrato interno)

- Backends internos: Python, JavaScript y Rust.
- Runtime/SDK interno de Holobit (incluyendo `holobit_sdk` interno por backend).
- Módulos de compatibilidad legacy y rutas de transpilers internos.

Nada de lo anterior debe consumirse como contrato estable desde programas de usuario Cobra; el único contrato de `usar` en REPL estricto es la lista canónica anterior.

## 4) Seguridad de exportaciones y rechazo de imports directos a backend

Para seguridad y estabilidad contractual:

1. **Exportaciones controladas**:
   - El módulo cargado por `usar` debe exponer `__all__` y símbolos públicos invocables.
   - Si un módulo externo no define `__all__` adecuado, se rechaza con error explícito.

2. **Rechazo de imports directos backend en REPL estricto**:
   - `usar "numpy"`, `usar "requests"` y análogos externos son rechazados.
   - No se permite acceder por namespace tipo `numero.es_finito(...)`; `usar` inyecta símbolos planos.

3. **Carga atómica**:
   - Ante error de importación/exportación, el contexto de variables no debe contaminarse con símbolos parciales.

## 5) Verificación de consistencia (docs, tests, runtime real)

Estado verificado en esta actualización:

- **Docs**: este inventario alinea el contrato público con la lista canónica de `REPL_COBRA_MODULE_MAP`.
- **Runtime**: la política efectiva de aliases en REPL estricto depende de `src/pcobra/cobra/usar_policy.py` y la ejecución en `InterpretadorCobra.ejecutar_usar`.
- **Tests de contrato**: `tests/integration/test_repl_usar_entrypoints_contract.py` cubre:
  - aceptación de módulos canónicos (`numero`, `texto`),
  - rechazo de externos (`numpy`, `requests`),
  - exigencia de `__all__` para exportabilidad,
  - inmutabilidad/atomicidad del contexto si falla `usar`.

## 6) Matriz por módulo objetivo

Módulos objetivo tomados del mapa oficial `REPL_COBRA_MODULE_MAP`:
`archivo`, `asincrono`, `datos`, `decoradores`, `fecha`, `interfaz`, `lista`, `logica`, `numero`, `texto`, `util`.

> Criterio de estado:
> - **implementado**: módulo resoluble y con exportaciones públicas (`__all__`).
> - **parcial**: resoluble pero con señales de API no canónica relevante.
> - **ausente**: no resoluble por las rutas oficiales.

| Módulo Cobra público | Backend interno (archivo Python) | Exportaciones públicas actuales | Estado |
|---|---|---|---|
| `archivo` | `standard_library/archivo.py` | `leer`, `escribir`, `adjuntar`, `existe` | implementado |
| `asincrono` | `standard_library/asincrono.py` | `grupo_tareas`, `limitar_tiempo`, `proteger_tarea`, `ejecutar_en_hilo`, `reintentar_async` | parcial |
| `datos` | `standard_library/datos.py` | `leer_csv`, `leer_json`, `escribir_csv`, `escribir_json`, `leer_excel`, `escribir_excel`, `leer_parquet`, `escribir_parquet`, `leer_feather`, `escribir_feather`, `describir`, `correlacion_pearson`, `correlacion_spearman`, `matriz_covarianza`, `calcular_percentiles`, `resumen_rapido`, `seleccionar_columnas`, `filtrar`, `mutar_columna`, `separar_columna`, `unir_columnas`, `agrupar_y_resumir`, `tabla_cruzada`, `pivotar_ancho`, `pivotar_largo`, `ordenar_tabla`, `combinar_tablas`, `rellenar_nulos`, `desplegar_tabla`, `pivotar_tabla`, `a_listas`, `de_listas` | parcial |
| `decoradores` | `standard_library/decoradores.py` | `memoizar`, `dataclase`, `temporizar`, `depreciado`, `sincronizar`, `reintentar`, `reintentar_async`, `orden_total`, `despachar_por_tipo` | parcial |
| `fecha` | `standard_library/fecha.py` | `hoy`, `formatear`, `sumar_dias` | implementado |
| `interfaz` | `standard_library/interfaz.py` | `mostrar_codigo`, `mostrar_markdown`, `mostrar_json`, `mostrar_arbol`, `preguntar_confirmacion`, `preguntar_password`, `mostrar_tabla`, `mostrar_tabla_paginada`, `mostrar_columnas`, `mostrar_panel`, `grupo_consola`, `estado_temporal`, `barra_progreso`, `limpiar_consola`, `imprimir_aviso`, `iniciar_gui`, `iniciar_gui_idle`, `preguntar_opciones_multiple` | parcial |
| `lista` | `standard_library/lista.py` | `cabeza`, `cola`, `longitud`, `combinar`, `mapear_seguro`, `mapear_aplanado`, `ventanas`, `chunk`, `tomar_mientras`, `descartar_mientras`, `scanear`, `pares_consecutivos` | parcial |
| `logica` | `standard_library/logica.py` | `es_verdadero`, `es_falso`, `conjuncion`, `disyuncion`, `negacion`, `entonces`, `si_no`, `coalesce`, `condicional`, `xor`, `nand`, `nor`, `implica`, `equivale`, `xor_multiple`, `todas`, `alguna`, `ninguna`, `solo_uno`, `conteo_verdaderos`, `paridad`, `mayoria`, `exactamente_n`, `tabla_verdad`, `diferencia_simetrica` | parcial |
| `numero` | `standard_library/numero.py` | `es_finito`, `es_infinito`, `es_nan`, `copiar_signo`, `signo`, `limitar`, `hipotenusa`, `distancia_euclidiana`, `raiz_entera`, `combinaciones`, `permutaciones`, `suma_precisa`, `interpolar`, `envolver_modular`, `varianza`, `varianza_muestral`, `media_geometrica`, `media_armonica`, `percentil`, `cuartiles`, `rango_intercuartil`, `coeficiente_variacion` | parcial |
| `texto` | `standard_library/texto.py` | `quitar_acentos`, `normalizar_espacios`, `es_palindromo`, `es_anagrama`, `codificar`, `decodificar`, `es_alfabetico`, `es_alfa_numerico`, `es_decimal`, `es_numerico`, `es_identificador`, `es_imprimible`, `es_ascii`, `es_mayusculas`, `es_minusculas`, `es_titulo`, `es_digito`, `es_espacio`, `quitar_prefijo`, `quitar_sufijo`, `a_snake`, `a_camel`, `quitar_envoltura`, `prefijo_comun`, `sufijo_comun`, `dividir_lineas`, `dividir_derecha`, `encontrar`, `encontrar_derecha`, `subcadena_antes`, `subcadena_despues`, `subcadena_antes_ultima`, `subcadena_despues_ultima`, `indice`, `indice_derecha`, `contar_subcadena`, `centrar_texto`, `rellenar_ceros`, `minusculas_casefold`, `intercambiar_mayusculas`, `expandir_tabulaciones`, `particionar`, `particionar_derecha`, `indentar_texto`, `desindentar_texto`, `envolver_texto`, `acortar_texto`, `formatear`, `formatear_mapa`, `tabla_traduccion`, `traducir` | parcial |
| `util` | `standard_library/util.py` | `es_nulo`, `es_vacio`, `repetir`, `rel` | parcial |
