# `standard_library.configuracion`

## Propósito

`configuracion` carga archivos de configuración en formatos simples y permite detectar capacidades disponibles del runtime, especialmente soporte TOML.

## Funciones públicas

- `leer_toml(ruta)`: lee configuración TOML desde un archivo.
- `leer_ini(ruta)`: lee configuración INI.
- `toml_disponible()`: indica si el runtime tiene parser TOML disponible.
- `leer_configuracion(ruta)`: lee configuración según la extensión soportada.

## Ejemplo mínimo

```cobra
usar "configuracion"

si configuracion.toml_disponible():
    cfg = configuracion.leer_toml("pyproject.toml")
sino:
    cfg = configuracion.leer_ini("app.ini")
```

## Notas de error y degradación segura

- `leer_toml` depende de `tomllib`; si no está disponible, debe fallar con un mensaje claro o permitir usar `leer_ini`/otro backend compatible como alternativa.
- `leer_configuracion` debe rechazar extensiones no soportadas en lugar de interpretar formatos desconocidos de forma ambigua.
- Validar valores obligatorios después de cargar el archivo y aplicar valores por defecto para claves opcionales.
