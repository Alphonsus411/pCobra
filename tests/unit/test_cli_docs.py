import argparse
import builtins
from io import StringIO
from pathlib import Path
from unittest.mock import call, patch

from pcobra.cobra.cli.commands import docs_cmd
from pcobra.cobra.cli.commands.docs_cmd import DocsCommand


def test_cli_docs_invokes_sphinx():
    raiz = Path(__file__).resolve().parents[2]
    source = raiz / "docs" / "frontend"
    build = raiz / "docs" / "build" / "html"
    api = source / "api"
    codigo = raiz / "src"

    with patch.object(docs_cmd.subprocess, "run") as mock_run:
        with patch.object(DocsCommand, "_obtener_raiz", return_value=raiz):
            DocsCommand().run(argparse.Namespace())
        mock_run.assert_has_calls([
            call([
                "sphinx-apidoc",
                "-o",
                str(api),
                str(codigo),
            ], check=True, capture_output=True, text=True, timeout=DocsCommand.SPHINX_TIMEOUT),
            call([
                "sphinx-build",
                "-b",
                "html",
                str(source),
                str(build),
            ], check=True, capture_output=True, text=True, timeout=DocsCommand.SPHINX_TIMEOUT),
        ])


def test_cli_docs_sin_sphinx():
    real_import = builtins.__import__

    def _fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "sphinx":
            raise ImportError
        return real_import(name, globals, locals, fromlist, level)

    with patch("builtins.__import__", side_effect=_fake_import), \
            patch("sys.stdout", new_callable=StringIO) as out:
        DocsCommand().run(argparse.Namespace())
    assert "No se encontró Sphinx" in out.getvalue()


