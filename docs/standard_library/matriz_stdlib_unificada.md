# Matriz unificada de stdlib (inventario + propuestas)

Este documento usa `__all__` como fuente pública para cada módulo.

## Inventario actual por módulo
- `src/pcobra/corelibs/numero.py`: absoluto, redondear, piso, techo, mcd, mcm, es_cercano, hipotenusa, distancia_euclidiana, es_finito, es_infinito, es_nan, copiar_signo, signo, producto, entero_a_base, entero_desde_base, longitud_bits, contar_bits, rotar_bits_izquierda, rotar_bits_derecha, entero_a_bytes, entero_desde_bytes, raiz, raiz_entera, potencia, limitar, interpolar, envolver_modular, aleatorio, aleatorio_entero, mediana, moda, desviacion_estandar, es_par, es_primo, factorial, promedio, combinaciones, permutaciones, suma_precisa, varianza, varianza_muestral, media_geometrica, media_armonica, percentil, cuartiles, rango_intercuartil, coeficiente_variacion
- `src/pcobra/standard_library/numero.py`: es_finito, es_infinito, es_nan, copiar_signo, signo, limitar, hipotenusa, distancia_euclidiana, raiz_entera, combinaciones, permutaciones, suma_precisa, interpolar, envolver_modular, varianza, varianza_muestral, media_geometrica, media_armonica, percentil, cuartiles, rango_intercuartil, coeficiente_variacion, absoluto, redondear, piso, techo, mcd, mcm, es_cercano, raiz, potencia, mediana, moda, es_par, es_primo, factorial, promedio, sumatoria, producto
- `src/pcobra/corelibs/texto.py`: mayusculas, minusculas, capitalizar, titulo, intercambiar_mayusculas, invertir, concatenar, codificar, decodificar, quitar_espacios, dividir, dividir_derecha, encontrar, encontrar_derecha, indice, indice_derecha, subcadena_antes, subcadena_despues, subcadena_antes_ultima, subcadena_despues_ultima, unir, formatear, formatear_mapa, tabla_traduccion, traducir, reemplazar, empieza_con, termina_con, incluye, quitar_prefijo, quitar_sufijo, a_snake, a_camel, quitar_envoltura, prefijo_comun, sufijo_comun, rellenar_izquierda, particionar, particionar_derecha, rellenar_derecha, normalizar_unicode, dividir_lineas, expandir_tabulaciones, contar_subcadena, indentar_texto, desindentar_texto, envolver_texto, acortar_texto, centrar_texto, rellenar_ceros, minusculas_casefold, es_alfabetico, es_alfa_numerico, es_decimal, es_numerico, es_identificador, es_imprimible, es_ascii, es_mayusculas, es_minusculas, es_espacio, es_titulo, es_digito, lineas_no_vacias
- `src/pcobra/standard_library/texto.py`: quitar_acentos, normalizar_espacios, es_palindromo, es_anagrama, codificar, decodificar, es_alfabetico, es_alfa_numerico, es_decimal, es_numerico, es_identificador, es_imprimible, es_ascii, es_mayusculas, es_minusculas, es_titulo, es_digito, es_espacio, quitar_prefijo, quitar_sufijo, a_snake, a_camel, quitar_envoltura, prefijo_comun, sufijo_comun, dividir_lineas, dividir_derecha, encontrar, encontrar_derecha, subcadena_antes, subcadena_despues, subcadena_antes_ultima, subcadena_despues_ultima, indice, indice_derecha, contar_subcadena, centrar_texto, rellenar_ceros, minusculas, mayusculas, minusculas_casefold, intercambiar_mayusculas, expandir_tabulaciones, particionar, particionar_derecha, indentar_texto, desindentar_texto, envolver_texto, acortar_texto, formatear, formatear_mapa, tabla_traduccion, traducir, recortar, repetir
- `src/pcobra/corelibs/datos.py`: leer_csv, leer_json, escribir_csv, escribir_json, leer_excel, escribir_excel, leer_parquet, escribir_parquet, leer_feather, escribir_feather, describir, correlacion_pearson, correlacion_spearman, matriz_covarianza, calcular_percentiles, resumen_rapido, seleccionar_columnas, filtrar, mutar_columna, separar_columna, unir_columnas, agrupar_y_resumir, tabla_cruzada, pivotar_ancho, pivotar_largo, ordenar_tabla, combinar_tablas, rellenar_nulos, desplegar_tabla, pivotar_tabla, agregar, mapear, reducir, claves, valores, longitud
- `src/pcobra/standard_library/datos.py`: leer_csv, leer_json, escribir_csv, escribir_json, leer_excel, escribir_excel, leer_parquet, escribir_parquet, leer_feather, escribir_feather, describir, correlacion_pearson, correlacion_spearman, matriz_covarianza, calcular_percentiles, resumen_rapido, seleccionar_columnas, filtrar, mutar_columna, separar_columna, unir_columnas, agrupar_y_resumir, tabla_cruzada, pivotar_ancho, pivotar_largo, ordenar_tabla, combinar_tablas, rellenar_nulos, desplegar_tabla, pivotar_tabla, agregar, mapear, reducir, claves, valores, longitud, invertir_tabla, tomar
- `src/pcobra/corelibs/logica.py`: es_verdadero, es_falso, conjuncion, disyuncion, negacion, xor, nand, nor, implica, equivale, xor_multiple, entonces, si_no, condicional, coalescer, todas, alguna, ninguna, solo_uno, conteo_verdaderos, paridad, mayoria, exactamente_n, tabla_verdad, diferencia_simetrica, si_condicional
- `src/pcobra/standard_library/logica.py`: es_verdadero, es_falso, conjuncion, disyuncion, negacion, entonces, si_no, coalescer, condicional, xor, nand, nor, implica, equivale, xor_multiple, todas, alguna, ninguna, solo_uno, conteo_verdaderos, paridad, mayoria, exactamente_n, tabla_verdad, diferencia_simetrica
- `src/pcobra/corelibs/asincrono.py`: proteger_tarea, limitar_tiempo, ejecutar_en_hilo, recolectar, carrera, primero_exitoso, esperar_timeout, reintentar_async, grupo_tareas, crear_tarea, iterar_completadas, mapear_concurrencia, recolectar_resultados, dormir_async
- `src/pcobra/standard_library/asincrono.py`: grupo_tareas, limitar_tiempo, proteger_tarea, ejecutar_en_hilo, reintentar_async, recolectar
- `src/pcobra/corelibs/sistema.py`: obtener_os, ejecutar, ejecutar_async, ejecutar_stream, obtener_env, listar_dir, ejecutar_comando_async, directorio_actual
- `src/pcobra/standard_library/sistema.py`: obtener_os, ejecutar, ejecutar_async, ejecutar_stream, obtener_env, listar_dir, directorio_actual
- `src/pcobra/corelibs/archivo.py`: leer, escribir, existe, eliminar, anexar, leer_lineas
- `src/pcobra/standard_library/archivo.py`: leer, escribir, adjuntar, existe
- `src/pcobra/corelibs/tiempo.py`: ahora, formatear, dormir, epoch, desde_epoch
- `src/pcobra/standard_library/tiempo.py`: ahora, formatear, dormir, epoch, desde_epoch
- `src/pcobra/corelibs/red.py`: obtener_url, enviar_post, obtener_url_async, enviar_post_async, descargar_archivo, obtener_url_texto, obtener_json
- `src/pcobra/standard_library/red.py`: obtener_url, enviar_post, obtener_url_async, enviar_post_async, descargar_archivo, obtener_json, obtener_url_texto
- `src/pcobra/corelibs/holobit.py`: (dinámico)
- `src/pcobra/standard_library/holobit.py`: crear_holobit, validar_holobit, serializar_holobit, deserializar_holobit, proyectar, transformar, graficar, combinar, medir

## Matriz propuesta de funciones nuevas (nombres Cobra en español)
| Módulo | Funciones nuevas propuestas |
|---|---|
| `numero` | sumatoria, producto, truncar, dividir_entera, resto |
| `texto` | recortar, repetir, centrar, separar_lineas, unir_con |
| `datos` | tomar, omitir, invertir_tabla, valores_unicos, contar_por |
| `logica` | si_todos, si_alguno, negar_todos, igual_todos, evaluar_reglas |
| `asincrono` | carrera, esperar_primera, tiempo_limite, canal_simple, mapa_async |
| `sistema` | obtener_usuario, existe_comando, variables_entorno, ruta_home, crear_proceso |
| `archivo` | copiar, mover, renombrar, crear_carpeta, listar_archivos |
| `tiempo` | sumar_segundos, diferencia_segundos, inicio_dia, fin_dia, zona_horaria |
| `red` | enviar_put, enviar_delete, descargar_json, validar_url, construir_query |
| `holobit` | normalizar, escalar, distancia, promedio_holobit, fusionar |
