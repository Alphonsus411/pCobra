import os
from unittest.mock import patch
from src.cli.cli import main


def test_cli_docs_invokes_sphinx():
    with patch("subprocess.run") as mock_run:
        main(["docs"])
        raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        source = os.path.join(raiz, "source")
        build = os.path.join(raiz, "build", "html")
        mock_run.assert_called_with(["sphinx-build", "-b", "html", source, build], check=True)

