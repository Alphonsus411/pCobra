"""Wrapper ligero para exponer ``pcobra.cobra.cli.cli`` bajo ``cobra.cli``."""

from typing import Iterable, Optional

from pcobra.cobra.cli.cli import main as _main

__all__ = ["main"]


def main(argv: Optional[Iterable[str]] = None) -> int:
    """Ejecuta la entrada principal de la CLI heredada."""

    return _main(list(argv) if argv is not None else None)


if __name__ == "__main__":  # pragma: no cover - compatibilidad CLI
    main()
