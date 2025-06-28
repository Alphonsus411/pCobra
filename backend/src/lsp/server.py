"""Módulo para iniciar un servidor LSP mínimo."""

import sys
from pylsp import lsp
from pylsp.python_lsp import start_io_lang_server


def main() -> None:
    """Arranca el servidor de lenguaje utilizando la implementación por defecto"""
    start_io_lang_server(lsp, sys.stdin.buffer, sys.stdout.buffer)


if __name__ == "__main__":
    main()
