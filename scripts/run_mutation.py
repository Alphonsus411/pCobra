#!/usr/bin/env python3
"""Ejecuta pruebas de mutación con MutPy sobre ``src``."""
from __future__ import annotations
import importlib
import os
import sys
from pathlib import Path
from typing import Optional

def _ensure_py312_compat() -> None:
    """
    Define importlib.find_loader para MutPy en Python 3.12.
    
    Raises:
        ImportError: Si no se puede configurar la compatibilidad
    """
    if not hasattr(importlib, "find_loader"):
        try:
            from importlib.machinery import PathFinder
            def find_loader(name: str, path: Optional[list[str]] = None):
                spec = PathFinder.find_spec(name, path)
                return spec.loader if spec else None
            importlib.find_loader = find_loader  # type: ignore[attr-defined]
        except ImportError as e:
            raise ImportError("No se pudo configurar la compatibilidad con Python 3.12") from e

def main() -> None:
    try:
        _ensure_py312_compat()
        
        repo = Path(__file__).resolve().parents[1]
        src_path = repo / "src"
        
        if not src_path.exists():
            raise FileNotFoundError(f"No se encontró el directorio src: {src_path}")
        
        # Preservar PYTHONPATH existente
        original_pythonpath = os.environ.get("PYTHONPATH", "")
        os.environ["PYTHONPATH"] = f"{src_path}{os.pathsep}{original_pythonpath}"
        
        sys.path.insert(0, str(src_path))
        
        args = [
            "--target", "src",
            "--unit-test", "tests.unit",
            "--runner", "pytest",
            "--percentage", "5",
            "--path", str(src_path),
        ]
        
        original_argv = sys.argv[:]
        try:
            sys.argv = ["mut.py"] + args
            import mutpy.commandline as commandline
            commandline.main(sys.argv)
        finally:
            sys.argv = original_argv
            
    except Exception as e:
        print(f"Error durante la ejecución de las pruebas de mutación: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()