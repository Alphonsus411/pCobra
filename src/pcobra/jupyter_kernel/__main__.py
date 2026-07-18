"""Punto de entrada para instalar el kernel de Jupyter."""

import argparse

from pcobra.jupyter_kernel import install


def main() -> int:
    """Instala el kernel cuando se solicita mediante el único comando válido."""
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("install",))
    parser.parse_args()
    install()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
