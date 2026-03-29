from unittest.mock import call, patch
import sys
from argparse import Namespace
import subprocess

from cobra.cli.commands.jupyter_cmd import JupyterCommand


def test_cli_jupyter_installs_kernel():
    cmd = JupyterCommand()
    with (
        patch.dict("sys.modules", {"jupyter": object()}),
        patch("subprocess.run") as mock_run,
        patch.object(JupyterCommand, "_resolver_ejecutable", return_value="/usr/bin/python3"),
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        cmd.run(Namespace(notebook=None))
        mock_run.assert_has_calls([
            call([sys.executable, "-m", "pcobra.jupyter_kernel", "install"], check=True, capture_output=True, text=True),
            call([
                "/usr/bin/python3",
                "-m",
                "jupyter",
                "notebook",
                "--KernelManager.default_kernel_name=cobra",
            ], check=True),
        ])


def test_cli_jupyter_opens_specific_notebook(tmp_path):
    nb = tmp_path / "demo.ipynb"
    nb.write_text("\n")
    cmd = JupyterCommand()
    with (
        patch.dict("sys.modules", {"jupyter": object()}),
        patch("subprocess.run") as mock_run,
        patch.object(JupyterCommand, "_resolver_ejecutable", return_value="/usr/bin/python3"),
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        cmd.run(Namespace(notebook=nb))
        mock_run.assert_has_calls([
            call([sys.executable, "-m", "pcobra.jupyter_kernel", "install"], check=True, capture_output=True, text=True),
            call([
                "/usr/bin/python3",
                "-m",
                "jupyter",
                "notebook",
                "--KernelManager.default_kernel_name=cobra",
                str(nb),
            ], check=True),
        ])


def test_cli_jupyter_uses_canonical_kernel_module_only():
    cmd = JupyterCommand()
    with (
        patch.dict("sys.modules", {"jupyter": object()}),
        patch("subprocess.run") as mock_run,
        patch.object(JupyterCommand, "_resolver_ejecutable", return_value="/usr/bin/python3"),
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""

        cmd.run(Namespace(notebook=None))

        first_call_args = mock_run.call_args_list[0].args[0]
        second_call_args = mock_run.call_args_list[1].args[0]
        assert first_call_args == [sys.executable, "-m", "pcobra.jupyter_kernel", "install"]
        assert "cobra.jupyter_kernel" not in first_call_args
        assert second_call_args[0] != "jupyter"


def test_cli_jupyter_no_usa_literal_jupyter_como_primer_argumento():
    cmd = JupyterCommand()
    with (
        patch.dict("sys.modules", {"jupyter": object()}),
        patch.object(JupyterCommand, "_resolver_ejecutable", return_value="/opt/python/bin/python3"),
        patch("subprocess.run") as mock_run,
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""

        cmd.run(Namespace(notebook=None))

        comando_jupyter = mock_run.call_args_list[1].args[0]
        assert comando_jupyter == [
            "/opt/python/bin/python3",
            "-m",
            "jupyter",
            "notebook",
            "--KernelManager.default_kernel_name=cobra",
        ]
        assert comando_jupyter[0] != "jupyter"


def test_cli_jupyter_error_modulo_no_instalado():
    cmd = JupyterCommand()
    original_import = __import__

    def import_fallido(name, *args, **kwargs):
        if name == "jupyter":
            raise ImportError
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=import_fallido), patch(
        "cobra.cli.commands.jupyter_cmd.mostrar_error"
    ) as mock_mostrar_error:
        code = cmd.run(Namespace(notebook=None))

    assert code == 1
    mock_mostrar_error.assert_called_once()


def test_cli_jupyter_error_ejecutable_no_encontrado():
    cmd = JupyterCommand()
    with (
        patch.dict("sys.modules", {"jupyter": object()}),
        patch.object(
            JupyterCommand,
            "_resolver_ejecutable",
            side_effect=JupyterCommand.EjecutableNoEncontradoError("python"),
        ),
        patch("subprocess.run") as mock_run,
        patch("cobra.cli.commands.jupyter_cmd.mostrar_error") as mock_mostrar_error,
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        code = cmd.run(Namespace(notebook=None))

    assert code == 1
    mock_mostrar_error.assert_called_once()


def test_cli_jupyter_error_subproceso():
    cmd = JupyterCommand()
    with (
        patch.dict("sys.modules", {"jupyter": object()}),
        patch("subprocess.run") as mock_run,
        patch("cobra.cli.commands.jupyter_cmd.mostrar_error") as mock_mostrar_error,
    ):
        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd="boom")
        code = cmd.run(Namespace(notebook=None))

    assert code == 1
    mock_mostrar_error.assert_called_once()


def test_cli_jupyter_notebook_inexistente_retorna_error_claro():
    cmd = JupyterCommand()
    with (
        patch.dict("sys.modules", {"jupyter": object()}),
        patch("subprocess.run") as mock_run,
        patch("cobra.cli.commands.jupyter_cmd.mostrar_error") as mock_mostrar_error,
    ):
        code = cmd.run(Namespace(notebook="no_existe.ipynb"))

    assert code == 1
    mock_run.assert_not_called()
    mock_mostrar_error.assert_called_once()
    mensaje = mock_mostrar_error.call_args.args[0]
    assert "No se encontró el notebook indicado" in mensaje
    assert "Traceback" not in mensaje
