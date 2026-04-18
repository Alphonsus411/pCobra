#!/usr/bin/env python3
"""Verifica que docs/MANUAL_COBRA.rst coincida con su generación automática."""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    subprocess.run(("python", "scripts/generar_manual_ref.py"), check=True)
    result = subprocess.run(
        ("git", "diff", "--quiet", "--", "docs/MANUAL_COBRA.rst"),
        check=False,
    )
    if result.returncode != 0:
        print(
            "[manual-ref] ERROR: docs/MANUAL_COBRA.rst fue editado manualmente "
            "o quedó desincronizado con docs/MANUAL_COBRA.md."
        )
        subprocess.run(
            ("git", "--no-pager", "diff", "--", "docs/MANUAL_COBRA.rst"),
            check=False,
        )
        print("[manual-ref] Ejecuta: python scripts/generar_manual_ref.py")
        return 1

    print("[manual-ref] OK: docs/MANUAL_COBRA.rst está sincronizado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
