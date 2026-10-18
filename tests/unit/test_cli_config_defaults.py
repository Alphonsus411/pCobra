"""Contratos de configuración predeterminada de la CLI canónica."""

import subprocess
import sys
import textwrap


def _ejecutar_aislado(codigo: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(codigo)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def test_cli_starts_with_defaults_when_config_absent():
    resultado = _ejecutar_aislado("""
        from unittest.mock import patch

        with patch(
            "pcobra.cobra.cli.utils.config.load_config",
            return_value={},
        ):
            from pcobra.cobra.cli.cli import AppConfig

        assert AppConfig.config_data == {}
        assert AppConfig.DEFAULT_LANGUAGE == "es"
        assert AppConfig.DEFAULT_COMMAND == "run"
        assert AppConfig.PROGRAM_NAME == "cobra"
    """)

    assert resultado.returncode == 0, resultado.stdout + resultado.stderr


def test_cli_uses_defaults_when_config_load_fails():
    resultado = _ejecutar_aislado("""
        from unittest.mock import patch

        with patch(
            "pcobra.cobra.cli.utils.config.load_config",
            side_effect=RuntimeError("boom"),
        ):
            from pcobra.cobra.cli.cli import AppConfig

        assert AppConfig.config_data == {}
        assert AppConfig.DEFAULT_LANGUAGE == "es"
        assert AppConfig.DEFAULT_COMMAND == "run"
    """)

    assert resultado.returncode == 0, resultado.stdout + resultado.stderr
    assert "Failed to load configuration: boom" in resultado.stderr
