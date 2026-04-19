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
    monkeypatch.setitem(usar_loader.USAR_WHITELIST, 'demo', 'demo')
    monkeypatch.setenv('COBRA_USAR_INSTALL', '1')
    with patch.object(usar_loader.importlib, 'import_module', side_effect=[ModuleNotFoundError(), mock_mod]) as mock_import, \
         patch.object(usar_loader.subprocess, 'run') as mock_run:
        mock_run.return_value.returncode = 0
        mod = usar_loader.obtener_modulo('demo')
    mock_run.assert_called_once_with([sys.executable, '-m', 'pip', 'install', 'demo'], check=True)
    assert mod is mock_mod


def test_obtener_modulo_desde_corelibs_sin_pip():
    usar_loader.USAR_WHITELIST['texto'] = 'texto'
    with patch.object(usar_loader.subprocess, 'run') as mock_run:
        mod = usar_loader.obtener_modulo('texto')
    del usar_loader.USAR_WHITELIST['texto']
    mock_run.assert_not_called()
    assert mod.mayusculas('hola') == 'HOLA'


def test_obtener_modulo_rechaza_paquete_fuera_de_lista():
    original = usar_loader.USAR_WHITELIST.copy()
    try:
        usar_loader.USAR_WHITELIST.clear()
        usar_loader.USAR_WHITELIST['ok'] = 'ok'
        with pytest.raises(PermissionError):
            usar_loader.obtener_modulo('malo')
    finally:
        usar_loader.USAR_WHITELIST.clear()
        usar_loader.USAR_WHITELIST.update(original)


def test_obtener_modulo_instalacion_deshabilitada(monkeypatch):
    monkeypatch.setitem(usar_loader.USAR_WHITELIST, 'demo', 'demo')
    monkeypatch.delenv('COBRA_USAR_INSTALL', raising=False)
    with patch.object(usar_loader.importlib, 'import_module', side_effect=ModuleNotFoundError()):
        with patch.object(usar_loader.subprocess, 'run') as mock_run:
            with pytest.raises(RuntimeError):
                usar_loader.obtener_modulo('demo')
            mock_run.assert_not_called()


def test_obtener_modulo_instala_spec_estricto(monkeypatch):
    mock_mod = ModuleType('demo')
    spec = 'demo==1.0.0'
    monkeypatch.setitem(usar_loader.USAR_WHITELIST, 'demo', spec)
    monkeypatch.setenv('COBRA_USAR_INSTALL', '1')
    with patch.object(usar_loader.importlib, 'import_module', side_effect=[ModuleNotFoundError(), mock_mod]), \
         patch.object(usar_loader.subprocess, 'run') as mock_run:
        mock_run.return_value.returncode = 0
        mod = usar_loader.obtener_modulo('demo')
    mock_run.assert_called_once_with(
        [sys.executable, '-m', 'pip', 'install', 'demo==1.0.0'],
        check=True,
    )
    assert mod is mock_mod


def test_obtener_modulo_modo_inseguro_permite_flags(monkeypatch):
    mock_mod = ModuleType('demo')
    spec = 'demo==1.0 --hash=sha256:abc123'
    monkeypatch.setitem(usar_loader.USAR_WHITELIST, 'demo', spec)
    monkeypatch.setenv('COBRA_USAR_INSTALL', '1')
    monkeypatch.setenv('COBRA_USAR_INSTALL_UNSAFE_SPECS', '1')
    with patch.object(usar_loader.importlib, 'import_module', side_effect=[ModuleNotFoundError(), mock_mod]), \
         patch.object(usar_loader.subprocess, 'run') as mock_run:
        mock_run.return_value.returncode = 0
        mod = usar_loader.obtener_modulo('demo')
    mock_run.assert_called_once_with(
        [
            sys.executable,
            '-m',
            'pip',
            'install',
            'demo==1.0',
            '--hash=sha256:abc123',
        ],
        check=True,
    )
    assert mod is mock_mod


def test_cargar_lista_blanca_detecta_cobra_toml_en_raiz(monkeypatch, tmp_path):
    proyecto = tmp_path / "proyecto"
    modulo_dir = proyecto / "src" / "pcobra" / "cobra"
    modulo_dir.mkdir(parents=True)
    archivo_modulo = modulo_dir / "usar_loader.py"
    archivo_modulo.write_text("# archivo simulado", encoding="utf-8")
    (proyecto / "cobra.toml").write_text(
        "[usar]\npermitidos = [\"paquete-demo==1.2.3\"]\n", encoding="utf-8"
    )

    monkeypatch.setattr(usar_loader, "__file__", str(archivo_modulo))
    monkeypatch.setattr(usar_loader, "tomli", __import__("tomllib"))

    usar_loader.cargar_lista_blanca()

    assert usar_loader.USAR_WHITELIST["paquete-demo"] == "paquete-demo==1.2.3"


def test_cargar_lista_blanca_sin_cobra_toml_mantiene_hardcoded(monkeypatch, tmp_path):
    modulo_dir = tmp_path / "instalacion" / "lib" / "cobra"
    modulo_dir.mkdir(parents=True)
    archivo_modulo = modulo_dir / "usar_loader.py"
    archivo_modulo.write_text("# archivo simulado", encoding="utf-8")

    monkeypatch.setattr(usar_loader, "__file__", str(archivo_modulo))
    monkeypatch.setattr(usar_loader, "tomli", __import__("tomllib"))

    usar_loader.cargar_lista_blanca()

    assert "numpy" in usar_loader.USAR_WHITELIST
    assert "agix" in usar_loader.USAR_WHITELIST


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


def test_obtener_modulo_delega_en_nuevo_resolver(monkeypatch):
    mock_mod = ModuleType('json')
    monkeypatch.setitem(usar_loader.USAR_WHITELIST, 'json', 'json')

    class FakeResolver:
        def __init__(self, *args, **kwargs):
            pass

        def load_module(self, nombre, fallback_backend='python'):
            assert nombre == 'json'
            assert fallback_backend == 'python'
            return object(), mock_mod

    from pcobra.cobra.imports import resolver as imports_resolver

    monkeypatch.setattr(imports_resolver, 'CobraImportResolver', FakeResolver)

    mod = usar_loader.obtener_modulo('json')

    assert mod is mock_mod


def test_obtener_modulo_hace_fallback_si_resolver_lanza_module_not_found(monkeypatch):
    mock_mod = ModuleType('json')
    monkeypatch.setitem(usar_loader.USAR_WHITELIST, 'json', 'json')

    class FakeResolver:
        def __init__(self, *args, **kwargs):
            pass

        def load_module(self, *_args, **_kwargs):
            raise ModuleNotFoundError("pcobra.standard_library.core")

    from pcobra.cobra.imports import resolver as imports_resolver

    monkeypatch.setattr(imports_resolver, 'CobraImportResolver', FakeResolver)
    monkeypatch.setattr(usar_loader.importlib, 'import_module', lambda name: mock_mod)

    mod = usar_loader.obtener_modulo('json')

    assert mod is mock_mod
