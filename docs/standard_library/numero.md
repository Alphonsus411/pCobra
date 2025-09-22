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

```cobra
import standard_library.numero as numero

datos = [2, 4, 4, 4, 5, 5, 7, 9]

imprimir(numero.varianza(datos))                  # 2.0
imprimir(numero.media_armonica([1.5, 2.5, 4.0]))  # 2.373...
q1, q2, q3 = numero.cuartiles(datos)
imprimir((q1, q2, q3))                            # (3.5, 4.5, 5.5)
imprimir(numero.coeficiente_variacion(datos))     # 0.2828...
```

Estas funciones siguen las mismas validaciones que sus equivalentes en
`corelibs`, por lo que secuencias vacías o valores no numéricos producen errores
explícitos tanto en Python como en los demás backends soportados.
