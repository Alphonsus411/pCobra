# Inventario técnico de módulos `usar`

Fecha de actualización: 2026-05-03.

## 1) Fuente runtime de resolución de `usar "modulo"`

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

## 2) Matriz por módulo objetivo

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

## 3) Funciones con nombres no canónicos y propuesta de alias público

Se marcan como **no canónicas** las que están en inglés, demasiado técnicas del backend o abreviadas de forma opaca para API pública Cobra.

| Módulo | Nombre actual | Motivo | Alias público propuesto |
|---|---|---|---|
| `asincrono` | `reintentar_async` | sufijo inglés `_async` | `reintentar_asincrono` |
| `datos` | `leer_csv` / `escribir_csv` | sigla técnica inglesa | `leer_valores_separados_por_comas` / `escribir_valores_separados_por_comas` |
| `datos` | `leer_json` / `escribir_json` | sigla de formato | `leer_datos_json` / `escribir_datos_json` |
| `datos` | `leer_excel` / `escribir_excel` | marca/formato externo | `leer_hoja_calculo` / `escribir_hoja_calculo` |
| `datos` | `leer_parquet` / `escribir_parquet` | formato técnico | `leer_tabla_columnar`* / `escribir_tabla_columnar`* |
| `datos` | `leer_feather` / `escribir_feather` | formato técnico | `leer_tabla_ligera` / `escribir_tabla_ligera` |
| `datos` | `pivotar_ancho` / `pivotar_largo` | calco técnico | `pivotar_a_formato_ancho` / `pivotar_a_formato_largo` |
| `decoradores` | `reintentar_async` | sufijo inglés `_async` | `reintentar_asincrono` |
| `interfaz` | `mostrar_markdown` | término inglés | `mostrar_marcado` |
| `interfaz` | `mostrar_json` | sigla técnica | `mostrar_datos_json` |
| `interfaz` | `iniciar_gui` / `iniciar_gui_idle` | sigla inglesa GUI | `iniciar_interfaz_grafica` / `iniciar_interfaz_grafica_idle` |
| `lista` | `chunk` | inglés | `trocear` |
| `lista` | `scanear` | traducción no estándar de “scan” funcional | `acumular_parcial` |
| `logica` | `coalesce` | inglés de SQL/backend | `primer_no_nulo` |
| `logica` | `xor` / `nand` / `nor` | siglas lógicas crudas | `o_exclusivo` / `no_y` / `no_o` |
| `texto` | `a_snake` / `a_camel` | convenciones en inglés | `a_snake_case` / `a_camel_case` |
| `texto` | `minusculas_casefold` | tecnicismo Python | `minusculas_compatibles_unicode` |
| `numero` | `es_nan` | sigla inglesa | `es_no_numero` |
| `util` | `rel` | abreviatura opaca | `ruta_relativa` |

\* Nota: se sugiere corregir la ortografía a `columnar` en caso de adoptar alias relacionados.

## 4) Observaciones para siguientes tareas

- El mapa de módulos de REPL estricto (`REPL_COBRA_MODULE_MAP`) no incluye actualmente: `tiempo`, `coleccion`, `red`, `sistema`, `seguridad` (presentes en `corelibs`).
- Para una migración segura de nombres, conviene introducir alias compatibles en cada módulo y deprecar gradualmente nombres antiguos.
- Este inventario debe tratarse como línea base para evaluar cobertura de API pública de `usar`.
