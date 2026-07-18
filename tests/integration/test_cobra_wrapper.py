from __future__ import annotations

import json
import os
import subprocess
import sys
import venv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WRAPPER = REPO_ROOT / "scripts" / "bin" / "cobra"


def test_wrapper_ejecuta_entry_point_instalado_sin_importar_checkout(
    tmp_path: Path,
) -> None:
    entorno = tmp_path / "entorno"
    venv.EnvBuilder(with_pip=False).create(entorno)
    python = entorno / "bin" / "python3"

    purelib = subprocess.run(
        [str(python), "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    site_packages = Path(purelib)
    (site_packages / "entry_point_aislado.py").write_text(
        "import json, os, sys\n"
        "def main():\n"
        "    with open(os.environ['COBRA_MARKER'], 'w') as marker:\n"
        "        json.dump({'executable': sys.executable, 'path': sys.path}, marker)\n"
        "    return 37\n",
        encoding="utf-8",
    )
    dist_info = site_packages / "pcobra-0.0.dist-info"
    dist_info.mkdir()
    (dist_info / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: pcobra\nVersion: 0.0\n",
        encoding="utf-8",
    )
    (dist_info / "entry_points.txt").write_text(
        "[console_scripts]\ncobra = entry_point_aislado:main\n",
        encoding="utf-8",
    )

    marker = tmp_path / "entry-point.json"
    env = {
        "COBRA_MARKER": str(marker),
        "HOME": str(tmp_path),
        # El directorio del wrapper primero reproduce el caso propenso a recursión.
        "PATH": os.pathsep.join((str(WRAPPER.parent), str(entorno / "bin"))),
    }
    result = subprocess.run(
        [str(WRAPPER)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 37, result.stderr
    payload = json.loads(marker.read_text(encoding="utf-8"))
    assert Path(payload["executable"]).parent == entorno / "bin"
    assert str(REPO_ROOT) not in payload["path"]
    assert str(REPO_ROOT / "src") not in payload["path"]
