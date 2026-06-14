from __future__ import annotations

import importlib
import sys
import tomllib
from pathlib import Path
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[2]


def test_entrypoints_publicos_apuntan_al_namespace_pcobra() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = pyproject["project"]["scripts"]

    assert scripts["cobra"] == "pcobra.cli:main"

    source_main = (ROOT / "src" / "pcobra" / "__main__.py").read_text(encoding="utf-8")
    assert "from pcobra.cli import main" in source_main


def test_run_service_declara_solo_namespace_canonico_para_sandbox() -> None:
    source = (ROOT / "src" / "pcobra" / "cobra" / "cli" / "services" / "run_service.py").read_text(
        encoding="utf-8"
    )

    assert "from pcobra.core import sandbox as sandbox_module" in source
    assert 'import_module("core.sandbox")' not in source
