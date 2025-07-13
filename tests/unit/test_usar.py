from types import ModuleType
from unittest.mock import patch
import sys

# Evitar dependencias externas durante la importación de los módulos de pruebas
fake_yaml = ModuleType('yaml')
fake_yaml.safe_load = lambda *_args, **_kwargs: {}
sys.modules.setdefault('yaml', fake_yaml)

import pytest

from core.interpreter import InterpretadorCobra
from core.ast_nodes import NodoUsar
from cobra import usar_loader


def test_obtener_modulo_instala_si_no_existe():
    mock_mod = ModuleType('demo')
    usar_loader.USAR_WHITELIST.add('demo')
    with patch.object(usar_loader.importlib, 'import_module', side_effect=[ModuleNotFoundError(), mock_mod]) as mock_import, \
         patch.object(usar_loader.subprocess, 'run') as mock_run:
        mock_run.return_value.returncode = 0
        mod = usar_loader.obtener_modulo('demo')
    usar_loader.USAR_WHITELIST.remove('demo')
    mock_run.assert_called_once_with(['pip', 'install', 'demo'], check=True)
    assert mod is mock_mod


def test_obtener_modulo_desde_corelibs_sin_pip():
    usar_loader.USAR_WHITELIST.add('texto')
    with patch.object(usar_loader.subprocess, 'run') as mock_run:
        mod = usar_loader.obtener_modulo('texto')
    usar_loader.USAR_WHITELIST.remove('texto')
    mock_run.assert_not_called()
    assert mod.mayusculas('hola') == 'HOLA'


def test_obtener_modulo_rechaza_paquete_fuera_de_lista():
    usar_loader.USAR_WHITELIST.clear()
    usar_loader.USAR_WHITELIST.add('ok')
    with pytest.raises(PermissionError):
        usar_loader.obtener_modulo('malo')
    usar_loader.USAR_WHITELIST.clear()


@pytest.mark.timeout(5)
def test_interpreter_usar_registra_modulo(monkeypatch):
    mod = ModuleType('math')
    def fake(name):
        return mod
    monkeypatch.setattr(usar_loader, 'obtener_modulo', fake)
    import sys
    sys.modules['src.cobra.usar_loader'] = usar_loader
    interp = InterpretadorCobra()
    interp.ejecutar_nodo(NodoUsar('math'))
    assert interp.variables['math'] is mod
