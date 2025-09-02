from pathlib import Path
from io import StringIO
from unittest.mock import patch

from cobra.cli.cli import main


def test_cli_empaquetar_invoca_pyinstaller(tmp_path):
    with patch("subprocess.run") as mock_run:
        main(["empaquetar", f"--output={tmp_path}", "--name", "cobra"])
        raiz = Path(__file__).resolve().parents[3]
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
        )


def test_cli_empaquetar_sin_pyinstaller(tmp_path):
    with patch("subprocess.run", side_effect=FileNotFoundError), \
            patch("sys.stdout", new_callable=StringIO) as out:
        main(["empaquetar", f"--output={tmp_path}", "--name", "cobra"])
    assert "PyInstaller no está instalado" in out.getvalue()


def test_cli_empaquetar_con_spec(tmp_path):
    with patch("subprocess.run") as mock_run:
        main(["empaquetar", f"--output={tmp_path}", "--spec", "cobra.spec"])
        mock_run.assert_called_once_with(
            [
                "pyinstaller",
                "cobra.spec",
                "--distpath",
                str(tmp_path),
            ],
            check=True,
        )


def test_cli_empaquetar_con_datos(tmp_path):
    with patch("subprocess.run") as mock_run:
        main([
            "empaquetar",
            f"--output={tmp_path}",
            "--add-data",
            "foo;bar",
            "--add-data",
            "spam;eggs",
        ])
        raiz = Path(__file__).resolve().parents[3]
        cli_path = raiz / "src" / "cli" / "cli.py"
        mock_run.assert_called_once_with(
            [
                "pyinstaller",
                "--onefile",
                "-n",
                "cobra",
                str(cli_path),
                "--add-data",
                "foo;bar",
                "--add-data",
                "spam;eggs",
                "--distpath",
                str(tmp_path),
            ],
            check=True,
        )
