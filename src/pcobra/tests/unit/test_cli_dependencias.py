from pathlib import Path
from unittest.mock import patch
import io
import tempfile
from cobra.cli.commands.dependencias_cmd import DependenciasCommand


def test_cli_dependencias_instalar_invoca_pip(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("paqueteA==1.0\n")
    py_file = tmp_path / "pyproject.toml"
    py_file.write_text("[project]\ndependencies=['paqueteB==2.0']\n")

    created = []

    real_ntf = tempfile.NamedTemporaryFile

    def fake_tmp(*a, **k):
        f = real_ntf(*a, **k)
        created.append(f)
        return f

    with patch("cli.commands.dependencias_cmd.DependenciasCommand._ruta_requirements", return_value=str(req_file)) as mock_req, \
         patch("cli.commands.dependencias_cmd.DependenciasCommand._ruta_pyproject", return_value=str(py_file)) as mock_proj, \
         patch("tempfile.NamedTemporaryFile", side_effect=fake_tmp) as mock_tmp, \
         patch("subprocess.run") as mock_run:
        DependenciasCommand._instalar_dependencias()
        tmp_path_generated = created[0].name
        mock_run.assert_called_once_with(["pip", "install", "-r", tmp_path_generated], check=True)
        assert mock_req.called
        assert mock_proj.called


def test_cli_dependencias_listar_muestra_paquetes(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("paqueteA==1.0\n")
    py_file = tmp_path / "pyproject.toml"
    py_file.write_text("[project]\ndependencies=['paqueteB==2.0']\n")

    with patch("cli.commands.dependencias_cmd.DependenciasCommand._ruta_requirements", return_value=str(req_file)) as mock_req, \
         patch("cli.commands.dependencias_cmd.DependenciasCommand._ruta_pyproject", return_value=str(py_file)) as mock_proj, \
         patch("sys.stdout", new_callable=io.StringIO) as out:
        DependenciasCommand._listar_dependencias()
        salida = out.getvalue().strip().splitlines()
        salida = [s.replace("\x1b[92m", "").replace("\x1b[0m", "") for s in salida]
        assert sorted(salida) == ["paqueteA==1.0", "paqueteB==2.0"]
        assert mock_req.called
        assert mock_proj.called
