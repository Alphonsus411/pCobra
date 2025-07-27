import zipfile
from unittest.mock import patch
import pytest

from cli.commands import modules_cmd, package_cmd


@pytest.mark.timeout(5)
def test_instalar_paquete_destino_symlink(tmp_path, monkeypatch):
    # Preparar un paquete con un módulo
    src = tmp_path / "src"
    src.mkdir()
    modulo = src / "m.co"
    modulo.write_text("var x = 1")
    pkg = tmp_path / "demo.cobra"
    with zipfile.ZipFile(pkg, "w") as zf:
        zf.write(modulo, arcname=modulo.name)
    # Destino dentro de MODULES_PATH es un symlink
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(mods_dir))
    monkeypatch.setattr(package_cmd.modules_cmd, "MODULES_PATH", str(mods_dir))
    dest = mods_dir / modulo.name
    dest.symlink_to(modulo)
    with patch("cli.commands.package_cmd.mostrar_error") as err:
        ret = package_cmd.PaqueteCommand._instalar(str(pkg))
    assert ret == 1
    err.assert_called_once()
