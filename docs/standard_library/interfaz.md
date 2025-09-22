# `standard_library.interfaz`

El módulo ofrece utilidades listas para usar con [`rich`](https://rich.readthedocs.io/):

- **`mostrar_tabla(filas, columnas=None, titulo=None, estilos=None)`**: construye una
  tabla a partir de listas de diccionarios o secuencias y la imprime usando la consola
  indicada. Devuelve el objeto `Table` para ajustes adicionales.
- **`mostrar_columnas(elementos, numero_columnas=None, titulo=None)`**: reparte una
  lista de elementos en columnas equilibradas con la ayuda de `rich.columns.Columns`.
  Ideal para recrear listados tipo `console.table` sin construir tablas completas.
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
- **`preguntar_password(mensaje, validar=None)`**: pide una contraseña ocultando
  la entrada. Puede recibir una función de validación para repetir el prompt
  hasta obtener una respuesta válida.
- **`preguntar_opciones_multiple(mensaje, opciones, minimo=1, maximo=None)`**:
  permite seleccionar varias opciones a la vez introduciendo números o textos
  separados por comas. Devuelve una lista con los elementos elegidos en el mismo
  orden en el que fueron reconocidos.
- **`mostrar_panel(contenido, titulo=None, estilo="bold cyan")`**: crea un panel con
  bordes y permite definir el estilo interior y el color del borde.
- **`grupo_consola(titulo=None)`**: context manager que agrupa varias impresiones con
  sangría, emulando el comportamiento de `console.group` del navegador.
- **`barra_progreso(descripcion="Progreso", total=None)`**: context manager que
  devuelve el `Progress` de Rich y el identificador de la tarea.
- **`limpiar_consola(console=None)`**: invoca `Console.clear()` sobre la consola
  objetivo.
- **`imprimir_aviso(mensaje, nivel="info")`**: imprime mensajes consistentes con un
  icono y estilo según el nivel.
- **`mostrar_tabla_paginada(filas, tamano_pagina=10)`**: divide colecciones largas
  en varias tablas mostrando cada bloque por separado y preguntando si se desea
  continuar. Devuelve una lista con las tablas generadas.
- **`iniciar_gui`** e **`iniciar_gui_idle`**: lanzan las aplicaciones Flet
  distribuidas con Cobra, validando previamente que la dependencia esté disponible.

```python
from standard_library.interfaz import (
    barra_progreso,
    grupo_consola,
    mostrar_columnas,
    mostrar_codigo,
    mostrar_json,
    mostrar_markdown,
    mostrar_arbol,
    mostrar_tabla,
    mostrar_tabla_paginada,
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

# Agrupar mensajes para simular console.group/console.table
with grupo_consola(titulo="Resultados") as consola:
    consola.print("Resumen general")
    mostrar_columnas(
        ["Ada", "Hedy", "Grace", "Radia"],
        numero_columnas=2,
        console=consola,
        titulo="Participantes",
    )

# Nuevos prompts interactivos

Los prompts basados en `rich.prompt` comparten el mismo patrón de uso y devuelven
tipos nativos de Python para integrarlos fácilmente en scripts.

```python
from standard_library.interfaz import (
    preguntar_password,
    preguntar_opciones_multiple,
)

clave = preguntar_password("Introduce la clave del servicio")
etiquetas = preguntar_opciones_multiple(
    "Selecciona etiquetas",
    opciones=["backend", "frontend", "devops", "datos"],
    minimo=2,
    maximo=3,
)
print({"clave": clave, "etiquetas": etiquetas})

tablas = mostrar_tabla_paginada(
    filas=filas,
    tamano_pagina=1,
    titulo="Referentes",
)
print(f"Se mostraron {len(tablas)} páginas")
```

> **Compatibilidad:** todas las funciones que dependen de Rich realizan una
> comprobación previa y levantan `RuntimeError` cuando la librería no está
> instalada. En entornos sin Rich puedes sustituirlas o envolverlas en bloques
> `try/except` según tus necesidades.
```
