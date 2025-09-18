# `standard_library.interfaz`

El módulo ofrece utilidades listas para usar con [`rich`](https://rich.readthedocs.io/):

- **`mostrar_tabla(filas, columnas=None, titulo=None, estilos=None)`**: construye una
  tabla a partir de listas de diccionarios o secuencias y la imprime usando la consola
  indicada. Devuelve el objeto `Table` para ajustes adicionales.
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
from standard_library.interfaz import mostrar_tabla, barra_progreso

filas = [
    {"Nombre": "Ada", "Rol": "Pionera"},
    {"Nombre": "Hedy", "Rol": "Educadora"},
]

mostrar_tabla(filas, titulo="Referentes")
with barra_progreso(total=3, descripcion="Cargando") as (progreso, tarea):
    for _ in range(3):
        progreso.advance(tarea)
```
