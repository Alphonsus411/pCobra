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
from core.environment import Environment
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
    mod.__all__ = ['sumar']
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




def test_repl_usar_numero_inyecta_funciones_globales(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_numero)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero", "texto": "texto"})

    interp.ejecutar_nodo(NodoUsar("numero"))

    assert "es_finito" in interp.variables
    assert interp.obtener_variable("es_finito")(10) is True


def test_repl_usar_texto_inyecta_funciones_globales(monkeypatch):
    import pcobra.corelibs.texto as modulo_texto

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_texto)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero", "texto": "texto"})

    interp.ejecutar_nodo(NodoUsar("texto"))

    assert "a_snake" in interp.variables
    assert interp.obtener_variable("a_snake")("HolaMundo") == "hola_mundo"
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


def test_repl_usar_colision_en_ancestro_no_inyecta_exportables(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_numero)
    interp = InterpretadorCobra()
    contexto_padre = interp.contextos[-1]
    contexto_hijo = Environment(parent=contexto_padre)
    # Contrato: no sobrescribir en toda la cadena léxica.
    contexto_padre.define("es_finito", lambda _valor: "ocupado")
    interp.contextos.append(contexto_hijo)
    interp.mem_contextos.append({})

    with pytest.raises(NameError, match=r"símbolo 'es_finito' ya existe"):
        interp.ejecutar_nodo(NodoUsar("numero"))

    assert contexto_padre.get("es_finito")("x") == "ocupado"
    assert "es_finito" not in contexto_hijo.values
    assert "a_decimal" not in contexto_hijo.values
    assert "es_entero" not in contexto_hijo.values

    interp.mem_contextos.pop()
    interp.contextos.pop()



def test_repl_usar_texto_colision_en_ancestro_es_atomico(monkeypatch):
    import pcobra.corelibs.texto as modulo_texto

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_texto)
    interp = InterpretadorCobra()
    contexto_padre = interp.contextos[-1]
    contexto_hijo = Environment(parent=contexto_padre)
    # Contrato: no sobrescribir en toda la cadena léxica.
    contexto_padre.define("a_snake", lambda _valor: "ocupado")
    interp.contextos.append(contexto_hijo)
    interp.mem_contextos.append({})

    with pytest.raises(NameError, match=r"símbolo 'a_snake' ya existe"):
        interp.ejecutar_nodo(NodoUsar("texto"))

    assert contexto_padre.get("a_snake")("Hola") == "ocupado"
    assert "a_snake" not in contexto_hijo.values
    assert "a_kebab" not in contexto_hijo.values
    assert "capitalizar" not in contexto_hijo.values

    interp.mem_contextos.pop()
    interp.contextos.pop()


@pytest.mark.parametrize("nombre", ["numpy", "node-fetch", "serde", "holobit_sdk"])
def test_usar_modulos_externos_rechazados_en_runtime_general(nombre):
    interp = InterpretadorCobra()

    with pytest.raises(PermissionError, match=r"módulo externo no permitido en REPL estricto \(solo alias oficiales Cobra\)"):
        interp.ejecutar_nodo(NodoUsar(nombre))


def test_usar_modulo_externo_rechazado_sin_estado_parcial():
    interp = InterpretadorCobra()
    interp.contextos[-1].define("sentinela", 42)
    estado_inicial = dict(interp.variables)

    with pytest.raises(PermissionError, match=r"solo alias oficiales Cobra"):
        _ejecutar_codigo('usar "numpy"', interp)

    assert interp.variables == estado_inicial


def test_repl_usar_numpy_falla_sin_estado_parcial():
    interp = InterpretadorCobra()
    interp.contextos[-1].define("sentinela", 42)
    estado_inicial = dict(interp.variables)
    simbolos_iniciales = set(interp.contextos[-1].values.keys())
    interp.configurar_restriccion_usar_repl({"numero": "numero", "texto": "texto"})

    with pytest.raises(PermissionError, match=r"módulo externo no permitido en REPL estricto \(solo alias oficiales Cobra\)"):
        _ejecutar_codigo('usar "numpy"', interp)

    assert interp.variables == estado_inicial
    assert simbolos_iniciales == set(interp.contextos[-1].values.keys())
    assert "numpy" not in interp.variables


