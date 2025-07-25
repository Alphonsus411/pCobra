import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_pyinstaller_script(tmp_path):
    if not shutil.which("pyinstaller"):
        pytest.skip("pyinstaller no disponible")

    script = ROOT / "scripts" / "test_pyinstaller.sh"
    out_dir = tmp_path / "dist"
    env = os.environ.copy()
    env["OUTPUT_DIR"] = str(out_dir)
    result = subprocess.run(["bash", str(script)], cwd=ROOT, env=env)
    assert result.returncode == 0
    assert any(out_dir.iterdir())

