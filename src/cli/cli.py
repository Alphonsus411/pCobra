"""Shim de compatibilidad para ``python -m cli.cli``."""

from __future__ import annotations

import sys
import warnings

from pcobra.cli import build_legacy_cli_shim_main

main = build_legacy_cli_shim_main("cli.cli")

warnings.warn(
    "`python -m cli.cli` es una ruta legacy deprecada y no contractual; use `python -m pcobra.cli`.",
    DeprecationWarning,
    stacklevel=2,
)


if __name__ == "__main__":
    sys.exit(main())
