# `standard_library.compresion`

## Propósito

`compresion` cubre operaciones básicas con archivos ZIP: crear paquetes, extraerlos y listar su contenido.

## Funciones públicas

- `crear_zip(destino, rutas)`: crea un archivo ZIP con una o varias rutas.
- `extraer_zip(ruta_zip, destino)`: extrae un ZIP en un directorio destino.
- `listar_zip(ruta_zip)`: devuelve los nombres incluidos en un ZIP.

## Ejemplo mínimo

```cobra
usar "compresion"

compresion.crear_zip("salida.zip", ["datos/entrada.txt"])
entradas = compresion.listar_zip("salida.zip")
imprimir(entradas)
```

## Notas de error y degradación segura

- `extraer_zip` debe validar las rutas internas para impedir escritura fuera del directorio destino (protección contra Zip Slip).
- Archivos corruptos, rutas inexistentes o permisos insuficientes deben tratarse como errores controlados.
