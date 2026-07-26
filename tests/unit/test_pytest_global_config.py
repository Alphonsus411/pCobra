from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def test_configuracion_global_no_importa_shim_core() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    probe = repo_root / "test_pytest_global_config_probe.py"
    probe.write_text(
        "import sys\n\n"
        "def test_core_no_se_importa_durante_inicializacion():\n"
        "    assert 'core' not in sys.modules\n",
        encoding="utf-8",
    )

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-W",
                "error::DeprecationWarning",
                str(probe),
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        probe.unlink(missing_ok=True)

    assert result.returncode == 0, result.stdout + result.stderr
