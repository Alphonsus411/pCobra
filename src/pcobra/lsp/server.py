"""Módulo para iniciar un servidor LSP con soporte para Cobra."""

from __future__ import annotations

import sys

try:
    from pylsp.python_lsp import PythonLSPServer, start_io_lang_server
except ModuleNotFoundError as exc:  # pragma: no cover - dependencia opcional
    _PYLSP_ERROR = exc

    class PythonLSPServer:  # type: ignore[no-redef]
        """Implementación mínima usada cuando ``python-lsp-server`` falta."""

        def __init__(self, *_args, **_kwargs) -> None:
            raise ModuleNotFoundError(
                "El paquete opcional 'python-lsp-server' es necesario para el servidor LSP."
            ) from _PYLSP_ERROR

    def _fallback_start_io_lang_server(*_args, **_kwargs):  # pragma: no cover
        raise ModuleNotFoundError(
            "El paquete opcional 'python-lsp-server' es necesario para iniciar el servidor LSP."
        ) from _PYLSP_ERROR

    start_io_lang_server = _fallback_start_io_lang_server  # type: ignore[assignment]
else:
    _PYLSP_ERROR = None
    _fallback_start_io_lang_server = None  # type: ignore[assignment]

from lsp import cobra_plugin


def _obtener_start_callable():
    """Devuelve la función ``start_io_lang_server`` activa."""

    alias_mod = sys.modules.get("lsp.server")
    if alias_mod is not None and hasattr(alias_mod, "start_io_lang_server"):
        return alias_mod.start_io_lang_server  # type: ignore[attr-defined]
    return start_io_lang_server


class CobraLSPServer(PythonLSPServer):
    """Servidor LSP que registra el plugin de completado de Cobra."""

    def __init__(self, rx, tx, check_parent_process=False):
        super().__init__(rx, tx, check_parent_process)
        self.config.plugin_manager.register(cobra_plugin, name="cobra")


def main() -> None:
    """Arranca el servidor de lenguaje con el plugin registrado."""
    start_fn = _obtener_start_callable()
    if _PYLSP_ERROR is not None and start_fn is _fallback_start_io_lang_server:
        import logging

        logging.getLogger(__name__).warning(
            "python-lsp-server no está instalado; el servidor LSP no se iniciará."
        )
        return

    start_fn(sys.stdin.buffer, sys.stdout.buffer, False, CobraLSPServer)


if __name__ == "__main__":
    main()
