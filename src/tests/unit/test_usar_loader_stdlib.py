import types
from datetime import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend" / "src"))
sys.path.insert(0, str(ROOT))

from cobra import usar_loader
import standard_library.fecha as fecha


def test_obtener_modulo_standard_library(monkeypatch):
    usar_loader.USAR_WHITELIST.add("fecha")
    mod = usar_loader.obtener_modulo("fecha")
    usar_loader.USAR_WHITELIST.remove("fecha")
    assert isinstance(mod, types.ModuleType)
    assert hasattr(mod, "formatear")
    assert mod.formatear(datetime(2020, 1, 1)) == fecha.formatear(datetime(2020, 1, 1))

