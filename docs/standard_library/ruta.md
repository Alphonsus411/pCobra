# `standard_library.ruta`

## Propósito

`ruta` reúne utilidades para componer, normalizar e inspeccionar rutas de archivo de forma portable, evitando depender de separadores específicos del sistema operativo anfitrión.

## Funciones públicas

- `unir(*partes)`: combina segmentos de ruta en una sola ruta.
- `normalizar(ruta)`: elimina redundancias como `.` o separadores duplicados.
- `nombre(ruta)`: devuelve el nombre final del archivo o directorio.
- `extension(ruta)`: devuelve la extensión del nombre final.
- `padre(ruta)`: obtiene el directorio padre.
- `existe(ruta)`: indica si la ruta existe en el sistema de archivos.
- `es_absoluta(ruta)`: comprueba si la ruta es absoluta.
- `absoluta(ruta)`: convierte una ruta a su forma absoluta.
- `relativa(ruta, inicio=None)`: calcula una ruta relativa desde `inicio` o desde el directorio actual.

## Ejemplo mínimo

```cobra
usar "ruta"

archivo = ruta.unir("datos", "entrada.json")
normalizado = ruta.normalizar(archivo)
si ruta.existe(normalizado):
    imprimir(ruta.nombre(normalizado))
```

## Notas de error y degradación segura

- Las funciones que consultan el sistema de archivos, como `existe`, pueden devolver `falso` si la ruta no existe o si el entorno no permite acceder a ella.
- Validar entradas recibidas de usuarios antes de construir rutas para evitar escrituras o lecturas fuera de los directorios esperados.
