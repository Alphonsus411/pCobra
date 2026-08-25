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


def test_configuracion_global_preserva_identidad_de_submodulos_legacy() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    probe = repo_root / "test_pytest_alias_identity_probe.py"
    probe.write_text(
        "import importlib\n\n"
        "def test_aliases_lazy_reutilizan_modulos_canonicos():\n"
        "    legacy_plugin = importlib.import_module('cobra.cli.plugin')\n"
        "    canonical_plugin = importlib.import_module('pcobra.cobra.cli.plugin')\n"
        "    legacy_interpreter = importlib.import_module('core.interpreter')\n"
        "    canonical_interpreter = importlib.import_module('pcobra.core.interpreter')\n"
        "    assert legacy_plugin is canonical_plugin\n"
        "    assert legacy_plugin.PluginCommand is canonical_plugin.PluginCommand\n"
        "    assert legacy_interpreter is canonical_interpreter\n"
        "    assert legacy_interpreter.InterpretadorCobra is canonical_interpreter.InterpretadorCobra\n",
        encoding="utf-8",
    )

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", str(probe)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        probe.unlink(missing_ok=True)

    assert result.returncode == 0, result.stdout + result.stderr
