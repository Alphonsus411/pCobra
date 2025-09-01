from unittest.mock import patch, call
import sys
from argparse import Namespace

from cobra.cli.commands.jupyter_cmd import JupyterCommand


def test_cli_jupyter_installs_kernel():
    cmd = JupyterCommand()
    with patch.dict("sys.modules", {"jupyter": object()}), patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        cmd.run(Namespace(notebook=None))
        mock_run.assert_has_calls([
            call([sys.executable, "-m", "cobra.jupyter_kernel", "install"], check=True, capture_output=True, text=True),
            call([
                "jupyter",
                "notebook",
                "--KernelManager.default_kernel_name=cobra",
            ], check=True),
        ])


def test_cli_jupyter_opens_specific_notebook(tmp_path):
    nb = tmp_path / "demo.ipynb"
    nb.write_text("\n")
    cmd = JupyterCommand()
    with patch.dict("sys.modules", {"jupyter": object()}), patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        cmd.run(Namespace(notebook=nb))
        mock_run.assert_has_calls([
            call([sys.executable, "-m", "cobra.jupyter_kernel", "install"], check=True, capture_output=True, text=True),
            call([
                "jupyter",
                "notebook",
                "--KernelManager.default_kernel_name=cobra",
                str(nb),
            ], check=True),
        ])
