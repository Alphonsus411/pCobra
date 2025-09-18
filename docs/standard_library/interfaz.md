# `standard_library.interfaz`

El módulo ofrece utilidades listas para usar con [`rich`](https://rich.readthedocs.io/):

- **`mostrar_tabla(filas, columnas=None, titulo=None, estilos=None)`**: construye una
  tabla a partir de listas de diccionarios o secuencias y la imprime usando la consola
  indicada. Devuelve el objeto `Table` para ajustes adicionales.
- **`mostrar_codigo(codigo, lenguaje)`**: resalta código fuente usando
  [`rich.syntax.Syntax`](https://rich.readthedocs.io/en/stable/syntax.html) y lo
  imprime en la consola indicada. Devuelve el objeto `Syntax` para posteriores
  personalizaciones.
- **`mostrar_markdown(contenido, **opciones)`**: interpreta cadenas Markdown con
  `rich.markdown.Markdown`, incluyendo tablas, listas y resaltado inline. Admite
  pasar argumentos extras compatibles con `Markdown`.
- **`mostrar_json(datos, indent=2, sort_keys=True)`**: serializa diccionarios o
  listas con `rich.json.JSON`. Si recibe una cadena se asume que ya contiene
  JSON válido. Cuando el objeto no puede convertirse automáticamente se
  utiliza `rich.pretty.Pretty` para mostrar su representación.
- **`mostrar_arbol(nodos, titulo=None)`**: convierte diccionarios o listas
  anidadas en un árbol visual basado en `rich.tree.Tree`, ideal para mostrar
  estructuras de carpetas o relaciones jerárquicas.
- **`preguntar_confirmacion(mensaje, por_defecto=True)`**: solicita una respuesta
  afirmativa o negativa mediante `rich.prompt.Confirm`, respetando el valor por
  defecto especificado.
- **`mostrar_panel(contenido, titulo=None, estilo="bold cyan")`**: crea un panel con
  bordes y permite definir el estilo interior y el color del borde.
- **`barra_progreso(descripcion="Progreso", total=None)`**: context manager que
  devuelve el `Progress` de Rich y el identificador de la tarea.
- **`limpiar_consola(console=None)`**: invoca `Console.clear()` sobre la consola
  objetivo.
- **`imprimir_aviso(mensaje, nivel="info")`**: imprime mensajes consistentes con un
  icono y estilo según el nivel.
- **`iniciar_gui`** e **`iniciar_gui_idle`**: lanzan las aplicaciones Flet
  distribuidas con Cobra, validando previamente que la dependencia esté disponible.

```python
from standard_library.interfaz import (
    barra_progreso,
    mostrar_json,
    mostrar_markdown,
    mostrar_arbol,
    mostrar_codigo,
    mostrar_tabla,
)

filas = [
    {"Nombre": "Ada", "Rol": "Pionera"},
    {"Nombre": "Hedy", "Rol": "Educadora"},
]

mostrar_tabla(filas, titulo="Referentes")
mostrar_codigo("print('hola cobra')", "python")
mostrar_markdown("""\
# Informe

- Uso de Markdown desde Cobra
- Integración con Rich
""")
mostrar_json({"lenguaje": "Cobra", "version": "10.0.9"})
mostrar_arbol(
    [
        ("src", ["cobra.co", ("modulos", ["texto.co", "interfaz.co"])])],
    titulo="Proyecto",
)
with barra_progreso(total=3, descripcion="Cargando") as (progreso, tarea):
    for _ in range(3):
        progreso.advance(tarea)
```
