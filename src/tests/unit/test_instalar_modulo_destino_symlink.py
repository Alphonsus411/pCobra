import yaml
from unittest.mock import patch
import pytest

from cli.commands import modules_cmd


@pytest.mark.timeout(5)
def test_instalar_modulo_destino_symlink(tmp_path, monkeypatch):
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(mods_dir))
    mod_file = tmp_path / "cobra.mod"
    mod_file.write_text("lock: {}\n")
    monkeypatch.setattr(modules_cmd, "MODULE_MAP_PATH", str(mod_file))
    monkeypatch.setattr(modules_cmd, "LOCK_FILE", str(mod_file))

    modulo = tmp_path / "m.co"
    modulo.write_text("var x = 1")

    dest = mods_dir / modulo.name
    dest.symlink_to(modulo)

    with patch("cli.commands.modules_cmd.mostrar_error") as err:
        ret = modules_cmd.ModulesCommand._instalar_modulo(str(modulo))
    assert ret == 1
    err.assert_called_once()
