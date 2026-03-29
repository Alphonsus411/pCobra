"""Shim de compatibilidad para ``python -m cli.cli``."""

from __future__ import annotations

import sys

from pcobra.cli import build_legacy_cli_shim_main

main = build_legacy_cli_shim_main("cli.cli")


if __name__ == "__main__":
    sys.exit(main())
