from __future__ import annotations
import json
from importlib import import_module
from pathlib import Path
import pytest
from pcobra.contrato_capacidades_corelibs import CAPACIDADES_POR_MODULO

PROHIBIDOS = {"_backend", "_impl", "python", "pandas", "numpy"}
SNAPSHOT = json.loads((Path(__file__).parents[2] / "snapshots" / "public_api_por_modulo.json").read_text(encoding="utf-8"))

@pytest.mark.parametrize("nombre", sorted(CAPACIDADES_POR_MODULO))
def test_presencia_y_all_canonico(nombre: str) -> None:
    c = CAPACIDADES_POR_MODULO[nombre]
    mod = import_module(str(c["modulo"]))
    assert tuple(mod.__all__) == tuple(c["api_canonica"])
    for fn in c["api_canonica"]:
        assert hasattr(mod, fn)

@pytest.mark.parametrize("nombre", sorted(CAPACIDADES_POR_MODULO))
def test_ausencia_simbolos_prohibidos(nombre: str) -> None:
    c = CAPACIDADES_POR_MODULO[nombre]
    mod = import_module(str(c["modulo"]))
    lowered = {s.lower() for s in mod.__all__}
    for p in PROHIBIDOS:
        assert p not in lowered

@pytest.mark.parametrize("nombre", sorted(CAPACIDADES_POR_MODULO))
def test_snapshot_api_publica(nombre: str) -> None:
    mod = import_module(f"pcobra.standard_library.{nombre}")
    assert mod.__all__ == SNAPSHOT[nombre]

def test_errores_invalidos_coherentes() -> None:
    numero = import_module("pcobra.standard_library.numero")
    archivo = import_module("pcobra.standard_library.archivo")
    with pytest.raises(TypeError):
        numero.es_finito("abc")
    with pytest.raises(TypeError):
        archivo.leer(None)
