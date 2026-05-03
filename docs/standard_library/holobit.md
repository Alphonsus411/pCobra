# Módulo `holobit` (contrato público)

El módulo `holobit` disponible vía `usar "holobit"` expone **solo** estas funciones públicas:

- `crear_holobit`
- `validar_holobit`
- `serializar_holobit`
- `deserializar_holobit`
- `proyectar`
- `transformar`
- `graficar`
- `combinar`
- `medir`

## Reglas del contrato

- No se exportan clases ni namespaces internos de Python.
- La estructura de intercambio es serializable y Cobra-compatible:

```json
{"__cobra_tipo__": "holobit", "valores": [1.0, 2.0, 3.0]}
```

- Si `holobit_sdk` está instalado, el adaptador puede usarlo internamente para validar compatibilidad, sin exponer sus símbolos.
- `usar "holobit_sdk"` está prohibido por política de `usar`.

## Ejemplos Cobra

```cobra
usar "holobit"

var a = crear_holobit([1, 2, 3])
var b = crear_holobit([4, 5])

imprimir(validar_holobit(a))
imprimir(graficar(a))
imprimir(medir(a))

var c = combinar(a, b)
var s = serializar_holobit(c)
var d = deserializar_holobit(s)

var r = transformar(d, "rotar", "z", 90)
var p = proyectar(r, "2D")
imprimir(p)
```


## Notas de fachada

- La integración por `usar "holobit"` sanea símbolos y solo inyecta los nombres listados en `__all__`.
- Alias históricos (`crear`, `validar`, etc.) pueden existir internamente por compatibilidad, pero no forman parte del contrato público mínimo.
