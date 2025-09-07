# Casos de uso reales

Esta sección muestra ejemplos prácticos de cómo emplear la CLI de Cobra en distintos contextos.

Los scripts completos de estos ejemplos se encuentran en la carpeta `examples/casos_reales/` del repositorio.
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

El plugin `analizador_agix` soporta modulación emocional mediante los
parámetros `placer`, `activacion` y `dominancia`, cada uno en el rango
de `-1` a `1`.

```cobra
usar analizador_agix
codigo = "imprimir \"hola\""
sugerencias = analizador_agix.generar_sugerencias(codigo, placer=0.5, activacion=0.3, dominancia=-0.2)
imprimir sugerencias[0]
```

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

## Aplicación web
Un servicio mínimo con Flask puede generarse y ejecutarse con Cobra:

```cobra
usar flask
app = Flask(__name__)
@app.ruta('/')
def hola():
    regresar 'Hola desde Cobra'
```

Compila y lanza el servidor con:

```bash
cobra compilar app_web.co --a python -o build/app_web.py
python build/app_web.py
```

## Videojuego básico
Un pequeño juego usando Pygame:

```cobra
usar pygame
pantalla = pygame.nueva_pantalla(640, 480)
# ... lógica del juego ...
```

Para ejecutarlo:

```bash
cobra compilar juego.co --a python
python juego.py
```
