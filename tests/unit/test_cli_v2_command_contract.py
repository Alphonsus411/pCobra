import argparse

import pytest

from cobra.cli.commands_v2.run_cmd import RunCommandV2
from cobra.cli.commands_v2.build_cmd import BuildCommandV2
from cobra.cli.commands_v2.test_cmd import TestCommandV2
from cobra.cli.commands_v2.legacy_cmd import LegacyCommandGroupV2
from cobra.cli.cli import LEGACY_COMMAND_MIGRATION_MAP
from cobra.cli.target_policies import VERIFICATION_EXECUTABLE_TARGETS


def _build_subparsers() -> argparse._SubParsersAction:
    parser = argparse.ArgumentParser()
    return parser.add_subparsers(dest="command")


def test_run_v2_container_acepta_solo_targets_oficiales_runtime():
    subparsers = _build_subparsers()
    command = RunCommandV2()
    command.register_subparser(subparsers)

    parser = subparsers.choices[command.name]
    parsed = parser.parse_args(["programa.co", "--container", "rust"])
    assert parsed.container == "rust"

    with pytest.raises(SystemExit):
        parser.parse_args(["programa.co", "--container", "cpp"])


def test_test_v2_langs_es_opcional_y_usa_default_de_politica_oficial():
    subparsers = _build_subparsers()
    command = TestCommandV2()
    command.register_subparser(subparsers)

    parser = subparsers.choices[command.name]
    parsed = parser.parse_args(["programa.co"])

    assert parsed.langs == list(VERIFICATION_EXECUTABLE_TARGETS)


def test_build_v2_resuelve_backend_via_pipeline(monkeypatch):
    command = BuildCommandV2()
    called = {}

    monkeypatch.setattr(
        "cobra.cli.commands_v2.build_cmd.backend_pipeline.build",
        lambda file, hints: called.setdefault(
            "build",
            {
                "backend": "python",
                "reason": None,
                "runtime": {"language": "python"},
                "ast": [],
                "code": "print('ok')",
            },
        ),
    )
    monkeypatch.setattr(
        command._runtime_manager,
        "validate_command_runtime",
        lambda language, **kwargs: called.setdefault("runtime", (language, kwargs))
        or ("1.0", object(), object()),
    )

    status = command.run(
        argparse.Namespace(file="programa.co", modo="mixto", debug=False)
    )
    assert status == 0
    assert "build" in called
    assert called["runtime"][0] == "python"
    assert called["runtime"][1]["command"] == "build"


def test_build_v2_ux_salida_estable_sin_terminos_internos(monkeypatch):
    command = BuildCommandV2()
    messages: list[str] = []

    monkeypatch.setattr(
        "cobra.cli.commands_v2.build_cmd.backend_pipeline.build",
        lambda *_args, **_kwargs: {
            "backend": "python",
            "reason": "[backend_resolution] backend=python; reason=contract",
            "runtime": {"language": "python"},
            "ast": [],
            "code": "print('ok')",
            "artifact_path": "/tmp/programa.py",
        },
    )
    monkeypatch.setattr(
        command._runtime_manager,
        "validate_command_runtime",
        lambda *_args, **_kwargs: ("1.0", object(), object()),
    )
    monkeypatch.setattr(
        "cobra.cli.commands_v2.build_cmd.mostrar_info",
        lambda message, **_kwargs: messages.append(message),
    )

    status = command.run(
        argparse.Namespace(file="programa.co", modo="mixto", debug=False)
    )

    assert status == 0
    assert "Artefacto Cobra generado." in messages
    assert "Ruta de artefacto: /tmp/programa.py" in messages
    assert all("backend_resolution" not in message for message in messages)
    assert all("Transpilador" not in message for message in messages)


