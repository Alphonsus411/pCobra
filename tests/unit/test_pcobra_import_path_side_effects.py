from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_import_pcobra_no_modifica_path() -> None:
    env = os.environ.copy()
    env["PATH"] = "/tmp/pcobra-path-a:/tmp/pcobra-path-b"
    env.pop("PCOBRA_CLI_BOOTSTRAP_PATH", None)

    script = (
        "import os; "
        "before = os.environ.get('PATH'); "
        "import pcobra; "
        "after = os.environ.get('PATH'); "
        "print(before); "
        "print(after); "
        "raise SystemExit(0 if before == after else 1)"
    )

    proceso = subprocess.run(  # nosec B603
        [sys.executable, "-c", script],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert proceso.returncode == 0, proceso.stderr


def test_import_pcobra_cli_es_liviano_y_sin_side_effects() -> None:
    env = os.environ.copy()
    env["PATH"] = "/tmp/pcobra-cli-a:/tmp/pcobra-cli-b"
    env.pop("PCOBRA_CLI_BOOTSTRAP_PATH", None)

    script = (
        "import os, sys; "
        "before = os.environ.get('PATH'); "
        "import pcobra.cli as pc_cli; "
        "after = os.environ.get('PATH'); "
        "lazy_loaded = 'pcobra.cli.cli' in sys.modules; "
        "print(getattr(pc_cli, '__name__', '')); "
        "print(before); "
        "print(after); "
        "print(lazy_loaded); "
        "raise SystemExit(0 if before == after and not lazy_loaded else 1)"
    )

    proceso = subprocess.run(  # nosec B603
        [sys.executable, "-c", script],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert proceso.returncode == 0, proceso.stderr


def test_import_pcobra_es_liviano_sin_dependencias_opcionales() -> None:
    env = os.environ.copy()
    env.pop("PCOBRA_ENABLE_LEGACY_IMPORTS", None)

    script = (
        "import sys; "
        "import pcobra; "
        "tiene_gui = 'pcobra.gui' in sys.modules; "
        "tiene_flet = 'flet' in sys.modules; "
        "print(tiene_gui); "
        "print(tiene_flet); "
        "raise SystemExit(0 if not tiene_gui and not tiene_flet else 1)"
    )

    proceso = subprocess.run(  # nosec B603
        [sys.executable, "-c", script],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert proceso.returncode == 0, proceso.stderr


def test_pcobra_lazy_load_submodulos_publicos() -> None:
    env = os.environ.copy()

    script = (
        "import sys; "
        "import pcobra; "
        "antes = 'pcobra.core' in sys.modules; "
        "_core = pcobra.core; "
        "despues = 'pcobra.core' in sys.modules; "
        "print(antes); "
        "print(despues); "
        "raise SystemExit(0 if (not antes and despues and _core.__name__ == 'pcobra.core') else 1)"
    )

    proceso = subprocess.run(  # nosec B603
        [sys.executable, "-c", script],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert proceso.returncode == 0, proceso.stderr
