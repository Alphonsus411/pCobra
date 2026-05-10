# Informe de verificación de política `usar`
Fecha: 2026-05-10
## 1) Elementos localizados en `usar_policy.py`
- `USAR_COBRA_PUBLIC_MODULES`: lista canónica de módulos Cobra-facing permitidos por `usar`.
- `REPL_COBRA_MODULE_INTERNAL_PATH_MAP`: mapa alias canónico -> ruta interna oficial.
- Helpers de resolución/validación de rutas:
  - `validar_contrato_modulos_canonicos_usar()` valida prefijo permitido y existencia física de rutas internas.
  - `obtener_modulo_cobra_oficial()` (en `usar_loader.py`) resuelve módulo buscando primero `corelibs/` y luego `standard_library/`.
## 2) Política canónica de exportaciones
- `numero` (39 símbolos): es_finito, es_infinito, es_nan, copiar_signo, signo, limitar, hipotenusa, distancia_euclidiana, raiz_entera, combinaciones, permutaciones, suma_precisa, interpolar, envolver_modular, varianza, varianza_muestral, media_geometrica, media_armonica, percentil, cuartiles, rango_intercuartil, coeficiente_variacion, absoluto, redondear, piso, techo, mcd, mcm, es_cercano, raiz, potencia, mediana, moda, es_par, es_primo, factorial, promedio, sumatoria, producto
- `texto` (55 símbolos): quitar_acentos, normalizar_espacios, es_palindromo, es_anagrama, codificar, decodificar, es_alfabetico, es_alfa_numerico, es_decimal, es_numerico, es_identificador, es_imprimible, es_ascii, es_mayusculas, es_minusculas, es_titulo, es_digito, es_espacio, quitar_prefijo, quitar_sufijo, a_snake, a_camel, quitar_envoltura, prefijo_comun, sufijo_comun, dividir_lineas, dividir_derecha, encontrar, encontrar_derecha, subcadena_antes, subcadena_despues, subcadena_antes_ultima, subcadena_despues_ultima, indice, indice_derecha, contar_subcadena, centrar_texto, rellenar_ceros, minusculas, mayusculas, minusculas_casefold, intercambiar_mayusculas, expandir_tabulaciones, particionar, particionar_derecha, indentar_texto, desindentar_texto, envolver_texto, acortar_texto, formatear, formatear_mapa, tabla_traduccion, traducir, recortar, repetir
- `datos` (38 símbolos): leer_csv, leer_json, escribir_csv, escribir_json, leer_excel, escribir_excel, leer_parquet, escribir_parquet, leer_feather, escribir_feather, describir, correlacion_pearson, correlacion_spearman, matriz_covarianza, calcular_percentiles, resumen_rapido, seleccionar_columnas, filtrar, mutar_columna, separar_columna, unir_columnas, agrupar_y_resumir, tabla_cruzada, pivotar_ancho, pivotar_largo, ordenar_tabla, combinar_tablas, rellenar_nulos, desplegar_tabla, pivotar_tabla, agregar, mapear, reducir, claves, valores, longitud, invertir_tabla, tomar
- `logica` (25 símbolos): es_verdadero, es_falso, conjuncion, disyuncion, negacion, entonces, si_no, coalescer, condicional, xor, nand, nor, implica, equivale, xor_multiple, todas, alguna, ninguna, solo_uno, conteo_verdaderos, paridad, mayoria, exactamente_n, tabla_verdad, diferencia_simetrica
- `asincrono` (6 símbolos): grupo_tareas, limitar_tiempo, proteger_tarea, ejecutar_en_hilo, reintentar_async, recolectar
- `sistema` (7 símbolos): obtener_os, ejecutar, ejecutar_async, ejecutar_stream, obtener_env, listar_dir, directorio_actual
- `archivo` (4 símbolos): leer, escribir, adjuntar, existe
- `tiempo` (5 símbolos): ahora, formatear, dormir, epoch, desde_epoch
- `red` (7 símbolos): obtener_url, enviar_post, obtener_url_async, enviar_post_async, descargar_archivo, obtener_json, obtener_url_texto
- `holobit` (9 símbolos): crear_holobit, validar_holobit, serializar_holobit, deserializar_holobit, proyectar, transformar, graficar, combinar, medir

## 3) Verificación física de símbolos por módulo
| Módulo | corelibs | standard_library | Ruta interna recomendada | Motivo |
|---|---:|---:|---|---|
| `numero` | 38/39 | 39/39 | `src/pcobra/standard_library/numero.py` | Cubre 100% de `USAR_RUNTIME_EXPORT_OVERRIDES`. |
| `texto` | 49/55 | 55/55 | `src/pcobra/standard_library/texto.py` | Cubre 100% de `USAR_RUNTIME_EXPORT_OVERRIDES`. |
| `datos` | 36/38 | 38/38 | `src/pcobra/standard_library/datos.py` | Cubre 100% de `USAR_RUNTIME_EXPORT_OVERRIDES`. |
| `logica` | 25/25 | 25/25 | `src/pcobra/standard_library/logica.py` | Cubre 100% de `USAR_RUNTIME_EXPORT_OVERRIDES`. |
| `asincrono` | 1/6 | 3/6 | `INCONSISTENTE` | Ninguna ruta cubre al 100%. |
| `sistema` | 5/7 | 5/7 | `INCONSISTENTE` | Ninguna ruta cubre al 100%. |
| `archivo` | 3/4 | 4/4 | `src/pcobra/standard_library/archivo.py` | Cubre 100% de `USAR_RUNTIME_EXPORT_OVERRIDES`. |
| `tiempo` | 5/5 | 5/5 | `src/pcobra/standard_library/tiempo.py` | Cubre 100% de `USAR_RUNTIME_EXPORT_OVERRIDES`. |
| `red` | 3/7 | 7/7 | `src/pcobra/standard_library/red.py` | Cubre 100% de `USAR_RUNTIME_EXPORT_OVERRIDES`. |
| `holobit` | 9/9 | 0/9 | `src/pcobra/corelibs/holobit.py` | Cubre 100% de `USAR_RUNTIME_EXPORT_OVERRIDES`. |

## 4) Tabla de decisión para cambio mínimo de política
- Decisión propuesta: apuntar cada módulo a la ruta que cubre el 100% de exportaciones canónicas; excepción natural `holobit` que existe en `corelibs` y no en `standard_library`.

## 5) Validación de contrato de prefijos permitidos
- Todas las rutas recomendadas usan prefijos permitidos por `validar_contrato_modulos_canonicos_usar()`: `src/pcobra/corelibs/` o `src/pcobra/standard_library/`.
