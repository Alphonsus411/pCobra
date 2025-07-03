# Casos de uso reales

Esta sección muestra ejemplos prácticos de cómo emplear la CLI de Cobra en distintos contextos.

Los scripts completos de estos ejemplos se encuentran en la carpeta `casos_reales/` del repositorio.
Se incluyen cuadernos interactivos en `notebooks/casos_reales/` que muestran paso a paso la compilación y ejecución de cada ejemplo.
## Bioinformática
Un pequeño programa puede leer un archivo FASTA y contar el porcentaje de GC:

```cobra
archivo = leer("secuencia.fasta")
conteo = contar_gc(archivo)
imprimir "Porcentaje de GC:", conteo
```

Ejecuta el script con:

```bash
cobra ejecutar bioinfo.co
```
También puedes ejecutar el cuaderno `notebooks/casos_reales/bioinformatica.ipynb` para verlo paso a paso.


Dependencia recomendada: `biopython`.

## Inteligencia Artificial
Cobra se integra con herramientas de IA. Por ejemplo, usando `scikit-learn` o el plugin `analizador_agix`:

```cobra
usar sklearn
modelo = cargar_modelo("modelo.pkl")
resultado = modelo.predecir([1.2, 3.4])
imprimir resultado
```

Para ejecutar:

```bash
cobra ejecutar ia.co
```
También puedes ejecutar el cuaderno `notebooks/casos_reales/inteligencia_artificial.ipynb` para una versión interactiva.


Necesitarás `scikit-learn` y opcionalmente `analizador_agix`.

## Análisis de Datos
Con `pandas` y `matplotlib` puedes procesar CSV y generar gráficos:

```cobra
usar pandas, matplotlib
datos = pandas.leer_csv("datos.csv")
figura = datos.graficar(x="fecha", y="valor")
matplotlib.guardar(figura, "salida.png")
```

Ejecuta el programa así:

```bash
cobra ejecutar analisis.co
```
Puedes revisar el cuaderno interactivo `notebooks/casos_reales/analisis_datos.ipynb` para seguirlo paso a paso.


Instala las dependencias `pandas` y `matplotlib` antes de correrlo.
