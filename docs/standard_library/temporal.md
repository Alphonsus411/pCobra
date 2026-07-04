# `standard_library.temporal`

## Propósito

`temporal` gestiona archivos y directorios temporales para pruebas, scripts y tareas intermedias que requieren almacenamiento efímero.

## Funciones públicas

- `archivo_temporal(prefijo=None, sufijo=None)`: crea o reserva un archivo temporal.
- `directorio_temporal(prefijo=None)`: crea un directorio temporal.
- `limpiar(ruta)`: elimina de forma controlada un recurso temporal creado previamente.

## Ejemplo mínimo

```cobra
usar "temporal"

ruta_tmp = temporal.archivo_temporal("cobra-", ".txt")
# escribir datos temporales aquí
temporal.limpiar(ruta_tmp)
```

## Notas de error y degradación segura

- `limpiar` debe rechazar rutas vacías para evitar borrados accidentales.
- Usar directorios temporales del sistema y limpiar al terminar para no dejar archivos residuales con datos sensibles.
