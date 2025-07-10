import sys
import shutil
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import backend  # noqa: F401
from src.cli.cli import main


def test_docs_generation():
    if not shutil.which("sphinx-build") or not shutil.which("sphinx-apidoc"):
        pytest.skip("Sphinx no disponible")

    build_dir = Path("frontend/build/html")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    with patch("sys.stdout", new_callable=StringIO) as out:
        ret = main(["docs"])

    assert ret == 0
    assert (build_dir / "index.html").is_file()
    assert "Documentación generada" in out.getvalue()
