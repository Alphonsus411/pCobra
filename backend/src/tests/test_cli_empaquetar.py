from pathlib import Path
from io import StringIO
from unittest.mock import patch, call

from src.cli.cli import main


def test_cli_empaquetar_invoca_pyinstaller(tmp_path):
    with patch("subprocess.run") as mock_run:
        main(["empaquetar", f"--output={tmp_path}"])
        raiz = Path(__file__).resolve().parents[3]
        cli_path = raiz / "backend" / "src" / "cli" / "cli.py"
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
        main(["empaquetar", f"--output={tmp_path}"])
    assert "PyInstaller no está instalado" in out.getvalue()
