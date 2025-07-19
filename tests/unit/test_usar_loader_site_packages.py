import importlib
import types
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]


def test_obtener_modulo_en_site_packages(tmp_path, monkeypatch):
    site = tmp_path / "site-packages"
    cobra_dir = site / "cobra"
    corelibs_dir = site / "corelibs"
    stdlib_dir = site / "standard_library"
    cobra_dir.mkdir(parents=True)
    corelibs_dir.mkdir()
    stdlib_dir.mkdir()

    # Copiar archivos necesarios
    (cobra_dir / "__init__.py").write_text("")
    usar_loader_src = ROOT / "backend" / "src" / "cobra" / "usar_loader.py"
    (cobra_dir / "usar_loader.py").write_text(usar_loader_src.read_text())

    (corelibs_dir / "__init__.py").write_text("")
    texto_src = ROOT / "backend" / "corelibs" / "texto.py"
    (corelibs_dir / "texto.py").write_text(texto_src.read_text())

    (stdlib_dir / "__init__.py").write_text("")
    fecha_src = ROOT / "standard_library" / "fecha.py"
    (stdlib_dir / "fecha.py").write_text(fecha_src.read_text())

    monkeypatch.syspath_prepend(str(site))
    for key in list(sys.modules):
        if key == "cobra" or key.startswith("cobra."):
            del sys.modules[key]

    usar_loader = importlib.import_module("cobra.usar_loader")

    usar_loader.USAR_WHITELIST.update({"texto", "fecha"})
    try:
        mod_texto = usar_loader.obtener_modulo("texto")
        mod_fecha = usar_loader.obtener_modulo("fecha")
    finally:
        usar_loader.USAR_WHITELIST.clear()

    assert isinstance(mod_texto, types.ModuleType)
    assert mod_texto.mayusculas("hola") == "HOLA"
    assert isinstance(mod_fecha, types.ModuleType)
    assert mod_fecha.formatear(datetime(2020, 1, 1)) == "2020-01-01"
