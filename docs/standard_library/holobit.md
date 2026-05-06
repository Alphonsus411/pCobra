# `standard_library.holobit`

## Checklist funcional (holobit)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "holobit"`.

### Ejemplo Cobra

```cobra
usar "holobit"
# invoca funciones públicas del módulo
```

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
{"tipo":"holobit","valores":[1.0,2.0,3.0]}
```

- El módulo no expone `holobit_sdk`, clases internas ni helpers privados; cualquier acceso directo a esos símbolos se considera fuga y debe fallar en pruebas.
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
