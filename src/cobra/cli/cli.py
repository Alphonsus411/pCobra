"""Shim canónico de compatibilidad para ``python -m cobra.cli.cli``.

Este archivo es la implementación de referencia del wrapper legacy
``cobra.cli.cli``. La variante en ``cobra/cli/cli.py`` actúa como proxy mínimo.
"""

from __future__ import annotations

import sys

from pcobra.cli import build_legacy_cli_shim_main

main = build_legacy_cli_shim_main("cobra.cli.cli")


if __name__ == "__main__":
    sys.exit(main())
