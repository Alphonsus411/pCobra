from pathlib import Path
from unittest.mock import patch, call
from src.cli.cli import main


def test_cli_docs_invokes_sphinx():
    with patch("subprocess.run") as mock_run:
        main(["docs"])
        raiz = Path(__file__).resolve().parents[3]
        source = raiz / "frontend" / "docs"
        build = raiz / "frontend" / "build" / "html"
        api = raiz / "frontend" / "docs" / "api"
        codigo = raiz / "backend" / "src"
        mock_run.assert_has_calls([
            call([
                "sphinx-apidoc",
                "-o",
                str(api),
                str(codigo),
            ], check=True),
            call([
                "sphinx-build",
                "-b",
                "html",
                str(source),
                str(build),
            ], check=True),
        ])

