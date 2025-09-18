"""Utilidades de interfaz basadas en Rich para programas Cobra y scripts Python."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from contextlib import contextmanager
from typing import Any, Callable, Iterator, Literal

from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table

NivelAviso = Literal["info", "exito", "advertencia", "error"]
FilaTabla = Mapping[str, Any] | Sequence[Any]


def _obtener_console(console: Console | None) -> Console:
    """Devuelve la consola proporcionada o crea una nueva en modo seguro."""

    return console if console is not None else Console()


def _es_secuencia(objeto: FilaTabla) -> bool:
    """Determina si ``objeto`` es una secuencia apta (excluyendo cadenas)."""

    return isinstance(objeto, Sequence) and not isinstance(objeto, (str, bytes, bytearray))


def mostrar_codigo(
    codigo: str,
    lenguaje: str,
    console: Console | None = None,
) -> Any:
    """Resalta ``codigo`` con Rich y lo imprime en la consola indicada."""

    try:
        from rich.syntax import Syntax
    except ModuleNotFoundError as exc:  # pragma: no cover - depende de la instalación de Rich
        raise RuntimeError("Rich no está instalado. Ejecuta 'pip install rich'.") from exc

    console_obj = _obtener_console(console)
    resaltado = Syntax(codigo, lenguaje)
    console_obj.print(resaltado)
    return resaltado


def _agregar_a_arbol(arbol: Any, contenido: Any) -> None:
    if isinstance(contenido, Mapping):
        for clave, valor in contenido.items():
            rama = arbol.add(str(clave))
            _agregar_a_arbol(rama, valor)
    elif isinstance(contenido, tuple) and len(contenido) == 2:
        etiqueta, hijos = contenido
        rama = arbol.add(str(etiqueta))
        _agregar_a_arbol(rama, hijos)
    elif isinstance(contenido, Sequence) and not isinstance(
        contenido, (str, bytes, bytearray)
    ):
        for elemento in contenido:
            _agregar_a_arbol(arbol, elemento)
    elif contenido is not None:
        arbol.add(str(contenido))


def mostrar_arbol(
    nodos: Any,
    *,
    titulo: str | None = None,
    console: Console | None = None,
) -> Any:
    """Construye un árbol visual a partir de ``nodos`` y lo imprime con Rich."""

    try:
        from rich.tree import Tree
    except ModuleNotFoundError as exc:  # pragma: no cover - depende de la instalación de Rich
        raise RuntimeError("Rich no está instalado. Ejecuta 'pip install rich'.") from exc

    etiqueta_raiz = titulo if titulo is not None else "Árbol"
    arbol = Tree(etiqueta_raiz)
    _agregar_a_arbol(arbol, nodos)

    console_obj = _obtener_console(console)
    console_obj.print(arbol)
    return arbol


def preguntar_confirmacion(
    mensaje: str,
    *,
    por_defecto: bool = True,
    console: Console | None = None,
) -> bool:
    """Solicita confirmación al usuario devolviendo ``True`` o ``False``."""

    try:
        from rich.prompt import Confirm
    except ModuleNotFoundError as exc:  # pragma: no cover - depende de la instalación de Rich
        raise RuntimeError("Rich no está instalado. Ejecuta 'pip install rich'.") from exc

    console_obj = _obtener_console(console)
    return Confirm.ask(mensaje, default=por_defecto, console=console_obj)


def mostrar_tabla(
    filas: Iterable[FilaTabla],
    *,
    columnas: Sequence[str] | None = None,
    encabezados: Mapping[str, str] | None = None,
    estilos: Mapping[str, str] | None = None,
    titulo: str | None = None,
    console: Console | None = None,
) -> Table:
    """Construye y muestra una tabla usando :mod:`rich`.

    Args:
        filas: Colección de filas representadas como diccionarios o secuencias.
        columnas: Orden explícito de columnas. Si no se indica se infiere de los datos.
        encabezados: Etiquetas amigables para los nombres de columna.
        estilos: Estilos Rich aplicados a cada columna (``"bold green"``, ``"cyan"``, etc.).
        titulo: Texto a mostrar en la cabecera de la tabla.
        console: Consola Rich destino. Si se omite se crea una temporal.

    Returns:
        La instancia de :class:`rich.table.Table` creada, útil para pruebas o
        personalizaciones adicionales.
    """

    console_obj = _obtener_console(console)
    filas_materializadas = list(filas)

    columnas_finales: list[str]
    if columnas is not None:
        columnas_finales = [str(col) for col in columnas]
    else:
        columnas_finales = []
        for fila in filas_materializadas:
            if isinstance(fila, Mapping):
                for clave in fila.keys():
                    clave_str = str(clave)
                    if clave_str not in columnas_finales:
                        columnas_finales.append(clave_str)
            elif _es_secuencia(fila):
                for indice in range(len(fila)):
                    nombre = f"columna_{indice + 1}"
                    if nombre not in columnas_finales:
                        columnas_finales.append(nombre)

    if not columnas_finales:
        columnas_finales = ["valor"]

    tabla = Table(title=titulo, header_style="bold")
    for columna in columnas_finales:
        encabezado = encabezados.get(columna, columna) if encabezados else columna
        estilo = estilos.get(columna) if estilos else None
        tabla.add_column(encabezado, style=estilo)

    for fila in filas_materializadas:
        if isinstance(fila, Mapping):
            valores = [str(fila.get(col, "")) for col in columnas_finales]
        elif _es_secuencia(fila):
            fila_sec = list(fila)
            valores = [str(valor) for valor in fila_sec]
            if len(valores) < len(columnas_finales):
                valores.extend("" for _ in range(len(columnas_finales) - len(valores)))
            elif len(valores) > len(columnas_finales):
                valores = valores[: len(columnas_finales)]
        else:
            valores = [str(fila)] + [""] * (len(columnas_finales) - 1)
        tabla.add_row(*valores)

    console_obj.print(tabla)
    return tabla


def mostrar_panel(
    contenido: RenderableType,
    *,
    titulo: str | None = None,
    estilo: str | None = "bold cyan",
    borde: str | None = "cyan",
    expandir: bool = True,
    console: Console | None = None,
) -> Panel:
    """Muestra un panel decorado con Rich y devuelve el render creado."""

    panel = Panel(
        contenido,
        title=titulo,
        border_style=borde,
        style=estilo,
        expand=expandir,
    )
    console_obj = _obtener_console(console)
    console_obj.print(panel)
    return panel


@contextmanager
def barra_progreso(
    *,
    descripcion: str = "Progreso",
    total: float | None = None,
    console: Console | None = None,
    transient: bool = True,
) -> Iterator[tuple[Progress, TaskID]]:
    """Context manager que crea una barra de progreso lista para usar."""

    console_obj = _obtener_console(console)

    columnas_barra: list[Any] = [
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
    ]
    if total is not None:
        columnas_barra.append(TextColumn("{task.completed}/{task.total}"))
        columnas_barra.append(TimeRemainingColumn())
    else:
        columnas_barra.append(TextColumn("{task.completed}"))
    columnas_barra.append(TimeElapsedColumn())

    progress = Progress(*columnas_barra, console=console_obj, transient=transient)
    task_id = progress.add_task(descripcion, total=total)

    with progress:
        yield progress, task_id


def limpiar_consola(*, console: Console | None = None) -> None:
    """Limpia la consola utilizando :func:`rich.console.Console.clear`."""

    console_obj = _obtener_console(console)
    console_obj.clear()


_AVISOS: dict[NivelAviso, tuple[str, str]] = {
    "info": ("ℹ", "bold blue"),
    "exito": ("✔", "bold green"),
    "advertencia": ("⚠", "bold yellow"),
    "error": ("✖", "bold red"),
}


def imprimir_aviso(
    mensaje: str,
    *,
    nivel: NivelAviso = "info",
    console: Console | None = None,
    icono: str | None = None,
) -> None:
    """Imprime un mensaje con estilo uniforme para avisos y errores."""

    console_obj = _obtener_console(console)
    simbolo, estilo = _AVISOS.get(nivel, _AVISOS["info"])
    simbolo_final = icono if icono is not None else simbolo
    console_obj.print(f"{simbolo_final} {mensaje}", style=estilo)


GuiTarget = Callable[[Any], None]


def iniciar_gui(*, destino: GuiTarget | None = None, **kwargs: Any) -> None:
    """Inicia la aplicación gráfica principal basada en Flet."""

    try:
        import flet as ft
    except ModuleNotFoundError as exc:  # pragma: no cover - rama dependiente del entorno
        raise RuntimeError("Flet no está instalado. Ejecuta 'pip install flet'.") from exc

    target = destino
    if target is None:
        from pcobra.gui.app import main as target  # type: ignore[assignment]

    ft.app(target=target, **kwargs)


def iniciar_gui_idle(*, destino: GuiTarget | None = None, **kwargs: Any) -> None:
    """Abre el entorno interactivo (IDLE) de Cobra usando Flet."""

    try:
        import flet as ft
    except ModuleNotFoundError as exc:  # pragma: no cover - rama dependiente del entorno
        raise RuntimeError("Flet no está instalado. Ejecuta 'pip install flet'.") from exc

    target = destino
    if target is None:
        from pcobra.gui.idle import main as target  # type: ignore[assignment]

    ft.app(target=target, **kwargs)


__all__ = [
    "mostrar_codigo",  # Resalta fragmentos de código en la consola.
    "mostrar_arbol",  # Renderiza estructuras jerárquicas con Rich Tree.
    "preguntar_confirmacion",  # Pregunta sí/no utilizando ``rich.prompt``.
    "mostrar_tabla",  # Construye tablas a partir de mapeos o secuencias.
    "mostrar_panel",  # Envuelve contenido en paneles estilizados.
    "barra_progreso",  # Proporciona un contexto con barra de progreso.
    "limpiar_consola",  # Limpia la salida de la consola objetivo.
    "imprimir_aviso",  # Muestra mensajes de estado con iconos estándar.
    "iniciar_gui",  # Lanza la aplicación gráfica principal.
    "iniciar_gui_idle",  # Inicia el entorno gráfico de experimentación.
]