def test_build_v2_muestra_reason_solo_en_debug(monkeypatch):
    command = BuildCommandV2()
    messages: list[str] = []

    monkeypatch.setattr(
        "cobra.cli.commands_v2.build_cmd.backend_pipeline.build",
        lambda *_args, **_kwargs: {
            "backend": "python",
            "reason": "[backend_resolution] backend=python; reason=contract",
            "runtime": {"language": "python"},
            "ast": [],
            "code": "print('ok')",
        },
    )
    monkeypatch.setattr(
        command._runtime_manager,
        "validate_command_runtime",
        lambda *_args, **_kwargs: ("1.0", object(), object()),
    )
    monkeypatch.setattr(
        "cobra.cli.commands_v2.build_cmd.mostrar_info",
        lambda message, **_kwargs: messages.append(message),
    )

    status = command.run(
        argparse.Namespace(file="programa.co", modo="mixto", debug=True)
    )

    assert status == 0
    assert any("Resolución de backend (debug):" in message for message in messages)


def test_build_v2_help_no_expone_flags_backend():
    subparsers = _build_subparsers()
    command = BuildCommandV2()
    command.register_subparser(subparsers)
    parser = subparsers.choices[command.name]
    help_text = parser.format_help().lower()

    assert "--tipo" not in help_text
    assert "--backend" not in help_text
    assert "--tipos" not in help_text


def test_run_v2_valida_seguridad_por_ruta_binding(monkeypatch):
    command = RunCommandV2()
    called = {}

    monkeypatch.setattr(
        command._runtime_manager,
        "validate_command_runtime",
        lambda language, **kwargs: called.setdefault("runtime", (language, kwargs))
        or ("1.0", object(), object()),
    )
    monkeypatch.setattr(
        "cobra.cli.commands_v2.run_cmd.backend_pipeline.resolve_backend",
        lambda _file, _hints: type("R", (), {"reason_for": lambda self, debug: "ok"})(),
    )
    monkeypatch.setattr(command._legacy, "run", lambda _args: 0)

    status = command.run(
        argparse.Namespace(file="programa.co", debug=False, sandbox=False, container="rust", modo="mixto")
    )

    assert status == 0
    assert called["runtime"][0] == "rust"
    assert called["runtime"][1]["containerized"] is True
    assert called["runtime"][1]["command"] == "run"


def test_test_v2_valida_seguridad_por_ruta_binding(monkeypatch):
    command = TestCommandV2()
    calls: list[tuple[str, dict]] = []

    monkeypatch.setattr(
        command._runtime_manager,
        "validate_command_runtime",
        lambda language, **kwargs: calls.append((language, kwargs)) or ("1.0", object(), object()),
    )
    monkeypatch.setattr(
        "cobra.cli.commands_v2.test_cmd.backend_pipeline.resolve_backend",
        lambda _file, _hints: type("R", (), {"reason_for": lambda self, debug: "ok"})(),
    )
    monkeypatch.setattr(command._legacy, "run", lambda _args: 0)

    status = command.run(
        argparse.Namespace(file="programa.co", debug=False, langs=["python", "javascript", "rust"], modo="mixto")
    )

    assert status == 0
    assert calls[0][0] == "python" and calls[0][1]["sandbox"] is True
    assert calls[1][0] == "javascript" and calls[1][1]["containerized"] is True
    assert calls[2][0] == "rust" and calls[2][1]["containerized"] is True


def test_legacy_command_migration_map_cubre_comandos_legacy_principales():
    assert set(LEGACY_COMMAND_MIGRATION_MAP) == {"ejecutar", "compilar", "verificar", "modulos"}
    assert LEGACY_COMMAND_MIGRATION_MAP["ejecutar"]["target"] == "run"
    assert LEGACY_COMMAND_MIGRATION_MAP["compilar"]["target"] == "build"
    assert LEGACY_COMMAND_MIGRATION_MAP["verificar"]["target"] == "test"
    assert LEGACY_COMMAND_MIGRATION_MAP["modulos"]["target"] == "mod"
    assert LEGACY_COMMAND_MIGRATION_MAP["modulos"]["hint"].startswith("cobra mod ")


def test_legacy_group_muestra_mensaje_corto_de_migracion(monkeypatch):
    command = LegacyCommandGroupV2()
    warnings: list[str] = []
    monkeypatch.setattr("cobra.cli.commands_v2.legacy_cmd.messages.mostrar_advertencia", warnings.append)
    monkeypatch.setattr(command._execute, "run", lambda _args: 0)

    status = command.run(argparse.Namespace(legacy_command="ejecutar", archivo="app.co"))

    assert status == 0
    assert warnings
    assert "cobra run <archivo.co>" in warnings[0]
