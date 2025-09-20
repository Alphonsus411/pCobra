import dataclasses
import importlib.util
from pathlib import Path
import sys
import types

import pytest

MODULO = Path(__file__).resolve().parents[2] / "src" / "pcobra" / "standard_library" / "decoradores.py"
ESPEC = importlib.util.spec_from_file_location("standard_library.decoradores", MODULO)
assert ESPEC is not None and ESPEC.loader is not None
decoradores = importlib.util.module_from_spec(ESPEC)
sys.modules.setdefault(ESPEC.name, decoradores)
ESPEC.loader.exec_module(decoradores)

pcobra_pkg = sys.modules.setdefault("pcobra", types.ModuleType("pcobra"))
standard_library_pkg = sys.modules.setdefault(
    "pcobra.standard_library", types.ModuleType("pcobra.standard_library")
)
setattr(pcobra_pkg, "standard_library", standard_library_pkg)
sys.modules["pcobra.standard_library.decoradores"] = decoradores

memoizar = decoradores.memoizar
dataclase = decoradores.dataclase
temporizar = decoradores.temporizar


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

    def print(self, mensaje: str) -> None:
        self.mensajes.append(mensaje)


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
