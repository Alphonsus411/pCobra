import pytest
from unittest.mock import patch
from pathlib import Path

import core.rust_bridge as rust_bridge


def test_compilar_crate_sin_cbindgen(tmp_path):
    def fake_which(cmd):
        return None if cmd == "cbindgen" else "/usr/bin/" + cmd
    with patch("shutil.which", side_effect=fake_which), patch("subprocess.run") as run:
        with pytest.raises(RuntimeError):
            rust_bridge.compilar_crate(str(tmp_path))
        run.assert_not_called()


def test_compilar_crate_sin_cargo(tmp_path):
    def fake_which(cmd):
        if cmd == "cbindgen":
            return "/usr/bin/cbindgen"
        return None
    with patch("shutil.which", side_effect=fake_which), patch("subprocess.run") as run:
        with pytest.raises(RuntimeError):
            rust_bridge.compilar_crate(str(tmp_path))
        run.assert_not_called()
