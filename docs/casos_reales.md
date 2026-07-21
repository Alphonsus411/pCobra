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
cobra run bioinfo.co
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
cobra run ia.co
```
También puedes ejecutar el cuaderno `notebooks/casos_reales/inteligencia_artificial.ipynb` para una versión interactiva.


Necesitarás `scikit-learn`. Las sugerencias de `analizador_agix` usan `agix`, dependencia oficial incluida en la instalación completa de pCobra. Si trabajas con una instalación parcial o un entorno headless donde no está disponible, instala `agix` explícitamente; los demás flujos de Cobra pueden seguir funcionando sin cargar el motor.

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

El módulo `pandas` de la biblioteca estándar facilita leer archivos CSV/JSON y obtener resúmenes estadísticos sin perder la sencillez de Cobra. El siguiente programa carga ventas, filtra los registros incompletos y agrupa por mes para graficar posteriormente con `matplotlib`:

```cobra
usar pandas, matplotlib

ventas = pandas.leer_csv("ventas.csv")
limpias = pandas.filtrar(ventas, lambda fila: fila['monto'] != None)
mensuales = pandas.agrupar_y_resumir(
    limpias,
    por=['mes'],
    agregaciones={'monto': 'sum'}
)

columnas = pandas.a_listas(mensuales)
figura = matplotlib.linea(x=columnas['mes'], y=columnas['monto_sum'])
matplotlib.guardar(figura, "salida.png")
```

Ejecuta el programa así:

```bash
cobra run analisis.co
```
Puedes revisar el cuaderno interactivo `notebooks/casos_reales/analisis_datos.ipynb` para seguirlo paso a paso.

> **Requisitos:** instala `pandas` y `matplotlib`. Si transpiras a JavaScript, las funciones de lectura y estadística (`leer_csv`, `leer_json`, `describir`, `agrupar_y_resumir`) no estarán disponibles y deberás preparar los datos manualmente.

## Aplicación web
Un servicio mínimo con Flask puede generarse y ejecutarse con Cobra:

```cobra
usar flask
app = Flask(__name__)
@app.ruta('/')
def hola():
    regresar 'Hola desde Cobra'
```

Genera y lanza el servidor con flujo unificado:

```bash
cobra build app_web.co
python build/app_web.py
```

> Para forzar backend/ruta de salida en pipelines legacy, consulta `docs/migracion_cli_unificada.md`.

## Videojuego básico
Un pequeño juego usando Pygame:

```cobra
usar pygame
pantalla = pygame.nueva_pantalla(640, 480)
# ... lógica del juego ...
```

Para ejecutarlo:

```bash
cobra build juego.co
python juego.py
```
