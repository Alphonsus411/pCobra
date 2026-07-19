from pathlib import Path
from unittest.mock import patch
import io
import tempfile
from pcobra.cobra.cli.commands import dependencias_cmd

DependenciasCommand = dependencias_cmd.DependenciasCommand


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

    venv_path = tmp_path / ".venv"
    pip_path = venv_path / ("Scripts" if dependencias_cmd.sys.platform == "win32" else "bin") / ("pip.exe" if dependencias_cmd.sys.platform == "win32" else "pip")
    pip_path.parent.mkdir(parents=True)
    pip_path.touch()

    with patch.object(DependenciasCommand, "_ruta_requirements", return_value=req_file) as mock_req, \
         patch.object(DependenciasCommand, "_ruta_pyproject", return_value=py_file) as mock_proj, \
         patch.object(DependenciasCommand, "_crear_entorno_virtual", return_value=str(venv_path)), \
         patch("tempfile.NamedTemporaryFile", side_effect=fake_tmp) as mock_tmp, \
         patch.object(dependencias_cmd.subprocess, "run") as mock_run:
        DependenciasCommand._instalar_dependencias()
        tmp_path_generated = created[0].name
        mock_run.assert_called_once_with(
            [str(pip_path), "install", "-r", tmp_path_generated],
            check=True,
            capture_output=True,
            text=True,
        )
        assert mock_req.called
        assert mock_proj.called


def test_cli_dependencias_listar_muestra_paquetes(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("paqueteA==1.0\n")
    py_file = tmp_path / "pyproject.toml"
    py_file.write_text("[project]\ndependencies=['paqueteB==2.0']\n")

    with patch.object(DependenciasCommand, "_ruta_requirements", return_value=req_file) as mock_req, \
         patch.object(DependenciasCommand, "_ruta_pyproject", return_value=py_file) as mock_proj, \
         patch("sys.stdout", new_callable=io.StringIO) as out:
        DependenciasCommand._listar_dependencias()
        salida = out.getvalue().strip().splitlines()
        salida = [s.replace("\x1b[92m", "").replace("\x1b[0m", "") for s in salida]
        assert sorted(salida) == ["paqueteA==1.0", "paqueteB==2.0"]
        assert mock_req.called
        assert mock_proj.called
