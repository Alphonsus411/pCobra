"""Módulo para iniciar un servidor LSP con soporte para Cobra."""

from __future__ import annotations

import sys
from pylsp.python_lsp import PythonLSPServer, start_io_lang_server

from lsp import cobra_plugin


class CobraLSPServer(PythonLSPServer):
    """Servidor LSP que registra el plugin de completado de Cobra."""

    def __init__(self, rx, tx, check_parent_process=False):
        super().__init__(rx, tx, check_parent_process)
        self.config.plugin_manager.register(cobra_plugin, name="cobra")


def main() -> None:
    """Arranca el servidor de lenguaje con el plugin registrado."""
    start_io_lang_server(sys.stdin.buffer, sys.stdout.buffer, False, CobraLSPServer)


if __name__ == "__main__":
    main()
