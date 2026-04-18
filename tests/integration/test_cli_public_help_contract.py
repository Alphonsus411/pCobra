import os
import subprocess
import sys
from pathlib import Path

from pcobra.cobra.cli.public_command_policy import PUBLIC_COMMANDS


def _public_env() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("SQLITE_DB_KEY", None)
    env.pop("COBRA_DEV_MODE", None)
    env.pop("COBRA_CLI_COMMAND_PROFILE", None)
    env.pop("COBRA_INTERNAL_ENABLE_LEGACY_CLI", None)
    env.pop("COBRA_INTERNAL_LEGACY_TARGETS", None)
    return env


def test_cli_public_commands_contract_is_stable():
    assert PUBLIC_COMMANDS == ("run", "build", "test", "mod")


def test_cli_help_public_contract_snapshot():
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "--help"],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
        env=_public_env(),
    )
    assert result.returncode == 0

    expected_snapshot = (
        Path(__file__).parent / "golden" / "cli_ui_v2_help_public.golden"
    ).read_text(encoding="utf-8")
    assert " ".join(result.stdout.lower().split()) == " ".join(expected_snapshot.split())
    for command in ("run", "build", "test", "mod"):
        assert f" {command} " in f" {result.stdout.lower()} "
    assert "\n  menu " not in result.stdout.lower()
    assert "\n  legacy " not in result.stdout.lower()
    assert "--backend" not in result.stdout.lower()
    assert "--tipo" not in result.stdout.lower()
    assert "--tipos" not in result.stdout.lower()


def test_cli_build_help_public_contract_no_expone_flags_backend():
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "build", "--help"],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
        env=_public_env(),
    )
    assert result.returncode == 0
    output = result.stdout.lower()
    assert "--backend" not in output
    assert "--tipo" not in output
    assert "--tipos" not in output


def test_cli_help_public_contract_bloquea_ui_v1_en_perfil_publico():
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "--ui", "v1", "--help"],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
        env=_public_env(),
    )
    assert result.returncode == 0
    lower_output = result.stderr.lower() + result.stdout.lower()
    assert "cli v1 está reservada para desarrollo interno" in lower_output
    assert "migración automática a ui v2 pública" in lower_output


def test_cli_help_public_contract_bloquea_flags_legacy_en_arranque():
    repo_root = Path(__file__).resolve().parents[2]
    env = _public_env()
    env["COBRA_INTERNAL_ENABLE_LEGACY_CLI"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "--help"],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
        env=env,
    )
    assert result.returncode == 1
    lower_error = result.stderr.lower() + result.stdout.lower()
    assert "internal migration only" in lower_error
    assert "cobra_internal_enable_legacy_cli=1" in lower_error


def test_cli_help_public_contract_muestra_warning_migracion_en_comando_legacy():
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "compilar", "--help"],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
        env=_public_env(),
    )
    assert result.returncode == 0
    lower_output = result.stderr.lower() + result.stdout.lower()
    assert "comando legacy 'compilar'" in lower_output
    assert "migración automática aplicada: use 'build'" in lower_output
    assert "sugerencia: cobra build <archivo.co>" in lower_output
