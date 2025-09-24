import dataclasses
import importlib.machinery
import importlib.util
from pathlib import Path
import sys
import threading
import time
import types
from typing import Any, Awaitable, Callable

import pytest

MODULO = Path(__file__).resolve().parents[2] / "src" / "pcobra" / "standard_library" / "decoradores.py"
ESPEC = importlib.util.spec_from_file_location("standard_library.decoradores", MODULO)
assert ESPEC is not None and ESPEC.loader is not None

pcobra_pkg = sys.modules.setdefault("pcobra", types.ModuleType("pcobra"))
corelibs_pkg = sys.modules.setdefault("pcobra.corelibs", types.ModuleType("pcobra.corelibs"))
standard_library_pkg = sys.modules.setdefault(
    "pcobra.standard_library", types.ModuleType("pcobra.standard_library")
)

rich_pkg = sys.modules.setdefault("rich", types.ModuleType("rich"))
rich_console_pkg = sys.modules.setdefault("rich.console", types.ModuleType("rich.console"))


class _ConsoleStub:
    def print(self, *_: Any, **__: Any) -> None:
        pass


setattr(rich_console_pkg, "Console", _ConsoleStub)
setattr(rich_pkg, "console", rich_console_pkg)
rich_pkg.__spec__ = importlib.machinery.ModuleSpec("rich", loader=None)
rich_console_pkg.__spec__ = importlib.machinery.ModuleSpec("rich.console", loader=None)


async def _corelibs_stub(*args: Any, **kwargs: Any) -> Any:
    raise RuntimeError("reintentar_async no configurado en stub")


setattr(corelibs_pkg, "reintentar_async", _corelibs_stub)
setattr(pcobra_pkg, "corelibs", corelibs_pkg)
setattr(pcobra_pkg, "standard_library", standard_library_pkg)

decoradores = importlib.util.module_from_spec(ESPEC)
sys.modules.setdefault(ESPEC.name, decoradores)
ESPEC.loader.exec_module(decoradores)
sys.modules["pcobra.standard_library.decoradores"] = decoradores

memoizar = decoradores.memoizar
dataclase = decoradores.dataclase
temporizar = decoradores.temporizar
depreciado = decoradores.depreciado
sincronizar = decoradores.sincronizar
reintentar = decoradores.reintentar
reintentar_async = decoradores.reintentar_async
orden_total = decoradores.orden_total
despachar_por_tipo = decoradores.despachar_por_tipo


def test_memoizar_cachea_resultados():
    contador = {"llamadas": 0}

    @memoizar(maxsize=None)
    def sumar(x: int, y: int) -> int:
        contador["llamadas"] += 1
        return x + y

    assert sumar(1, 2) == 3
    assert sumar(1, 2) == 3
    assert sumar(2, 3) == 5
    assert contador["llamadas"] == 2


def test_dataclase_crea_dataclass():
    @dataclase(order=True)
    class Punto:
        x: int
        y: int

    assert dataclasses.is_dataclass(Punto)
    assert Punto(1, 2) < Punto(2, 3)


class ConsolaFalsa:
    def __init__(self) -> None:
        self.mensajes: list[str] = []
        self.estilos: list[str | None] = []

    def print(self, mensaje: str, *, style: str | None = None) -> None:
        self.mensajes.append(mensaje)
        self.estilos.append(style)


def test_temporizar_reporta_duracion(monkeypatch: pytest.MonkeyPatch):
    consola = ConsolaFalsa()
    tiempos = iter([1.0, 3.5])

    def perf_counter_falso() -> float:
        return next(tiempos)

    monkeypatch.setattr(decoradores.time, "perf_counter", perf_counter_falso)

    @temporizar(etiqueta="prueba", consola=consola, precision=2)
    def tarea() -> str:
        return "ok"

    assert tarea() == "ok"
    assert consola.mensajes == ["[prueba] 2.50 s"]
    assert consola.estilos == [None]


def test_depreciado_emite_advertencia(monkeypatch: pytest.MonkeyPatch):
    consola = ConsolaFalsa()

    @depreciado(mensaje="Usa `nuevo`", consola=consola)
    def funcion_obsoleta() -> str:
        return "hecho"

    with pytest.warns(DeprecationWarning) as advertencias:
        assert funcion_obsoleta() == "hecho"

    assert advertencias[0].message.args[0] == "Usa `nuevo`"
    assert consola.mensajes == ["Usa `nuevo`"]
    assert consola.estilos == ["bold yellow"]


