#!/usr/bin/env python3
"""Ejecuta pruebas de mutación con MutPy sobre backend/src."""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path


def _ensure_py312_compat() -> None:
    """Define importlib.find_loader para MutPy en Python 3.12."""
    if not hasattr(importlib, "find_loader"):
        from importlib.machinery import PathFinder

        def find_loader(name: str, path: list[str] | None = None):
            spec = PathFinder.find_spec(name, path)
            return spec.loader if spec else None

        importlib.find_loader = find_loader  # type: ignore[attr-defined]


def main() -> None:
    _ensure_py312_compat()
    repo = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo))
    sys.path.insert(0, str(repo / "backend" / "src"))
    os.environ["PYTHONPATH"] = f"{repo}:{repo / 'backend' / 'src'}"

    args = [
        "--target",
        "src",
        "--unit-test",
        "tests.unit",
        "--runner",
        "pytest",
        "--percentage",
        "5",
        "--path",
        str(repo / "backend" / "src"),
    ]
    sys.argv = ["mut.py"] + args
    import mutpy.commandline as commandline

    commandline.main(sys.argv)


if __name__ == "__main__":
    main()
