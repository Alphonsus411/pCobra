from pathlib import Path
from io import StringIO
from unittest.mock import patch

from pcobra.cobra.cli import cli as cli_module
from pcobra.cobra.cli.commands.empaquetar_cmd import EmpaquetarCommand


def _cli_context():
    return (
        patch.object(cli_module, "resolve_command_profile", return_value="development"),
        patch.object(cli_module.AppConfig, "BASE_COMMAND_CLASSES", [EmpaquetarCommand]),
    )


def test_cli_empaquetar_invoca_pyinstaller(tmp_path):
    profile, commands = _cli_context()
    with profile, commands, patch("subprocess.run") as mock_run:
        cli_module.main(["empaquetar", f"--output={tmp_path}", "--name", "cobra"])
        raiz = Path(__file__).resolve().parents[2]
        cli_path = raiz / "src" / "cli" / "cli.py"
        mock_run.assert_called_once_with(
            [
                "pyinstaller",
                "--onefile",
                "-n",
                "cobra",
                str(cli_path),
                "--distpath",
                str(tmp_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )


def test_cli_empaquetar_sin_pyinstaller(tmp_path):
    profile, commands = _cli_context()
    with profile, commands, patch("subprocess.run", side_effect=FileNotFoundError), \
            patch("sys.stdout", new_callable=StringIO) as out:
        cli_module.main(["empaquetar", f"--output={tmp_path}", "--name", "cobra"])
    assert "No se encontró PyInstaller" in out.getvalue()


def test_cli_empaquetar_con_spec(tmp_path):
    spec = tmp_path / "cobra.spec"
    spec.touch()
    profile, commands = _cli_context()
    with profile, commands, patch("subprocess.run") as mock_run:
        cli_module.main(["empaquetar", f"--output={tmp_path}", "--spec", str(spec)])
        mock_run.assert_called_once_with(
            [
                "pyinstaller",
                str(spec),
                "--distpath",
                str(tmp_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )


def test_cli_empaquetar_con_datos(tmp_path):
    foo = tmp_path / "foo"
    spam = tmp_path / "spam"
    foo.touch()
    spam.touch()
    profile, commands = _cli_context()
    with profile, commands, patch("subprocess.run") as mock_run:
        cli_module.main([
            "empaquetar",
            f"--output={tmp_path}",
            "--add-data",
            f"{foo};bar",
            "--add-data",
            f"{spam};eggs",
        ])
        raiz = Path(__file__).resolve().parents[2]
        cli_path = raiz / "src" / "cli" / "cli.py"
        mock_run.assert_called_once_with(
            [
                "pyinstaller",
                "--onefile",
                "-n",
                "cobra",
                str(cli_path),
                "--add-data",
                f"{foo};bar",
                "--add-data",
                f"{spam};eggs",
                "--distpath",
                str(tmp_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
