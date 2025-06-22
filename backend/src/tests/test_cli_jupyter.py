from unittest.mock import patch, call
import sys
from src.cli.cli import main


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
