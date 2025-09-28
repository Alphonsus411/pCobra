import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from cobra.cli.commands import modules_cmd, package_cmd


def _crear_paquete(dest: Path, archivos: dict[str, str]) -> Path:
    with zipfile.ZipFile(dest, "w") as zf:
        for nombre, contenido in archivos.items():
            zf.writestr(nombre, contenido)
    return dest


@pytest.mark.timeout(5)
def test_instalar_paquete_correcto(tmp_path, monkeypatch):
    pkg = _crear_paquete(tmp_path / "demo.cobra", {"modulo.co": "var x = 1"})
    mods_dir = tmp_path / "mods"
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(mods_dir))
    monkeypatch.setattr(package_cmd.modules_cmd, "MODULES_PATH", str(mods_dir))

    ret = package_cmd.PaqueteCommand._instalar(pkg)

    assert ret == 0
    assert (mods_dir / "modulo.co").read_text() == "var x = 1"


@pytest.mark.timeout(5)
def test_instalar_paquete_destino_symlink(tmp_path, monkeypatch):
    pkg = _crear_paquete(tmp_path / "demo.cobra", {"m.co": "var x = 1"})
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(mods_dir))
    monkeypatch.setattr(package_cmd.modules_cmd, "MODULES_PATH", str(mods_dir))
    dest = mods_dir / "m.co"
    dest.symlink_to(tmp_path / "fuente.co")

    with patch("cobra.cli.commands.package_cmd.mostrar_error") as err:
        ret = package_cmd.PaqueteCommand._instalar(pkg)

    assert ret == 1
    err.assert_called_once()


@pytest.mark.timeout(5)
def test_instalar_paquete_con_ruta_maliciosa(tmp_path, monkeypatch):
    pkg = _crear_paquete(tmp_path / "demo.cobra", {"../malo.co": "pwn"})
    mods_dir = tmp_path / "mods"
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(mods_dir))
    monkeypatch.setattr(package_cmd.modules_cmd, "MODULES_PATH", str(mods_dir))

    with patch("cobra.cli.commands.package_cmd.mostrar_error") as err:
        ret = package_cmd.PaqueteCommand._instalar(pkg)

    assert ret == 1
    err.assert_called_once()
    assert not any(mods_dir.rglob("malo.co"))