@pytest.mark.parametrize(
    "escenario",
    [
        "alias_no_permitido",
        "modulo_sin___file__",
        "ruta_no_oficial",
    ],
)
def test_repl_usar_rechazo_externo_emite_mensaje_canonico(monkeypatch, escenario):
    modulo = ModuleType("numero")
    modulo.__all__ = ["es_finito"]
    modulo.es_finito = lambda valor: True

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero", "texto": "texto"})

    if escenario == "alias_no_permitido":
        with pytest.raises(PermissionError, match=r"módulo externo no permitido en REPL estricto \(solo alias oficiales Cobra\)"):
            interp.ejecutar_nodo(NodoUsar("numpy"))
        return

    if escenario == "modulo_sin___file__":
        monkeypatch.delattr(modulo, "__file__", raising=False)
    else:
        modulo.__file__ = "/tmp/externo/numero.py"

    monkeypatch.setattr(
        core_usar_loader,
        "obtener_modulo_cobra_oficial",
        lambda _nombre: modulo,
    )

    with pytest.raises(PermissionError, match=r"módulo externo no permitido en REPL estricto \(solo alias oficiales Cobra\)"):
        interp.ejecutar_nodo(NodoUsar("numero"))


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


def test_repl_semantica_oficial_plana_libro_parser_legacy_usar_numero_es_finito(monkeypatch):
    """Semántica oficial plana del libro con parser legacy `usar "..."`: numero exporta es_finito."""
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_numero)
    interp = _ejecutar_codigo('usar \"numero\"\nimprimir(es_finito(10))')

    assert "es_finito" in interp.variables
    assert interp.obtener_variable("es_finito")(10) is True


def test_repl_semantica_oficial_plana_libro_parser_legacy_usar_texto_a_snake(monkeypatch):
    """Semántica oficial plana del libro con parser legacy `usar "..."`: texto exporta a_snake."""
    import pcobra.corelibs.texto as modulo_texto

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_texto)
    interp = _ejecutar_codigo('usar \"texto\"\nimprimir(a_snake(\"HolaMundo\"))')

    assert "a_snake" in interp.variables
    assert interp.obtener_variable("a_snake")("HolaMundo") == "hola_mundo"


def test_repl_semantica_oficial_plana_libro_parser_legacy_colision_es_atomica(monkeypatch):
    """Semántica oficial plana del libro con parser legacy `usar "..."`: colisión sin inyección parcial."""
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_numero)
    interp = InterpretadorCobra()
    interp.contextos[-1].define("es_finito", lambda _x: "ocupado")

    with pytest.raises(NameError, match=r"símbolo 'es_finito' ya existe"):
        _ejecutar_codigo('usar "numero"', interp)

    assert interp.contextos[-1].get("es_finito")("x") == "ocupado"
    assert "es_infinito" not in interp.contextos[-1].values


def test_repl_no_habilita_acceso_por_punto_para_usar_numero(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_numero)
    with pytest.raises(InvalidTokenError, match=r"Token no reconocido: '\.'"):
        _ejecutar_codigo('usar "numero"\nnumero.es_finito(10)')


def test_repl_usar_modulo_oficial_sin_all_inyecta_callables_publicos(monkeypatch):
    modulo = ModuleType("numero")
    modulo.es_finito = lambda valor: valor == valor
    modulo.a_decimal = lambda valor: float(valor)
    modulo._interna = lambda valor: valor
    modulo.CONSTANTE = 7
    modulo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/numero.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: modulo)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero", "texto": "texto", "logica": "logica"})
    _ejecutar_codigo('usar "numero"\nes_finito(10)', interp)

    assert "es_finito" in interp.variables
    assert "a_decimal" in interp.variables
    assert "_interna" not in interp.variables
    assert "CONSTANTE" not in interp.variables


def test_repl_usar_modulo_oficial_con_all_mixto_filtra_callables_publicos(monkeypatch):
    modulo = ModuleType("texto")
    modulo.__all__ = ["a_snake", "_privada", "NO_CALLABLE", "faltante"]
    modulo.a_snake = lambda texto: "hola_mundo" if texto == "HolaMundo" else str(texto)
    modulo._privada = lambda texto: texto
    modulo.NO_CALLABLE = "valor"
    modulo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/texto.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: modulo)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero", "texto": "texto", "logica": "logica"})
    _ejecutar_codigo('usar "texto"\na_snake("HolaMundo")', interp)

    assert "a_snake" in interp.variables
    assert interp.obtener_variable("a_snake")("HolaMundo") == "hola_mundo"
    assert "_privada" not in interp.variables
    assert "NO_CALLABLE" not in interp.variables
    assert "faltante" not in interp.variables

