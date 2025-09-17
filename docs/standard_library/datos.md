# standard_library.datos

El módulo `standard_library.datos` encapsula operaciones comunes sobre datos tabulares usando `pandas` y `numpy`. Todas las funciones devuelven estructuras simples (`list` de `dict` o `dict` de listas) para que puedan consumirse fácilmente desde Cobra o por librerías externas.

## Funciones disponibles (backend Python)

- **`leer_csv(ruta, *, separador=",", encoding="utf-8", limite_filas=None)`**: lee un archivo CSV y devuelve una lista de registros. Los valores ausentes se normalizan como `None`.
- **`leer_json(ruta, *, orient=None, lineas=False)`**: carga un archivo JSON (incluido JSON Lines) y lo expone como lista de diccionarios.
- **`describir(datos)`**: calcula estadísticas básicas por columna y devuelve un diccionario de métricas.
- **`seleccionar_columnas(datos, columnas)`**: extrae columnas específicas y reporta si alguna falta.
- **`filtrar(datos, condicion)`**: aplica una función por fila y conserva solo los registros que devuelvan `True`.
- **`agrupar_y_resumir(datos, por, agregaciones)`**: agrupa por columnas y aplica agregaciones compatibles con `DataFrame.agg`.
- **`a_listas(datos)`**: transforma la tabla a un diccionario columna → lista.
- **`de_listas(columnas)`**: genera una lista de diccionarios a partir de un mapeo de columnas.

## Backend JavaScript

En el objetivo JavaScript se ofrece una implementación parcial que mantiene las transformaciones puramente estructurales (`seleccionar_columnas`, `filtrar`, `a_listas`, `de_listas`). Las funciones que dependen de `pandas` (`leer_csv`, `leer_json`, `describir`, `agrupar_y_resumir`) lanzan un error explicando la limitación para evitar resultados inconsistentes.

> **Sugerencia:** si necesitas procesar archivos directamente en JavaScript, realiza la lectura con utilidades propias del entorno (por ejemplo `fetch` o `fs`) y entrega los datos a Cobra usando `de_listas` o listas de diccionarios.
