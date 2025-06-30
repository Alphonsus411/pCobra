from pathlib import Path
from unittest.mock import patch
from src.cli.cli import main


def test_cli_dependencias_instalar_invoca_pip():
    with patch("subprocess.run") as mock_run:
        main(["dependencias", "instalar"])
        req = Path(__file__).resolve().parents[3] / "requirements.txt"
        mock_run.assert_called_once_with(["pip", "install", "-r", str(req)], check=True)


def test_cli_dependencias_listar_muestra_paquetes(tmp_path, monkeypatch):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("paqueteA==1.0\npaqueteB==2.0\n")
    monkeypatch.setattr(
        "src.cli.commands.dependencias_cmd.DependenciasCommand._ruta_requirements",
        lambda: str(req_file),
    )

    with patch("sys.stdout", new_callable=lambda: __import__("io").StringIO()) as out:
        main(["dependencias", "listar"])
    salida = out.getvalue().strip().splitlines()
    assert salida == ["paqueteA==1.0", "paqueteB==2.0"]
