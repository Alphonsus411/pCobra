import sys
from pathlib import Path
from io import BytesIO
import types
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Evita dependencias pesadas al importar el módulo
dummy_plugin = types.ModuleType("cobra_plugin")
sys.modules.setdefault("lsp.cobra_plugin", dummy_plugin)

from lsp import server


def test_main_invoca_start_io_lang_server():
    """main() debe llamar a start_io_lang_server con CobraLSPServer."""
    with patch("lsp.server.start_io_lang_server") as mock_start:
        server.main()
        mock_start.assert_called_once_with(
            sys.stdin.buffer, sys.stdout.buffer, False, server.CobraLSPServer
        )


def test_plugin_registrado_en_instancia():
    """Al crear CobraLSPServer se registra el plugin 'cobra'."""

    def fake_init(self, rx, tx, check_parent_process=False):
        self.config = types.SimpleNamespace(plugin_manager=Mock())

    with patch.object(server.PythonLSPServer, "__init__", fake_init):
        srv = server.CobraLSPServer(BytesIO(), BytesIO())

    srv.config.plugin_manager.register.assert_called_once_with(
        server.cobra_plugin, name="cobra"
    )
