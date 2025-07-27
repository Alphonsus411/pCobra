from types import ModuleType
from unittest.mock import patch
import sys

# Evitar dependencias externas durante la importación de los módulos de pruebas
fake_yaml = ModuleType('yaml')
fake_yaml.safe_load = lambda *_args, **_kwargs: {}
sys.modules.setdefault('yaml', fake_yaml)
fake_jsonschema = ModuleType('jsonschema')
fake_jsonschema.validate = lambda *_args, **_kwargs: None
fake_jsonschema.ValidationError = Exception
sys.modules.setdefault('jsonschema', fake_jsonschema)
ts_mod = ModuleType('tree_sitter_languages')
ts_mod.get_parser = lambda *_args, **_kwargs: None
sys.modules.setdefault('tree_sitter_languages', ts_mod)

import pytest

from core.interpreter import InterpretadorCobra
from core.ast_nodes import NodoUsar
from cobra import usar_loader


def test_obtener_modulo_instala_si_no_existe(monkeypatch):
    mock_mod = ModuleType('demo')
    usar_loader.USAR_WHITELIST.add('demo')
    monkeypatch.setenv('COBRA_USAR_INSTALL', '1')
    with patch.object(usar_loader.importlib, 'import_module', side_effect=[ModuleNotFoundError(), mock_mod]) as mock_import, \
         patch.object(usar_loader.subprocess, 'run') as mock_run:
        mock_run.return_value.returncode = 0
        mod = usar_loader.obtener_modulo('demo')
    usar_loader.USAR_WHITELIST.remove('demo')
    mock_run.assert_called_once_with([sys.executable, '-m', 'pip', 'install', 'demo'], check=True)
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


def test_obtener_modulo_instalacion_deshabilitada(monkeypatch):
    usar_loader.USAR_WHITELIST.add('demo')
    monkeypatch.delenv('COBRA_USAR_INSTALL', raising=False)
    with patch.object(usar_loader.importlib, 'import_module', side_effect=ModuleNotFoundError()):
        with patch.object(usar_loader.subprocess, 'run') as mock_run:
            with pytest.raises(RuntimeError):
                usar_loader.obtener_modulo('demo')
            mock_run.assert_not_called()
    usar_loader.USAR_WHITELIST.remove('demo')


@pytest.mark.timeout(5)
def test_interpreter_usar_registra_modulo(monkeypatch):
    mod = ModuleType('math')
    def fake(name):
        return mod
    monkeypatch.setattr(usar_loader, 'obtener_modulo', fake)
    import sys
    sys.modules['cobra.usar_loader'] = usar_loader
    interp = InterpretadorCobra()
    interp.ejecutar_nodo(NodoUsar('math'))
    assert interp.variables['math'] is mod
