import pytest
from io import StringIO
from unittest.mock import patch
import backend  # ensure backend aliases are initialized
from cobra.cli.cli import main
from cobra.cli.commands import modules_cmd


def test_cli_help():
    with patch("sys.stdout", new_callable=StringIO) as out:
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0
    assert "uso" in out.getvalue().lower() or "usage" in out.getvalue().lower()


@pytest.mark.timeout(5)
def test_modulos_instalar_ruta_no_archivo(tmp_path, monkeypatch):
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(mods_dir))
    mod_file = tmp_path / "cobra.mod"
    mod_file.write_text("lock: {}\n")
    monkeypatch.setattr(modules_cmd, "MODULE_MAP_PATH", str(mod_file))
    monkeypatch.setattr(modules_cmd, "LOCK_FILE", str(mod_file))

    ruta = tmp_path / "dir"
    ruta.mkdir()
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "instalar", str(ruta)])
    assert "inv\u00e1lida" in out.getvalue().lower()


@pytest.mark.timeout(5)
def test_modulos_instalar_extension_invalida(tmp_path, monkeypatch):
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(mods_dir))
    mod_file = tmp_path / "cobra.mod"
    mod_file.write_text("lock: {}\n")
    monkeypatch.setattr(modules_cmd, "MODULE_MAP_PATH", str(mod_file))
    monkeypatch.setattr(modules_cmd, "LOCK_FILE", str(mod_file))

    archivo = tmp_path / "m.txt"
    archivo.write_text("x = 1")
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "instalar", str(archivo)])
    assert "inv\u00e1lida" in out.getvalue().lower()


@pytest.mark.timeout(5)
def test_modulos_instalar_enlace_simbolico(tmp_path, monkeypatch):
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(mods_dir))
    mod_file = tmp_path / "cobra.mod"
    mod_file.write_text("lock: {}\n")
    monkeypatch.setattr(modules_cmd, "MODULE_MAP_PATH", str(mod_file))
    monkeypatch.setattr(modules_cmd, "LOCK_FILE", str(mod_file))

    real_file = tmp_path / "m.co"
    real_file.write_text("var x = 1")
    link = tmp_path / "link.co"
    link.symlink_to(real_file)
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "instalar", str(link)])
    assert "inv\u00e1lida" in out.getvalue().lower()
