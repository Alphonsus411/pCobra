import argparse
import sys
import shutil
from io import StringIO
from pathlib import Path
import subprocess
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
import pcobra  # noqa: F401
from pcobra.cobra.cli.commands.docs_cmd import DocsCommand


def test_docs_generation():
    if (
        not shutil.which("sphinx-build")
        or not shutil.which("sphinx-apidoc")
        or not shutil.which("plantuml")
    ):
        pytest.skip("Sphinx no disponible")

    build_dir = ROOT / "docs" / "build" / "html"
    if build_dir.exists():
        shutil.rmtree(build_dir)

    comando = DocsCommand()
    with patch("sys.stdout", new_callable=StringIO) as out:
        with patch.object(DocsCommand, "_obtener_raiz", return_value=ROOT):
            ret = comando.run(argparse.Namespace())

    assert ret == 0
    assert (build_dir / "index.html").is_file()
    assert "Documentación generada" in out.getvalue()

    linkcheck_dir = ROOT / "docs" / "build" / "linkcheck"
    if linkcheck_dir.exists():
        shutil.rmtree(linkcheck_dir)
    result = subprocess.run(
        ["sphinx-build", "-b", "linkcheck", str(ROOT / "docs" / "frontend"), str(linkcheck_dir)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert result.returncode == 0
    assert "broken" not in result.stdout

    manual = build_dir / "MANUAL_COBRA.html"
    especificacion = build_dir / "especificacion_tecnica.html"
    assert manual.is_file() or especificacion.is_file()

    index_content = (build_dir / "index.html").read_text(encoding="utf-8")
    assert "toctree-wrapper" in index_content or "class=\"toc\"" in index_content
