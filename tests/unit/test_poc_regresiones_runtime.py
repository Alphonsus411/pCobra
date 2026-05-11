from __future__ import annotations

from pathlib import Path
from types import ModuleType

import pytest

from pcobra.core.ast_nodes import NodoUsar
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core import usar_loader as core_usar_loader


def _interp(alias: dict[str, str]) -> InterpretadorCobra:
    inter = InterpretadorCobra()
    inter.configurar_restriccion_usar_repl(alias)
    return inter


def test_poc_exitos_numero_logica_tiempo_y_llamada_anidada() -> None:
    inter = _interp({"numero": "numero", "logica": "logica", "tiempo": "tiempo"})
    inter.ejecutar_nodo(NodoUsar("numero"))
    inter.ejecutar_nodo(NodoUsar("logica"))
    inter.ejecutar_nodo(NodoUsar("tiempo"))

    inter.contextos[-1].define("doble", lambda x: x * 2)
    assert inter.variables["es_finito"](inter.variables["doble"](21)) is True
    assert inter.variables["signo"](-7) == -1
    assert inter.variables["conjuncion"](True, inter.variables["negacion"](False)) is True
    assert isinstance(inter.variables["epoch"](), (int, float))


def test_poc_texto_api_completa_sin_ciclo(monkeypatch) -> None:
    modulo = ModuleType("texto")
    modulo.__all__ = ["minusculas", "mayusculas", "a_snake"]
    modulo.minusculas = str.lower
    modulo.mayusculas = str.upper
    modulo.a_snake = lambda txt: txt.replace(" ", "_")

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _n: modulo)
    inter = _interp({"texto": "texto"})
    inter.ejecutar_nodo(NodoUsar("texto"))

    assert "minusculas" in inter.variables
    assert "mayusculas" in inter.variables


def test_poc_datos_longitud_disponible(monkeypatch) -> None:
    modulo_datos = ModuleType("datos")
    modulo_datos.__all__ = ["longitud"]
    modulo_datos.longitud = len

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _n: modulo_datos)
    inter = _interp({"datos": "datos"})
    inter.ejecutar_nodo(NodoUsar("datos"))

    assert "longitud" in inter.variables
    assert inter.variables["longitud"]([1, 2, 3]) == 3


def test_poc_archivo_existe_permitido_en_sandbox(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    inter = _interp({"archivo": "archivo"})
    inter.ejecutar_nodo(NodoUsar("archivo"))
    inter.variables["escribir"]("ok.txt", "hola")
    assert inter.variables["existe"]("ok.txt") is True


def test_poc_seguridad_rechaza_numpy_con_error_corto() -> None:
    inter = _interp({"numero": "numero"})
    with pytest.raises(PermissionError) as exc:
        inter.ejecutar_nodo(NodoUsar("numpy"))
    mensaje = str(exc.value).lower()
    assert "numpy" in mensaje
    assert "traceback" not in mensaje


@pytest.mark.parametrize("modulo", ["holobit_sdk", "pcobra.core.interpreter", "os", "json"])
def test_poc_seguridad_bloquea_modulos_backend_sdk_externos(modulo: str) -> None:
    inter = _interp({"numero": "numero"})
    with pytest.raises(PermissionError):
        inter.ejecutar_nodo(NodoUsar(modulo))



def test_poc_minimo_alias_oficiales_y_no_publicos() -> None:
    inter = _interp({"numero": "numero", "texto": "texto", "logica": "logica", "tiempo": "tiempo", "datos": "datos"})
    for modulo in ("numero", "texto", "logica", "tiempo", "datos"):
        inter.ejecutar_nodo(NodoUsar(modulo))

    assert inter.variables["es_finito"](10) is True
    assert inter.variables["signo"](0 - 5) == -1
    assert inter.variables["recortar"](" cobra ") == "cobra"
    assert inter.variables["mayusculas"]("cobra") == "COBRA"
    assert inter.variables["conjuncion"](True, False) is False
    assert isinstance(inter.variables["epoch"](), (int, float))
    assert inter.variables["longitud"]("cobra") == 5

    simbolos = set(inter.contextos[-1].values.keys())
    assert "_backend" not in simbolos
    assert "_impl" not in simbolos
    assert "__all__" not in simbolos

def test_poc_verifica_rutas_lexer_parser_no_modificables() -> None:
    contenido = Path("scripts/ci/gate_no_parser_lexer_changes.py").read_text(encoding="utf-8")
    for ruta in (
        "src/pcobra/core/lexer.py",
        "src/pcobra/core/parser.py",
        "src/pcobra/cobra/core/lexer.py",
        "src/pcobra/cobra/core/parser.py",
    ):
        assert ruta in contenido
