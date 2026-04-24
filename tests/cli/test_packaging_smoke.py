from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("build")


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.integration
def test_packaging_smoke_build_install_and_run_help(tmp_path: Path) -> None:
    """Valida artefactos de packaging y `pcobra.cli:main(['--help'])` en entorno limpio."""

    dist_dir = tmp_path / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    build_result = subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--sdist", "--outdir", str(dist_dir)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert build_result.returncode == 0, (
        "No se pudo construir wheel/sdist para el smoke test de packaging. "
        f"stdout={build_result.stdout!r} stderr={build_result.stderr!r}"
    )

    wheels = sorted(dist_dir.glob("*.whl"))
    sdists = sorted(dist_dir.glob("*.tar.gz"))
    assert wheels, "No se generó wheel durante el smoke test de packaging."
    assert sdists, "No se generó sdist durante el smoke test de packaging."

    venv_dir = tmp_path / "venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_dir)],
        check=True,
        capture_output=True,
        text=True,
    )

    if os.name == "nt":
        venv_python = venv_dir / "Scripts" / "python.exe"
        venv_pip = venv_dir / "Scripts" / "pip.exe"
    else:
        venv_python = venv_dir / "bin" / "python"
        venv_pip = venv_dir / "bin" / "pip"

    subprocess.run(
        [str(venv_pip), "install", "--no-deps", "--force-reinstall", str(wheels[0])],
        check=True,
        capture_output=True,
        text=True,
    )

    smoke_script = (
        "import pcobra\n"
        "import pcobra.cli\n"
        "from pcobra.cli import main\n"
        "import sys\n"
        "antes = set(sys.modules)\n"
        "code = main(['--help'])\n"
        "despues = set(sys.modules)\n"
        "if code != 0:\n"
        "    raise SystemExit(f'pcobra.cli.main([\\'--help\\']) devolvió {code}')\n"
        "prohibidos = {'cobra', 'core', 'bindings'}\n"
        "cargados = sorted(name for name in (despues - antes) if name in prohibidos)\n"
        "if cargados:\n"
        "    raise SystemExit(f'Se cargaron paquetes raíz legacy en smoke limpio: {cargados!r}')\n"
    )
    run_help = subprocess.run(
        [str(venv_python), "-I", "-c", smoke_script],
        check=False,
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    assert run_help.returncode == 0, (
        "El smoke test aislado de packaging debe validar `import pcobra; import pcobra.cli` y ejecutar --help sin depender de paquetes raíz. "
        f"stdout={run_help.stdout!r} stderr={run_help.stderr!r}"
    )
