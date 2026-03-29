"""Proxy mínimo hacia el shim canónico de ``src/cobra/cli/cli.py``."""

from __future__ import annotations

import sys

from pcobra.cli import build_legacy_cli_shim_main

main = build_legacy_cli_shim_main("cobra.cli.cli")


if __name__ == "__main__":
    sys.exit(main())
