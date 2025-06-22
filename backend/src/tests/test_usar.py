from types import ModuleType
from unittest.mock import patch

import pytest

from src.core.interpreter import InterpretadorCobra
from src.core.ast_nodes import NodoUsar
from src.cobra import usar_loader


def test_obtener_modulo_instala_si_no_existe():
    mock_mod = ModuleType('demo')
    with patch.object(usar_loader.importlib, 'import_module', side_effect=[ModuleNotFoundError(), mock_mod]) as mock_import, \
         patch.object(usar_loader.subprocess, 'run') as mock_run:
        mock_run.return_value.returncode = 0
        mod = usar_loader.obtener_modulo('demo')
    mock_run.assert_called_once_with(['pip', 'install', 'demo'], check=True)
    assert mod is mock_mod


@pytest.mark.timeout(5)
def test_interpreter_usar_registra_modulo(monkeypatch):
    mod = ModuleType('math')
    monkeypatch.setattr(usar_loader, 'obtener_modulo', lambda name: mod)
    interp = InterpretadorCobra()
    interp.ejecutar_nodo(NodoUsar('math'))
    assert interp.variables['math'] is mod
