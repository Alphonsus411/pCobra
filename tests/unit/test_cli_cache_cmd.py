import importlib
import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch
import argparse

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def test_cli_cache_limpiar(monkeypatch, tmp_path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    (cache_dir / "x.ast").write_text("dato")
    monkeypatch.setenv("COBRA_AST_CACHE", str(cache_dir))
    backend_src = PROJECT_ROOT / "backend" / "src"
    for path in (PROJECT_ROOT, backend_src):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    import backend  # ensure path hooks are set

    from src.cli.commands.cache_cmd import CacheCommand

    with patch("sys.stdout", new_callable=StringIO) as out:
        CacheCommand().run(argparse.Namespace())
    assert list(cache_dir.glob("*.ast")) == []
