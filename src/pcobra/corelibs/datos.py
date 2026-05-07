"""Módulo canónico ``datos`` para `usar`.

Este puente mantiene el nombre público en español (`usar "datos"`) y reexpone
la implementación oficial ubicada en ``pcobra.standard_library.datos`` mediante
una whitelist explícita de símbolos Cobra.
"""

from pcobra.standard_library import datos as _datos

leer_csv = _datos.leer_csv
leer_json = _datos.leer_json
escribir_csv = _datos.escribir_csv
escribir_json = _datos.escribir_json
leer_excel = _datos.leer_excel
escribir_excel = _datos.escribir_excel
leer_parquet = _datos.leer_parquet
escribir_parquet = _datos.escribir_parquet
leer_feather = _datos.leer_feather
escribir_feather = _datos.escribir_feather
describir = _datos.describir
correlacion_pearson = _datos.correlacion_pearson
correlacion_spearman = _datos.correlacion_spearman
matriz_covarianza = _datos.matriz_covarianza
calcular_percentiles = _datos.calcular_percentiles
resumen_rapido = _datos.resumen_rapido
seleccionar_columnas = _datos.seleccionar_columnas
filtrar = _datos.filtrar
mutar_columna = _datos.mutar_columna
separar_columna = _datos.separar_columna
unir_columnas = _datos.unir_columnas
agrupar_y_resumir = _datos.agrupar_y_resumir
tabla_cruzada = _datos.tabla_cruzada
pivotar_ancho = _datos.pivotar_ancho
pivotar_largo = _datos.pivotar_largo
ordenar_tabla = _datos.ordenar_tabla
combinar_tablas = _datos.combinar_tablas
rellenar_nulos = _datos.rellenar_nulos
desplegar_tabla = _datos.desplegar_tabla
pivotar_tabla = _datos.pivotar_tabla
agregar = _datos.agregar
mapear = _datos.mapear
reducir = _datos.reducir
claves = _datos.claves
valores = _datos.valores
longitud = _datos.longitud

__all__ = [
    "leer_csv",
    "leer_json",
    "escribir_csv",
    "escribir_json",
    "leer_excel",
    "escribir_excel",
    "leer_parquet",
    "escribir_parquet",
    "leer_feather",
    "escribir_feather",
    "describir",
    "correlacion_pearson",
    "correlacion_spearman",
    "matriz_covarianza",
    "calcular_percentiles",
    "resumen_rapido",
    "seleccionar_columnas",
    "filtrar",
    "mutar_columna",
    "separar_columna",
    "unir_columnas",
    "agrupar_y_resumir",
    "tabla_cruzada",
    "pivotar_ancho",
    "pivotar_largo",
    "ordenar_tabla",
    "combinar_tablas",
    "rellenar_nulos",
    "desplegar_tabla",
    "pivotar_tabla",
    "agregar",
    "mapear",
    "reducir",
    "claves",
    "valores",
    "longitud",
]
