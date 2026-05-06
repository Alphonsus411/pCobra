# `standard_library.numero`

## Checklist funcional (numero)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "numero"`.

### Ejemplo Cobra

```cobra
usar "numero"
# invoca funciones públicas del módulo
```

# `standard_library.numero`

El módulo `standard_library.numero` expone los mismos atajos que
`pcobra.corelibs.numero`, pero empaquetados para usarse directamente desde
programas escritos en Cobra o en Python transpilar. Además de las utilidades
clásicas como `signo`, `limitar` o `envolver_modular`, ahora incluye métricas
estadísticas pensadas para análisis exploratorios rápidos:

- `varianza` y `varianza_muestral` replican la semántica de `statistics` para
  calcular dispersión poblacional o muestral.
- `media_geometrica` y `media_armonica` permiten trabajar con tasas de
  crecimiento o promedios ponderados inversamente sin perder validaciones.
- `percentil`, `cuartiles` y `rango_intercuartil` usan interpolación lineal
  compatible con NumPy para describir la distribución de una serie.
- `coeficiente_variacion` normaliza la desviación estándar respecto a la media,
  con modos poblacional y muestral según se necesite.
- `hipotenusa` calcula la magnitud de vectores 2D/3D sin perder precisión.
- `distancia_euclidiana` obtiene la separación entre puntos iterables.

```cobra
import standard_library.numero as numero

datos = [2, 4, 4, 4, 5, 5, 7, 9]

imprimir(numero.varianza(datos))                  # 2.0
imprimir(numero.media_armonica([1.5, 2.5, 4.0]))  # 2.373...
q1, q2, q3 = numero.cuartiles(datos)
imprimir((q1, q2, q3))                            # (3.5, 4.5, 5.5)
imprimir(numero.coeficiente_variacion(datos))     # 0.2828...

punto_a = (0.0, 0.0, 0.0)
punto_b = (1.0, 2.0, 2.0)
imprimir(numero.hipotenusa(3.0, 4.0))             # 5.0
imprimir(numero.distancia_euclidiana(punto_a, punto_b))  # 3.0
```

Estas funciones siguen las mismas validaciones que sus equivalentes en
`corelibs`, por lo que secuencias vacías o valores no numéricos producen errores
explícitos tanto en Python como en los demás backends soportados.

<!-- BEGIN: AUTO-STDLIB-FUNCTIONS -->
## API pública sincronizada (`standard_library.numero`)

| Función |
|---|
| `coeficiente_variacion` |
| `combinaciones` |
| `copiar_signo` |
| `cuartiles` |
| `distancia_euclidiana` |
| `envolver_modular` |
| `es_finito` |
| `es_infinito` |
| `es_nan` |
| `hipotenusa` |
| `interpolar` |
| `limitar` |
| `media_armonica` |
| `media_geometrica` |
| `percentil` |
| `permutaciones` |
| `raiz_entera` |
| `rango_intercuartil` |
| `signo` |
| `suma_precisa` |
| `varianza` |
| `varianza_muestral` |
<!-- END: AUTO-STDLIB-FUNCTIONS -->

- `aleatorio_entero(minimo, maximo, semilla=None)` genera enteros inclusivos estilo `randint` con nombre Cobra.
