"""Utilidades de interfaz basadas en Rich para programas Cobra y scripts Python."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from contextlib import contextmanager
from typing import Any, Callable, Iterator, Literal

from rich.columns import Columns
from rich.console import Console, Group, RenderableType
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
from rich.padding import Padding
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


def mostrar_markdown(
    contenido: str,
    *,
    console: Console | None = None,
    **markdown_kwargs: Any,
) -> Any:
    """Renderiza texto Markdown con Rich y lo envía a la consola indicada."""

    try:
        from rich.markdown import Markdown
    except ModuleNotFoundError as exc:  # pragma: no cover - depende de la instalación de Rich
        raise RuntimeError("Rich no está instalado. Ejecuta 'pip install rich'.") from exc

    render = Markdown(contenido, **markdown_kwargs)

    console_obj = _obtener_console(console)
    console_obj.print(render)
    return render


def mostrar_json(
    datos: Any,
    *,
    console: Console | None = None,
    indent: int | None = 2,
    sort_keys: bool = True,
) -> Any:
    """Muestra datos JSON o estructuras Python con formato legible."""

    try:
        from rich.json import JSON
        from rich.pretty import Pretty
    except ModuleNotFoundError as exc:  # pragma: no cover - depende de la instalación de Rich
        raise RuntimeError("Rich no está instalado. Ejecuta 'pip install rich'.") from exc

    console_obj = _obtener_console(console)

    render: Any
    if isinstance(datos, str):
        render = JSON(datos, indent=indent)
    else:
        try:
            render = JSON.from_data(datos, indent=indent, sort_keys=sort_keys)
        except (TypeError, ValueError):
            render = Pretty(datos)

    console_obj.print(render)
    return render


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


def preguntar_texto(
    mensaje: str,
    *,
    por_defecto: str | None = None,
    console: Console | None = None,
    validar: Callable[[str], bool] | None = None,
    mensaje_error: str = "Entrada inválida, intenta nuevamente.",
) -> str:
    """Solicita texto libre y permite validar el resultado."""

    try:
        from rich.prompt import Prompt
    except ModuleNotFoundError as exc:  # pragma: no cover - depende de la instalación de Rich
        raise RuntimeError("Rich no está instalado. Ejecuta 'pip install rich'.") from exc

    console_obj = _obtener_console(console)

    while True:
        respuesta = Prompt.ask(
            mensaje,
            default=por_defecto,
            console=console_obj,
            show_default=por_defecto is not None,
        )
        if validar is None or validar(respuesta):
            return respuesta
        console_obj.print(f"[red]{mensaje_error}[/red]")


def preguntar_opcion(
    mensaje: str,
    opciones: Sequence[Any],
    *,
    por_defecto: Any | None = None,
    console: Console | None = None,
    mostrar_opciones: bool = True,
) -> str:
    """Solicita al usuario elegir un elemento de ``opciones``."""

    try:
        from rich.prompt import Prompt
    except ModuleNotFoundError as exc:  # pragma: no cover - depende de la instalación de Rich
        raise RuntimeError("Rich no está instalado. Ejecuta 'pip install rich'.") from exc

    if not opciones:
        raise ValueError("Debes proporcionar al menos una opción para elegir.")

    opciones_texto = [str(opcion) for opcion in opciones]
    valor_defecto: str | None = None
    if por_defecto is not None:
        valor_defecto = str(por_defecto)
        if valor_defecto not in opciones_texto:
            raise ValueError("El valor por defecto debe estar dentro de las opciones.")

    console_obj = _obtener_console(console)
    return Prompt.ask(
        mensaje,
        choices=opciones_texto,
        default=valor_defecto,
        console=console_obj,
        show_choices=mostrar_opciones,
        show_default=valor_defecto is not None,
    )


def preguntar_entero(
    mensaje: str,
    *,
    por_defecto: int | None = None,
    minimo: int | None = None,
    maximo: int | None = None,
    console: Console | None = None,
    mensaje_error: str = "Introduce un número entero válido.",
) -> int:
    """Solicita al usuario un número entero y valida rangos opcionales."""

    try:
        from rich.prompt import IntPrompt
    except ModuleNotFoundError as exc:  # pragma: no cover - depende de la instalación de Rich
        raise RuntimeError("Rich no está instalado. Ejecuta 'pip install rich'.") from exc

    if minimo is not None and maximo is not None and minimo > maximo:
        raise ValueError("El mínimo no puede ser mayor que el máximo.")

    if por_defecto is not None:
        if minimo is not None and por_defecto < minimo:
            raise ValueError("El valor por defecto es menor que el mínimo permitido.")
        if maximo is not None and por_defecto > maximo:
            raise ValueError("El valor por defecto es mayor que el máximo permitido.")

    console_obj = _obtener_console(console)

    while True:
        respuesta = IntPrompt.ask(
            mensaje,
            default=por_defecto,
            console=console_obj,
            show_default=por_defecto is not None,
        )
        if minimo is not None and respuesta < minimo:
            console_obj.print(
                f"[red]{mensaje_error} Debe ser mayor o igual a {minimo}.[/red]"
            )
            continue
        if maximo is not None and respuesta > maximo:
            console_obj.print(
                f"[red]{mensaje_error} Debe ser menor o igual a {maximo}.[/red]"
            )
            continue
        return respuesta


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


def mostrar_columnas(
    elementos: Iterable[RenderableType | str],
    *,
    numero_columnas: int | None = None,
    titulo: str | None = None,
    expandir: bool = True,
    igualar_ancho: bool = False,
    alinear: Literal["left", "center", "right"] | None = None,
    padding: int | tuple[int, int] | tuple[int, int, int, int] = (0, 1),
    console: Console | None = None,
) -> Columns:
    """Crea una cuadrícula de elementos utilizando ``rich.columns.Columns``.

    Args:
        elementos: Colección de textos o renderizables Rich que se mostrarán.
        numero_columnas: Máximo de columnas deseadas. Los elementos se reparten de
            izquierda a derecha y, si se excede el límite, se agrupan verticalmente
            por columnas. Cuando es ``None`` se deja que Rich decida el número.
        titulo: Encabezado opcional a mostrar sobre el bloque de columnas.
        expandir: Si ``True`` la cuadrícula ocupará todo el ancho disponible.
        igualar_ancho: Fuerza a que todas las columnas midan lo mismo.
        alinear: Alineación del contenido (``"left"``, ``"center"`` o ``"right"``).
        padding: Relleno aplicado a cada celda (top, right, bottom, left).
        console: Instancia de :class:`rich.console.Console` en la que imprimir.

    Returns:
        La instancia de :class:`rich.columns.Columns` generada, útil para pruebas o
        reutilización posterior.
    """

    console_obj = _obtener_console(console)
    renderizables = list(elementos)

    if numero_columnas is not None:
        if numero_columnas <= 0:
            raise ValueError("numero_columnas debe ser un entero positivo")
        if renderizables:
            limite = min(numero_columnas, len(renderizables))
            columnas_virtuales: list[list[RenderableType | str]] = [
                [] for _ in range(limite)
            ]
            for indice, renderizable in enumerate(renderizables):
                columnas_virtuales[indice % limite].append(renderizable)
            renderizables = [
                Group(*columna)
                if len(columna) > 1
                else columna[0]
                for columna in columnas_virtuales
            ]
        else:
            renderizables = []

    columnas_render = Columns(
        renderizables,
        padding=padding,
        expand=expandir,
        equal=igualar_ancho,
        align=alinear,
        title=titulo,
    )
    console_obj.print(columnas_render)
    return columnas_render


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
def grupo_consola(
    titulo: str | None = None,
    *,
    console: Console | None = None,
    sangria: int = 4,
    estilo_titulo: str | None = "bold",
) -> Iterator[Console]:
    """Agrupa múltiples impresiones siguiendo la semántica de ``console.group``.

    Si la instancia de :class:`rich.console.Console` proporcionada ya implementa
    ``group`` se delega directamente en ella. En caso contrario se simula el
    agrupado capturando las impresiones, añadiendo un título opcional y aplicando
    sangría mediante :class:`rich.padding.Padding`.

    Args:
        titulo: Texto que encabezará el grupo. En la simulación se imprime antes
            del contenido indentado.
        console: Consola Rich a utilizar. Si no se indica se creará una nueva.
        sangria: Número de espacios usados para indentar en la simulación.
        estilo_titulo: Estilo Rich aplicado al título cuando se imprime manualmente.

    Yields:
        La consola sobre la que imprimir los mensajes agrupados.
    """

    console_obj = _obtener_console(console)
    group_callable = getattr(console_obj, "group", None)
    if callable(group_callable):
        args = (titulo,) if titulo is not None else ()
        try:
            contexto = group_callable(*args)
        except TypeError:
            contexto = None
        else:
            if hasattr(contexto, "__enter__") and hasattr(contexto, "__exit__"):
                with contexto:
                    yield console_obj
                return

    class _GrupoProxy:
        def __init__(self, base: Console) -> None:
            self._base = base
            self._llamadas: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

        def print(self, *objetos: Any, **kwargs: Any) -> None:  # type: ignore[override]
            self._llamadas.append((objetos, kwargs))

        def __getattr__(self, nombre: str) -> Any:
            return getattr(self._base, nombre)

    proxy = _GrupoProxy(console_obj)
    try:
        yield proxy  # type: ignore[misc]
    finally:
        llamadas = proxy._llamadas
        if titulo is not None:
            console_obj.print(titulo, style=estilo_titulo)
        for args, kwargs in llamadas:
            if not args:
                console_obj.print(**kwargs)
                continue
            if len(args) == 1:
                renderizable = args[0]
            else:
                renderizable = Group(*args)
            console_obj.print(Padding(renderizable, (0, 0, 0, sangria)), **kwargs)


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
    "mostrar_markdown",  # Renderiza texto Markdown enriquecido.
    "mostrar_json",  # Formatea estructuras o cadenas JSON.
    "mostrar_arbol",  # Renderiza estructuras jerárquicas con Rich Tree.
    "preguntar_confirmacion",  # Pregunta sí/no utilizando ``rich.prompt``.
    "mostrar_tabla",  # Construye tablas a partir de mapeos o secuencias.
    "mostrar_columnas",  # Organiza elementos en un diseño de columnas.
    "mostrar_panel",  # Envuelve contenido en paneles estilizados.
    "grupo_consola",  # Agrupa mensajes con sangría estilo consola.
    "barra_progreso",  # Proporciona un contexto con barra de progreso.
    "limpiar_consola",  # Limpia la salida de la consola objetivo.
    "imprimir_aviso",  # Muestra mensajes de estado con iconos estándar.
    "iniciar_gui",  # Lanza la aplicación gráfica principal.
    "iniciar_gui_idle",  # Inicia el entorno gráfico de experimentación.
]
