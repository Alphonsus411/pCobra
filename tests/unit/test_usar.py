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
from core.errors import InvalidTokenError
from core.ast_nodes import NodoUsar
from cobra.core import Lexer, Parser
from cobra import usar_loader
from core import usar_loader as core_usar_loader


def test_obtener_modulo_instala_si_no_existe(monkeypatch):
    mock_mod = ModuleType('demo')
    monkeypatch.setitem(usar_loader.USAR_WHITELIST, 'demo', 'demo')
    monkeypatch.setenv('COBRA_USAR_INSTALL', '1')
    real_import = usar_loader.importlib.import_module
    def _side_effect(name, *args, **kwargs):
        if name.startswith('pcobra.'):
            return real_import(name, *args, **kwargs)
        if name == 'demo':
            _side_effect.calls += 1
            if _side_effect.calls == 1:
                raise ModuleNotFoundError()
            return mock_mod
        return real_import(name, *args, **kwargs)
    _side_effect.calls = 0
    with patch.object(usar_loader.importlib, 'import_module', side_effect=_side_effect) as mock_import, \
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
    mod.sumar = lambda a, b: a + b
    monkeypatch.setattr(core_usar_loader, 'obtener_modulo', lambda _name, **_kwargs: mod)
    interp = InterpretadorCobra()
    interp.ejecutar_nodo(NodoUsar('math'))
    assert interp.obtener_variable('sumar')(1, 2) == 3


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


def _ejecutar_codigo(codigo: str, interp: InterpretadorCobra | None = None) -> InterpretadorCobra:
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    interprete = interp or InterpretadorCobra()
    interprete.ejecutar_ast(ast)
    return interprete


def test_repl_usar_numero_permite_es_finito_sin_prefijo(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_numero)
    interp = _ejecutar_codigo('usar "numero"\nes_finito(10)')

    assert "es_finito" in interp.variables
    assert interp.obtener_variable("es_finito")(10) is True


def test_repl_usar_texto_permite_a_snake_sin_prefijo(monkeypatch):
    import pcobra.corelibs.texto as modulo_texto

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_texto)
    interp = _ejecutar_codigo('usar "texto"\na_snake("HolaMundo")')

    assert "a_snake" in interp.variables
    assert interp.obtener_variable("a_snake")("HolaMundo") == "hola_mundo"


def test_repl_usar_detecta_colision_de_simbolo_existente(monkeypatch):
    import pcobra.corelibs.texto as modulo_texto

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_texto)
    interp = InterpretadorCobra()
    interp.contextos[-1].define("a_snake", lambda x: x)

    with pytest.raises(NameError, match=r"símbolo 'a_snake' ya existe"):
        interp.ejecutar_nodo(NodoUsar('texto'))


def test_repl_usar_colision_no_inyecta_ningun_simbolo(monkeypatch):
    modulo = ModuleType("mi_modulo")
    modulo.colisiona = lambda x: x
    modulo.disponible = lambda x: x
    modulo.__all__ = ["colisiona", "disponible"]

    monkeypatch.setattr(
        core_usar_loader,
        "obtener_modulo",
        lambda _nombre, **_kwargs: modulo,
    )
    interp = InterpretadorCobra()
    interp.contextos[-1].define("colisiona", lambda x: x)

    with pytest.raises(NameError, match=r"símbolo 'colisiona' ya existe"):
        interp.ejecutar_nodo(NodoUsar("mi_modulo"))

    assert interp.obtener_variable("colisiona") is not None
    assert "disponible" not in interp.variables


def test_repl_usar_numpy_falla_sin_estado_parcial():
    interp = InterpretadorCobra()
    interp.contextos[-1].define("sentinela", 42)
    estado_inicial = dict(interp.variables)
    interp.configurar_restriccion_usar_repl({"numero": "numero", "texto": "texto"})

    with pytest.raises(PermissionError, match="módulos externos no soportados en REPL"):
        _ejecutar_codigo('usar "numpy"', interp)

    assert interp.variables == estado_inicial
    assert "numpy" not in interp.variables


def test_obtener_modulo_alias_cobra_usa_origen_oficial(monkeypatch):
    modulo_oficial = ModuleType("numero")
    modulo_oficial.es_finito = lambda valor: True
    monkeypatch.setitem(usar_loader.USAR_WHITELIST, "numero", "numero")

    llamadas = {"oficial": 0, "importlib": 0}

    def _resolver_fallido(*_args, **_kwargs):
        from pcobra.cobra.imports.resolver import ImportResolutionError

        raise ImportResolutionError("sin backend")

    class FakeResolver:
        def __init__(self, *args, **kwargs):
            pass

        load_module = _resolver_fallido

    def _import_module_controlado(nombre, *args, **kwargs):
        if nombre == "numero":
            llamadas["importlib"] += 1
            raise ModuleNotFoundError(nombre)
        return importlib_import_real(nombre, *args, **kwargs)

    def _oficial_controlado(nombre):
        llamadas["oficial"] += 1
        assert nombre == "numero"
        return modulo_oficial

    importlib_import_real = usar_loader.importlib.import_module
    from pcobra.cobra.imports import resolver as imports_resolver

    monkeypatch.setattr(imports_resolver, "CobraImportResolver", FakeResolver)
    monkeypatch.setattr(usar_loader.importlib, "import_module", _import_module_controlado)
    monkeypatch.setattr(usar_loader, "obtener_modulo_cobra_oficial", _oficial_controlado)

    modulo = usar_loader.obtener_modulo("numero")

    assert modulo is modulo_oficial
    assert llamadas == {"oficial": 1, "importlib": 1}


def test_repl_no_habilita_acceso_por_punto_para_usar_numero(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_numero)
    with pytest.raises(InvalidTokenError, match=r"Token no reconocido: '\.'"):
        _ejecutar_codigo('usar "numero"\nnumero.es_finito(10)')
