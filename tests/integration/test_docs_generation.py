import sys
import shutil
from io import StringIO
from pathlib import Path
import subprocess
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend" / "src"))
import backend  # noqa: F401
from cobra.cli.cli import main


def test_docs_generation():
    if not shutil.which("sphinx-build") or not shutil.which("sphinx-apidoc"):
        pytest.skip("Sphinx no disponible")

    build_dir = Path("docs/build/html")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    with patch("sys.stdout", new_callable=StringIO) as out:
        ret = main(["docs"])

    assert ret == 0
    assert (build_dir / "index.html").is_file()
    assert "Documentación generada" in out.getvalue()

    linkcheck_dir = Path("docs/build/linkcheck")
    if linkcheck_dir.exists():
        shutil.rmtree(linkcheck_dir)
    result = subprocess.run(
        ["sphinx-build", "-b", "linkcheck", "docs/frontend", str(linkcheck_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "broken" not in result.stdout

    manual = build_dir / "MANUAL_COBRA.html"
    especificacion = build_dir / "especificacion_tecnica.html"
    assert manual.is_file() or especificacion.is_file()

    index_content = (build_dir / "index.html").read_text(encoding="utf-8")
    assert "toctree-wrapper" in index_content or "class=\"toc\"" in index_content