def test_repl_usar_colision_policy_warn_alias_required_no_overwrite(monkeypatch):
    modulo = ModuleType("texto")
    modulo.__all__ = ["a_snake", "a_camel"]
    modulo.a_snake = lambda texto: texto
    modulo.a_camel = lambda texto: texto
    modulo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/texto.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: modulo)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"texto": "texto"})
    interp.configurar_politica_colision_usar("warn_alias_required")
    interp.contextos[-1].define("a_snake", lambda _texto: "ocupado")

    with pytest.raises(NameError, match=r"Requiere alias explícito"):
        _ejecutar_codigo('usar "texto"', interp)

    assert interp.contextos[-1].get("a_snake")("x") == "ocupado"
    assert "a_camel" not in interp.contextos[-1].values


def test_repl_usar_colision_multiple_sin_inyeccion_parcial(monkeypatch):
    modulo = ModuleType("texto")
    modulo.__all__ = ["a_snake", "a_camel", "quitar_prefijo"]
    modulo.a_snake = lambda texto: texto
    modulo.a_camel = lambda texto: texto
    modulo.quitar_prefijo = lambda texto, prefijo: texto.removeprefix(prefijo)
    modulo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/texto.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: modulo)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"texto": "texto"})
    interp.contextos[-1].define("a_snake", lambda _texto: "ocupado")
    interp.contextos[-1].define("a_camel", lambda _texto: "ocupado")

    with pytest.raises(NameError, match=r"symbol_collision"):
        _ejecutar_codigo('usar "texto"', interp)

    assert "quitar_prefijo" not in interp.contextos[-1].values


def test_usar_numero_exporta_solo_nombres_espanoles(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_numero)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero"})
    interp.ejecutar_nodo(NodoUsar("numero"))

    assert "es_finito" in interp.variables
    assert "isfinite" not in interp.variables


def test_usar_texto_exporta_solo_nombres_espanoles(monkeypatch):
    import pcobra.corelibs.texto as modulo_texto

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_texto)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"texto": "texto"})
    interp.ejecutar_nodo(NodoUsar("texto"))

    assert "a_snake" in interp.variables
    assert "to_snake_case" not in interp.variables


def test_usar_datos_incluye_filtrar_mapear_reducir(monkeypatch):
    import pcobra.standard_library.datos as modulo_datos

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_datos)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"datos": "datos"})
    interp.ejecutar_nodo(NodoUsar("datos"))

    for simbolo in ("filtrar", "mapear", "reducir"):
        assert simbolo in interp.variables


def test_usar_numpy_rechazado_en_superficie_publica():
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero", "texto": "texto", "datos": "datos"})

    with pytest.raises(PermissionError, match=r"solo alias oficiales Cobra"):
        interp.ejecutar_nodo(NodoUsar("numpy"))


def test_internals_holobit_sdk_no_importables_por_usar_loader():
    for nombre in ("holobit_sdk", "holobit_sdk.core", "holobit_sdk.visualization"):
        with pytest.raises(ValueError):
            usar_loader.obtener_modulo(nombre)


def test_usar_holobit_expone_solo_api_publica(monkeypatch):
    import pcobra.corelibs.holobit as modulo_holobit

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_holobit)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"holobit": "holobit"})
    interp.ejecutar_nodo(NodoUsar("holobit"))

    assert "holobit" in interp.variables
    assert "proyectar" in interp.variables
    assert "_require_holobit_sdk" not in interp.variables


def test_simbolos_exportados_por_usar_no_contienen_doble_guion_bajo(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_numero)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero"})
    interp.ejecutar_nodo(NodoUsar("numero"))

    assert all("__" not in simbolo for simbolo in interp.variables)


def test_usar_no_exporta_simbolos_bloqueados(monkeypatch):
    import pcobra.standard_library.datos as modulo_datos

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_datos)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"datos": "datos"})
    interp.ejecutar_nodo(NodoUsar("datos"))

    for simbolo in ("self", "append", "map", "filter", "unwrap", "expect"):
        assert simbolo not in interp.variables


def test_backends_legados_no_cargan_en_startup_normal():
    for nombre in ("go", "cpp", "java", "wasm", "asm"):
        with pytest.raises(PermissionError):
            usar_loader.obtener_modulo(nombre)


def test_politica_publica_backend_es_python_javascript_rust():
    from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS

    assert PUBLIC_BACKENDS == ("python", "javascript", "rust")
