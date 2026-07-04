# `standard_library.serializacion`

## Propósito

`serializacion` permite convertir datos entre estructuras Cobra y formatos interoperables como JSON y CSV, además de leerlos o escribirlos en archivos.

## Funciones públicas

- `codificar_json(valor)`: serializa un valor compatible a texto JSON.
- `decodificar_json(texto)`: interpreta texto JSON y devuelve la estructura correspondiente.
- `leer_json(ruta)`: lee un archivo JSON.
- `escribir_json(ruta, valor)`: escribe un valor como JSON.
- `leer_csv(ruta)`: lee filas desde un archivo CSV.
- `escribir_csv(ruta, filas)`: escribe filas en un archivo CSV.

## Ejemplo mínimo

```cobra
usar "serializacion"

datos = serializacion.decodificar_json("{\"activo\": true}")
texto = serializacion.codificar_json(datos)
imprimir(texto)
```

## Notas de error y degradación segura

- `decodificar_json` debe fallar de forma explícita cuando el texto no sea JSON válido.
- Las operaciones de archivo pueden fallar por permisos, rutas inexistentes o datos que no sean serializables; capturar esos errores en programas que procesen entradas externas.
- Para CSV, normalizar encabezados y codificación cuando el archivo provenga de terceros.
