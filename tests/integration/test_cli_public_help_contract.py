import argparse
import os
import re
import subprocess
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import cobra.cli.cli as cli_module
import pcobra.cli as public_cli
from pcobra.cobra.cli.public_command_policy import PUBLIC_COMMANDS


def _leer_snapshot_texto(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        return data.decode("utf-16")
    return data.decode("utf-8")


def _public_env() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("SQLITE_DB_KEY", None)
    env.pop("COBRA_DEV_MODE", None)
    env.pop("COBRA_CLI_COMMAND_PROFILE", None)
    env.pop("COBRA_INTERNAL_ENABLE_LEGACY_CLI", None)
    env.pop("COBRA_INTERNAL_LEGACY_TARGETS", None)
    return env


def _comandos_en_ayuda_temprana(output: str) -> tuple[str, ...]:
    bloque = output.split("Lenguaje Cobra CLI. Comandos públicos:\n", 1)[1]
    bloque = bloque.split("\n\nOpciones:\n", 1)[0]
    return tuple(linea.split()[0] for linea in bloque.splitlines())


def _comandos_en_linea_de_uso(output: str) -> tuple[str, ...]:
    coincidencias = re.findall(r"\{([a-z]+(?:,\s*[a-z]+)+)\}", output)
    comandos = next(grupo for grupo in coincidencias if "run" in grupo.split(","))
    return tuple(comando.strip() for comando in comandos.split(","))


def test_cli_early_global_help_exposes_exact_public_commands():
    with patch("sys.stdout", new_callable=StringIO) as output:
        assert public_cli.main(["--help"]) == 0

    ayuda = output.getvalue()
    assert _comandos_en_ayuda_temprana(ayuda) == PUBLIC_COMMANDS
    assert _comandos_en_linea_de_uso(ayuda) == PUBLIC_COMMANDS


def test_cobra_entrypoint_early_help_exposes_exact_public_commands():
    repo_root = Path(__file__).resolve().parents[2]
    env = _public_env()
    env["PATH"] = f"{repo_root / 'scripts' / 'bin'}{os.pathsep}{env.get('PATH', '')}"

    for help_flag in ("--help", "-h"):
        result = subprocess.run(
            ["cobra", help_flag],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(repo_root),
            env=env,
        )
        assert result.returncode == 0
        assert _comandos_en_linea_de_uso(result.stdout) == PUBLIC_COMMANDS


def test_cli_public_commands_contract_is_stable():
    assert PUBLIC_COMMANDS == ("run", "build", "test", "mod", "repl", "gui")


def test_cli_public_commands_contract_keeps_repl_as_official_command():
    # `repl` debe permanecer en el contrato público oficial (no alias legacy).
    assert "repl" in PUBLIC_COMMANDS


def test_cli_ui_v2_registra_repl_oficial_y_no_alias_interactive_legacy():
    registry = cli_module.CommandRegistry()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    commands = registry.register_base_commands(
        subparsers,
        ui="v2",
        profile="public",
    )

    assert "repl" in commands
    assert commands["repl"].__class__.__name__ == "ReplCommandV2"
    assert "interactive" not in commands


def test_cli_public_profile_does_not_register_extended_choices(monkeypatch):
    monkeypatch.delenv("COBRA_DEV_MODE", raising=False)
    monkeypatch.delenv("COBRA_CLI_COMMAND_PROFILE", raising=False)

    app = cli_module.CliApplication()
    app.initialize()
    app._ensure_command_structure()

    commands = set(app.command_registry.commands)
    choices = app._subparsers.choices
    visible_help_choices = {
        action.dest
        for action in app._subparsers._choices_actions
        if action.help is not argparse.SUPPRESS
    }

    assert commands == set(PUBLIC_COMMANDS)
    assert set(choices) == set(PUBLIC_COMMANDS)
    assert "paquete" in choices
    assert "hub" in choices
    assert "installer" not in choices
    assert visible_help_choices == set(PUBLIC_COMMANDS)
    assert "paquete" not in visible_help_choices
    assert "hub" not in visible_help_choices
    for command in ("installer", "paquete", "hub"):
        assert command not in commands


def test_cli_help_public_contract_snapshot():
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(repo_root),
        env=_public_env(),
    )
    assert result.returncode == 0

    expected_snapshot = (
        Path(__file__).parent / "golden" / "cli_ui_v2_help_public.golden"
    )
    expected_snapshot = _leer_snapshot_texto(expected_snapshot)
    assert " ".join(result.stdout.lower().split()) == " ".join(
        expected_snapshot.lower().split()
    )
    for command in ("run", "build", "test", "mod", "repl", "gui"):
        assert f" {command} " in f" {result.stdout.lower()} "
    for command in ("installer", "paquete", "hub"):
        assert f" {command} " not in f" {result.stdout.lower()} "
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
        encoding="utf-8",
        cwd=str(repo_root),
        env=_public_env(),
    )
    assert result.returncode == 0
    output = result.stdout.lower()
    assert "--backend" not in output
    assert "--tipo" not in output
    assert "--tipos" not in output


def test_cli_public_invalid_extended_commands_do_not_appear_as_choices():
    repo_root = Path(__file__).resolve().parents[2]
    for invalid_command in ("installer", "compilar"):
        result = subprocess.run(
            [sys.executable, "-m", "cobra.cli.cli", invalid_command, "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(repo_root),
            env=_public_env(),
        )
        assert result.returncode != 0
        lower_output = result.stderr.lower() + result.stdout.lower()
        assert f"invalid choice: '{invalid_command}'" in lower_output
        match = re.search(r"choose from ([^)]+)\)", lower_output)
        assert match is not None
        choices_message = match.group(1)
        for command in PUBLIC_COMMANDS:
            assert command in choices_message
        for command in ("installer", "compilar", "paquete", "hub"):
            assert command not in choices_message


def test_cli_public_hidden_compat_commands_are_callable_but_not_main_help():
    repo_root = Path(__file__).resolve().parents[2]
    for legacy_command in ("paquete", "hub"):
        result = subprocess.run(
            [sys.executable, "-m", "cobra.cli.cli", legacy_command, "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(repo_root),
            env=_public_env(),
        )
        assert result.returncode == 0
        lower_output = result.stderr.lower() + result.stdout.lower()
        assert "invalid choice" not in lower_output
        assert "choose from" not in lower_output
        assert f"usage: cobra {legacy_command}" in result.stdout.lower()


def test_cli_help_public_contract_muestra_warning_migracion_en_comando_legacy():
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "compilar", "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(repo_root),
        env=_public_env(),
    )
    assert result.returncode != 0
    lower_output = result.stderr.lower() + result.stdout.lower()
    assert "invalid choice: 'compilar'" in lower_output
    choices_message = lower_output.split("invalid choice: 'compilar'", 1)[1]
    for command in ("run", "build", "test", "mod", "repl", "gui"):
        assert command in choices_message
    for command in ("installer", "paquete", "hub"):
        assert command not in choices_message
