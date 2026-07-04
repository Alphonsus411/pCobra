# `standard_library.compresion`

## Checklist funcional (compresion)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "compresion"`.

### Ejemplo Cobra

```cobra
usar "compresion"
# invoca funciones públicas del módulo
```

# `standard_library.compresion`

## Compresión y archivos ZIP

Compresión de datos y empaquetado o extracción de archivos en formatos comunes.

## API pública principal

- `comprimir(datos)`
- `descomprimir(datos)`
- `crear_zip(ruta_destino, archivos)`
- `extraer_zip(ruta_zip, destino)`

## Uso rápido

```cobra
usar "compresion"
```

Nombres públicos en español (fuente prevista: `__all__`).

## Nota de seguridad

La extracción ZIP debe validar rutas de entrada para impedir escritura fuera del directorio destino (protección contra Zip Slip).
