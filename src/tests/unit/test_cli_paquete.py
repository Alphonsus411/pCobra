from io import StringIO
import zipfile
import tomllib
from unittest.mock import patch

from cli.cli import main
from cli.commands import modules_cmd, package_cmd


def test_paquete_crear_instalar(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    modulo = src / "m.co"
    modulo.write_text("var x = 1")
    pkg = tmp_path / "demo.cobra"

    with patch("sys.stdout", new_callable=StringIO):
        main(["paquete", "crear", str(src), str(pkg), "--nombre=demo", "--version=0.1"])

    assert pkg.exists()
    with zipfile.ZipFile(pkg) as zf:
        data = tomllib.loads(zf.read("cobra.pkg").decode("utf-8"))
    assert data["paquete"]["nombre"] == "demo"
    mods_dir = tmp_path / "mods"
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(mods_dir))

    with patch("sys.stdout", new_callable=StringIO):
        main(["paquete", "instalar", str(pkg)])

    assert (mods_dir / "m.co").exists()