def test_sincronizar_evita_concurrencia():
    errores: list[str] = []
    en_ejecucion = threading.Event()

    @sincronizar()
    def seccion_critica() -> None:
        if en_ejecucion.is_set():
            errores.append("concurrencia")
        en_ejecucion.set()
        time.sleep(0.01)
        en_ejecucion.clear()

    hilos = [threading.Thread(target=seccion_critica) for _ in range(2)]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()

    assert errores == []


def test_reintentar_aplica_reintentos(monkeypatch: pytest.MonkeyPatch):
    consola = ConsolaFalsa()
    esperas: list[float] = []

    def sleep_falso(segundos: float) -> None:
        esperas.append(segundos)

    monkeypatch.setattr(decoradores.time, "sleep", sleep_falso)

    contador = {"llamadas": 0}

    @reintentar(
        intentos=3,
        excepciones=(ValueError,),
        retardo_inicial=0.5,
        factor_backoff=2,
        consola=consola,
    )
    def fragil() -> str:
        contador["llamadas"] += 1
        if contador["llamadas"] < 3:
            raise ValueError("fallo")
        return "ok"

    assert fragil() == "ok"
    assert contador["llamadas"] == 3
    assert esperas == [0.5, 1.0]
    assert len(consola.mensajes) == 2
    assert consola.mensajes[0].endswith("reintento 2/3")
    assert consola.mensajes[1].endswith("reintento 3/3")
    assert consola.mensajes[0].startswith("[reintentar:")
    assert consola.estilos == ["bold yellow", "bold yellow"]


@pytest.mark.asyncio
async def test_reintentar_async_envuelve_corelibs(monkeypatch: pytest.MonkeyPatch):
    consola = ConsolaFalsa()
    llamadas = {"contador": 0}

    async def reintentar_falso(
        funcion: Callable[[], Awaitable[str]],
        *,
        intentos: int,
        excepciones: tuple[type[BaseException], ...],
        retardo_inicial: float,
        factor_backoff: float,
        max_retardo: float | None,
        jitter: Any,
    ) -> str:
        assert intentos == 3
        assert excepciones == (RuntimeError,)
        assert retardo_inicial == 0.1
        assert factor_backoff == 2.0
        assert max_retardo is None
        assert jitter is None
        ultimo_error: BaseException | None = None
        for numero in range(1, intentos + 1):
            try:
                return await funcion()
            except excepciones as exc:  # type: ignore[misc]
                ultimo_error = exc
                if numero == intentos:
                    raise
        assert ultimo_error is not None
        raise ultimo_error

    monkeypatch.setattr(decoradores, "_reintentar_async", reintentar_falso)

    @reintentar_async(intentos=3, excepciones=(RuntimeError,), consola=consola, etiqueta="tarea")
    async def fragil() -> str:
        llamadas["contador"] += 1
        if llamadas["contador"] < 2:
            raise RuntimeError("fallo")
        return "listo"

    assert await fragil() == "listo"
    assert llamadas["contador"] == 2
    assert len(consola.mensajes) == 1
    assert consola.mensajes[0].endswith("reintento 2/3")
    assert consola.mensajes[0].startswith("[reintentar:")
    assert consola.estilos == ["bold yellow"]


def test_orden_total_completa_operadores() -> None:
    @orden_total
    class Carta:
        def __init__(self, valor: int, palo: str) -> None:
            self.valor = valor
            self.palo = palo

        def __eq__(self, otro: object) -> bool:
            if not isinstance(otro, Carta):
                return NotImplemented
            return (self.valor, self.palo) == (otro.valor, otro.palo)

        def __lt__(self, otro: "Carta") -> bool:
            return (self.valor, self.palo) < (otro.valor, otro.palo)

    menor = Carta(1, "bastos")
    medio = Carta(1, "copas")
    mayor = Carta(2, "oros")

    assert menor <= medio <= mayor
    assert mayor >= medio > menor
    assert menor != mayor
    assert not (mayor < menor)


def test_orden_total_requiere_clase() -> None:
    with pytest.raises(TypeError):
        orden_total(lambda: None)


def test_despachar_por_tipo_registra_y_despacha() -> None:
    @despachar_por_tipo
    def describir(valor: object) -> str:
        return f"Valor genérico: {valor!r}"

    @describir.registrar(int)
    def _(valor: int) -> str:
        return f"Entero: {valor}"

    @describir.registrar(str)
    def _(valor: str) -> str:
        return f"Cadena: {valor}".upper()

    assert describir(5) == "Entero: 5"
    assert describir("hola") == "CADENA: HOLA"
    assert describir(5.0).startswith("Valor genérico")

    handler = describir.despachar(int)
    assert handler(3) == "Entero: 3"
    assert int in describir.registros

    with pytest.raises(TypeError):
        describir.registrar("no es un tipo")  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        describir.despachar("no es un tipo")  # type: ignore[arg-type]
