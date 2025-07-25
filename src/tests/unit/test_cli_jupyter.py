from unittest.mock import patch, call
import sys
from cli.cli import main


def test_cli_jupyter_installs_kernel():
    with patch("subprocess.run") as mock_run:
        main(["jupyter"])
        mock_run.assert_has_calls([
            call([sys.executable, "-m", "cobra.jupyter_kernel", "install"], check=True),
            call([
                "jupyter",
                "notebook",
                "--KernelManager.default_kernel_name=cobra",
            ], check=True),
        ])


def test_cli_jupyter_opens_specific_notebook():
    with patch("subprocess.run") as mock_run:
        main(["jupyter", "--notebook=demo.ipynb"])
        mock_run.assert_has_calls([
            call([sys.executable, "-m", "cobra.jupyter_kernel", "install"], check=True),
            call([
                "jupyter",
                "notebook",
                "--KernelManager.default_kernel_name=cobra",
                "demo.ipynb",
            ], check=True),
        ])
