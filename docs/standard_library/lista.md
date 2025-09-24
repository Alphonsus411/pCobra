El módulo `standard_library.lista` envuelve transformaciones comunes sobre
secuencias, manteniendo validaciones descriptivas y compatibilidad con los
transpiladores soportados. A diferencia de las utilidades de bajo nivel en
`pcobra.corelibs.coleccion`, aquí las funciones convierten siempre la entrada a
listas nativas para simplificar el trabajo con valores provenientes de Cobra.

## `mapear_aplanado(lista, funcion)`

Combina el mapeo con un aplanado de un nivel. Cada elemento de `lista` se pasa a
`funcion` y el iterable devuelto se concatena sobre el resultado final
respetando el orden. Si la función produce un valor que no sea iterable se
lanza `TypeError` para alertar del uso incorrecto.

```cobra
import standard_library.lista as lista

var rutas = [
    {"origen": "A", "destinos": ["B", "C"]},
    {"origen": "B", "destinos": ("C", "D")},
]

var conexiones = lista.mapear_aplanado(
    rutas,
    lambda registro: [registro["origen"]] + registro["destinos"],
)
# -> ["A", "B", "C", "B", "C", "D"]
```

El resultado es siempre una lista nueva, por lo que los datos originales no se
modifican. Al trabajar con generadores o rangos se consumen una única vez y se
preservan los tipos de sus elementos.
