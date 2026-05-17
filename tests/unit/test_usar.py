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
from core.ast_nodes import NodoLlamadaFuncion, NodoUsar, NodoValor
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




def test_repl_usar_numero_ejecuta_callable_runtime_es_finito(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_numero)
    interp = _ejecutar_codigo('usar \"numero\"\nes_finito(10)')

    llamada = NodoLlamadaFuncion("es_finito", [NodoValor(10)])
    assert interp.ejecutar_llamada_funcion(llamada) is True


def test_repl_usar_numero_ejecuta_callable_runtime_es_nan_con_math_nan(monkeypatch):
    import math
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_numero)
    # Caso explícito: validar es_nan(math.nan) en runtime.
    interp = _ejecutar_codigo('usar \"numero\"\nes_nan(math.nan)')

    llamada = NodoLlamadaFuncion("es_nan", [NodoValor(math.nan)])
    assert interp.ejecutar_llamada_funcion(llamada) is True


def test_repl_usar_numero_ejecuta_callable_runtime_es_nan_con_entero(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_numero)
    interp = _ejecutar_codigo('usar \"numero\"\nes_nan(10)')

    llamada = NodoLlamadaFuncion("es_nan", [NodoValor(10)])
    assert interp.ejecutar_llamada_funcion(llamada) is False



def test_repl_usar_texto_ejecuta_callables_runtime_basicos(monkeypatch):
    import pcobra.corelibs.texto as modulo_texto

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_texto)
    interp = _ejecutar_codigo('usar "texto"\nrecortar("  cobra  ")')

    assert interp.obtener_variable("recortar")("  cobra  ") == "cobra"
    assert interp.obtener_variable("repetir")("ja", 3) == "jajaja"
    assert interp.obtener_variable("quitar_acentos")("canción") == "cancion"
    assert interp.obtener_variable("prefijo_comun")("cobra", "cobre") == "cobr"
    assert interp.obtener_variable("sufijo_comun")("programacion", "nacion") == "acion"
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





def test_repl_usar_numero_regresion_es_finito_y_signo(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_numero)
    interp = _ejecutar_codigo('usar "numero"\nes_finito(10)\nsigno(0-5)')

    assert interp.obtener_variable("es_finito")(10) is True
    assert interp.obtener_variable("signo")(-5) == -1


def test_repl_usar_texto_regresion_mayusculas_recortar_repetir_quitar_acentos(monkeypatch):
    import pcobra.corelibs.texto as modulo_texto

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_texto)
    interp = _ejecutar_codigo('usar "texto"\nmayusculas("cobra")\nrecortar("  cobra  ")\nrepetir("co", 2)\nquitar_acentos("canción")')

    assert interp.obtener_variable("mayusculas")("cobra") == "COBRA"
    assert interp.obtener_variable("recortar")("  cobra  ") == "cobra"
    assert interp.obtener_variable("repetir")("co", 2) == "coco"
    assert interp.obtener_variable("quitar_acentos")("canción") == "cancion"


def test_repl_usar_logica_regresion_conjuncion_y_negacion(monkeypatch):
    import pcobra.corelibs.logica as modulo_logica

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_logica)
    interp = _ejecutar_codigo('usar "logica"\nconjuncion(verdadero, falso)\nnegacion(falso)')

    assert interp.obtener_variable("conjuncion")(True, False) is False
    assert interp.obtener_variable("negacion")(False) is True


def test_repl_usar_tiempo_regresion_epoch_valida_tipo_y_rango(monkeypatch):
    import pcobra.corelibs.tiempo as modulo_tiempo

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_tiempo)
    interp = _ejecutar_codigo('usar "tiempo"\nepoch()')

    valor_epoch = interp.obtener_variable("epoch")()
    assert isinstance(valor_epoch, (int, float))
    assert 0 <= valor_epoch < 4102444800


def test_repl_usar_datos_regresion_longitud_cobra(monkeypatch):
    import pcobra.corelibs.datos as modulo_datos

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_datos)
    interp = _ejecutar_codigo('usar "datos"\nlongitud("cobra")')

    assert interp.obtener_variable("longitud")("cobra") == 5

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


def test_repl_usar_numero_callables_policy_funcion_usuario_e_imprimir(monkeypatch, capsys):
    import math
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_numero)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero", "texto": "texto"})

    _ejecutar_codigo('usar "numero"', interp)
    assert interp.obtener_variable("es_finito")(10) is True
    assert interp.obtener_variable("es_nan")(math.nan) is True

    with pytest.raises(NameError, match=r"desviacion_estandar"):
        _ejecutar_codigo("desviacion_estandar([1, 2, 3])", interp)

    with pytest.raises(PermissionError, match=r"módulo externo no permitido en REPL estricto \(solo alias oficiales Cobra\)"):
        _ejecutar_codigo('usar "numpy"', interp)

    funcion_usuario = {
        "tipo": "funcion",
        "params": ["x"],
        "body": ["retornar x + 1"],
    }
    interp.contextos[-1].define("incrementar", funcion_usuario)
    llamada_usuario = NodoLlamadaFuncion("incrementar", [NodoValor(41)])
    assert interp.ejecutar_llamada_funcion(llamada_usuario) == 42

    _ejecutar_codigo("imprimir(verdadero)\nimprimir(falso)", interp)
    assert capsys.readouterr().out.strip().splitlines()[-2:] == ["verdadero", "falso"]
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


def test_usar_logica_dos_veces_es_idempotente(monkeypatch):
    import pcobra.corelibs.logica as modulo_logica

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_logica)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"logica": "logica"})

    _ejecutar_codigo('usar "logica"\nusar "logica"', interp)

    assert "es_verdadero" in interp.variables


def test_usar_numero_dos_veces_es_idempotente(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_numero)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero"})

    _ejecutar_codigo('usar "numero"\nusar "numero"', interp)

    assert "es_finito" in interp.variables


def test_usar_numero_conflicto_real_por_redefinicion_usuario(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_numero)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero"})
    interp.contextos[-1].define("es_finito", 123)

    with pytest.raises(NameError, match=r"conflicto"):
        _ejecutar_codigo('usar "numero"', interp)


def test_usar_conflicto_entre_modulos_distintos_mismo_nombre(monkeypatch):
    modulo_numero = ModuleType("numero")
    modulo_numero.__all__ = ["compartido"]
    modulo_numero.compartido = lambda valor: valor
    modulo_numero.__file__ = "/workspace/pCobra/src/pcobra/corelibs/numero.py"

    modulo_logica = ModuleType("logica")
    modulo_logica.__all__ = ["compartido"]
    modulo_logica.compartido = lambda valor: not valor
    modulo_logica.__file__ = "/workspace/pCobra/src/pcobra/corelibs/logica.py"

    def _resolver(nombre, **_kwargs):
        if nombre == "numero":
            return modulo_numero
        if nombre == "logica":
            return modulo_logica
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", _resolver)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero", "logica": "logica"})
    _ejecutar_codigo('usar "numero"', interp)

    with pytest.raises(NameError, match=r"conflicto"):
        _ejecutar_codigo('usar "logica"', interp)




def test_repl_usar_datos_imprimir_longitud_lista_produce_3(monkeypatch, capsys):
    import pcobra.standard_library.datos as modulo_datos

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_datos)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"datos": "datos"})

    _ejecutar_codigo('usar "datos"\nimprimir(longitud([1, 2, 3]))', interp)

    assert capsys.readouterr().out.strip().splitlines()[-1] == "3"


def test_usar_texto_expone_superficie_publica_clave(monkeypatch):
    import pcobra.corelibs.texto as modulo_texto

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_texto)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"texto": "texto"})
    interp.ejecutar_nodo(NodoUsar("texto"))

    for simbolo in ("recortar", "repetir", "quitar_acentos", "prefijo_comun", "sufijo_comun"):
        assert simbolo in interp.variables

    assert interp.obtener_variable("recortar")("  cobra  ") == "cobra"
    assert interp.obtener_variable("repetir")("ja", 3) == "jajaja"
    assert interp.obtener_variable("quitar_acentos")("canción") == "cancion"
    assert interp.obtener_variable("prefijo_comun")("cobra", "cobre") == "cobr"
    assert interp.obtener_variable("sufijo_comun")("programacion", "nacion") == "acion"


def test_usar_numero_conserva_es_finito_y_signo_operativos(monkeypatch):
    import pcobra.corelibs.numero as modulo_numero

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_numero)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero"})
    interp.ejecutar_nodo(NodoUsar("numero"))

    assert interp.obtener_variable("es_finito")(10) is True
    assert interp.obtener_variable("signo")(0 - 5) == -1


def test_usar_datos_no_exporta_objetos_backend_sdk_wrappers(monkeypatch):
    modulo = ModuleType("datos")
    modulo.__all__ = ["longitud", "backend", "sdk", "wrapper", "modulo_externo", "module_object", "backend_module_object", "USAR_RUNTIME_EXPORT_OVERRIDES", "REPL_COBRA_MODULE_INTERNAL_PATH_MAP"]
    modulo.longitud = lambda xs: len(xs)
    modulo.backend = ModuleType("backend")
    modulo.sdk = ModuleType("sdk")
    modulo.wrapper = ModuleType("wrapper")
    modulo.modulo_externo = ModuleType("modulo_externo")
    modulo.module_object = object()
    modulo.backend_module_object = object()
    modulo.USAR_RUNTIME_EXPORT_OVERRIDES = object()
    modulo.REPL_COBRA_MODULE_INTERNAL_PATH_MAP = object()
    modulo.__file__ = "/workspace/pCobra/src/pcobra/standard_library/datos.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: modulo)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"datos": "datos"})

    with pytest.raises(ImportError, match=r"rechazos de saneamiento en usar"):
        interp.ejecutar_nodo(NodoUsar("datos"))

    assert "longitud" not in interp.variables
    for simbolo in (
        "backend",
        "sdk",
        "wrapper",
        "modulo_externo",
        "module_object",
        "backend_module_object",
        "USAR_RUNTIME_EXPORT_OVERRIDES",
        "REPL_COBRA_MODULE_INTERNAL_PATH_MAP",
    ):
        assert simbolo not in interp.variables
def test_usar_datos_incluye_filtrar_mapear_reducir(monkeypatch):
    import pcobra.standard_library.datos as modulo_datos

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_datos)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"datos": "datos"})
    interp.ejecutar_nodo(NodoUsar("datos"))

    for simbolo in ("filtrar", "mapear", "reducir"):
        assert simbolo in interp.variables



def test_usar_datos_operaciones_basicas_agregar_mapear_filtrar(monkeypatch):
    import pcobra.standard_library.datos as modulo_datos

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: modulo_datos)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"datos": "datos"})
    interp.ejecutar_nodo(NodoUsar("datos"))

    tabla = [{"valor": 1}, {"valor": 2}]

    assert interp.obtener_variable("agregar")(tabla, {"valor": 3})[-1]["valor"] == 3
    assert interp.obtener_variable("mapear")(tabla, lambda fila: {**fila, "valor": fila["valor"] * 2}) == [
        {"valor": 2},
        {"valor": 4},
    ]
    assert interp.obtener_variable("filtrar")(tabla, lambda fila: fila["valor"] % 2 == 0) == [{"valor": 2}]

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


def test_repl_usar_emite_evento_telemetria_saneamiento_rechazado(monkeypatch, caplog):
    modulo = ModuleType("mod_ext")
    modulo.__all__ = ["ok", "backend"]
    modulo.ok = lambda valor: valor
    modulo.backend = ModuleType("backend_obj")
    modulo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/mod_ext.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: modulo)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"mod_ext": "mod_ext"})

    with pytest.raises(ImportError, match=r"rechazos de saneamiento en usar"):
        interp.ejecutar_nodo(NodoUsar("mod_ext"))

    assert "usar_sanitize_reject" in caplog.text
    assert "simbolos_rechazados" in caplog.text


def test_repl_usar_emite_evento_telemetria_colision_warn(monkeypatch, caplog):
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
        interp.ejecutar_nodo(NodoUsar("texto"))

    assert "usar_collision" in caplog.text
    assert "warn_alias_required" in caplog.text


@pytest.mark.parametrize("nombre", ["numpy", "node-fetch", "serde", "holobit_sdk"])
def test_usar_loader_rechaza_numpy_y_equivalentes_prohibidos(nombre):
    with pytest.raises(PermissionError, match=r"Importación no permitida en 'usar'"):
        usar_loader.obtener_modulo(nombre)


def test_usar_rechaza_modulo_no_canonico_en_repl_estricto():
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"num": "numero"})

    with pytest.raises(PermissionError, match=r"usar_error\[modulo_no_canonico\]"):
        interp.ejecutar_nodo(NodoUsar("numero"))




def test_repl_usar_texto_simbolo_fuera_de_overrides_no_disponible(monkeypatch):
    import pcobra.corelibs.texto as modulo_texto

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_texto)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"texto": "texto"})

    with pytest.raises(NameError, match=r"capitalizar"):
        _ejecutar_codigo('usar "texto"\ncapitalizar("hola")', interp)


def test_usar_texto_mantiene_filtro_outside_public_api_para_capitalizar(monkeypatch):
    modulo_texto = core_usar_loader.obtener_modulo_cobra_oficial("texto")

    _, conflictos = core_usar_loader.sanitizar_exports_publicos(modulo_texto, "texto")
    conflicto_capitalizar = next(
        (c for c in conflictos if c.get("symbol") == "capitalizar"),
        None,
    )

    assert conflicto_capitalizar is not None
    assert conflicto_capitalizar["code"] == "outside_public_api"
    assert conflicto_capitalizar["symbol"] == "capitalizar"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_texto)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"texto": "texto"})

    with pytest.raises(NameError, match=r"capitalizar"):
        _ejecutar_codigo('usar "texto"\ncapitalizar("hola")', interp)

    assert "capitalizar" not in interp.variables


def test_usar_error_export_invalido_es_diferenciado(monkeypatch):
    modulo = ModuleType("texto")
    modulo.__all__ = ["NO_CALLABLE"]
    modulo.NO_CALLABLE = "valor"
    modulo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/texto.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: modulo)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"texto": "texto"})

    with pytest.raises(ImportError, match=r"no hay símbolos exportables válidos"):
        interp.ejecutar_nodo(NodoUsar("texto"))


def test_usar_no_muestra_traceback_ni_detalle_en_modo_normal(monkeypatch, caplog):
    modulo = ModuleType("texto")
    modulo.__all__ = ["a_snake"]
    modulo.a_snake = lambda texto: texto
    modulo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/texto.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: modulo)
    monkeypatch.delenv("PCOBRA_DEBUG_RUNTIME", raising=False)
    monkeypatch.delenv("PCOBRA_DEBUG_TRACES", raising=False)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"texto": "texto"})
    interp.contextos[-1].define("a_snake", lambda _texto: "ocupado")

    with pytest.raises(NameError) as excinfo:
        interp.ejecutar_nodo(NodoUsar("texto"))

    texto_error = str(excinfo.value)
    assert "conflicto de símbolos" in texto_error
    assert "detalle=" not in texto_error
    assert "Traceback" not in caplog.text


def test_usar_muestra_detalle_extendido_en_debug(monkeypatch, caplog):
    modulo = ModuleType("texto")
    modulo.__all__ = ["a_snake"]
    modulo.a_snake = lambda texto: texto
    modulo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/texto.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: modulo)
    monkeypatch.setenv("PCOBRA_DEBUG_RUNTIME", "1")

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"texto": "texto"})
    interp.contextos[-1].define("a_snake", lambda _texto: "ocupado")

    with pytest.raises(NameError) as excinfo:
        interp.ejecutar_nodo(NodoUsar("texto"))

    texto_error = str(excinfo.value)
    assert "detalle=" in texto_error
    assert "Traceback" in caplog.text


def test_usar_error_carga_modulo_mensaje_corto_en_modo_normal(monkeypatch, caplog):
    monkeypatch.setattr(
        core_usar_loader,
        "obtener_modulo_cobra_oficial",
        lambda _nombre: (_ for _ in ()).throw(ModuleNotFoundError("boom")),
    )
    monkeypatch.delenv("PCOBRA_DEBUG_RUNTIME", raising=False)
    monkeypatch.delenv("PCOBRA_DEBUG_TRACES", raising=False)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"texto": "texto"})

    with pytest.raises(ImportError) as excinfo:
        interp.ejecutar_nodo(NodoUsar("texto"))

    texto_error = str(excinfo.value)
    assert "error al cargar el módulo" in texto_error
    assert "boom" not in texto_error
    assert "Traceback" not in caplog.text


def test_usar_warning_conflictos_saneamiento_formato_compacto(monkeypatch, caplog):
    modulo = ModuleType("texto")
    modulo.__all__ = ["A_snake", "a_snake"]
    modulo.A_snake = lambda texto: texto
    modulo.a_snake = lambda texto: texto
    modulo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/texto.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: modulo)
    monkeypatch.delenv("PCOBRA_DEBUG_RUNTIME", raising=False)
    monkeypatch.delenv("PCOBRA_DEBUG_TRACES", raising=False)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"texto": "texto"})

    with pytest.raises(ImportError):
        interp.ejecutar_nodo(NodoUsar("texto"))

    warnings_saneamiento = [
        rec.message for rec in caplog.records if "USAR sanitize conflicts event module=texto" in rec.message
    ]
    assert warnings_saneamiento
    warning = warnings_saneamiento[-1]
    assert "module=texto" in warning
    assert "count=2" in warning
    assert "conflicts=[" not in warning
    assert "{'symbol'" not in warning




def test_usar_warning_conflictos_saneamiento_formato_texto_estable(monkeypatch, caplog):
    modulo = ModuleType("numero")
    modulo.__all__ = ["A_snake", "a_snake"]
    modulo.A_snake = lambda n: n
    modulo.a_snake = lambda n: n
    modulo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/numero.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: modulo)
    monkeypatch.delenv("PCOBRA_DEBUG_RUNTIME", raising=False)
    monkeypatch.delenv("PCOBRA_DEBUG_TRACES", raising=False)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero"})

    with pytest.raises(ImportError):
        interp.ejecutar_nodo(NodoUsar("numero"))

    warnings_saneamiento = [
        rec.message for rec in caplog.records if "USAR sanitize conflicts event module=numero" in rec.message
    ]
    assert warnings_saneamiento
    assert warnings_saneamiento[-1] == "USAR sanitize conflicts event module=numero count=2 sample=[A_snake->a_snake,a_snake]"


def test_usar_warning_conflictos_saneamiento_detalle_solo_debug(monkeypatch, caplog):
    modulo = ModuleType("texto")
    modulo.__all__ = ["A_snake", "a_snake"]
    modulo.A_snake = lambda texto: texto
    modulo.a_snake = lambda texto: texto
    modulo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/texto.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: modulo)
    monkeypatch.setenv("PCOBRA_DEBUG_RUNTIME", "1")

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"texto": "texto"})

    with pytest.raises(ImportError):
        interp.ejecutar_nodo(NodoUsar("texto"))

    warnings_saneamiento = [
        rec.message for rec in caplog.records if "USAR sanitize conflicts event module=texto" in rec.message
    ]
    assert warnings_saneamiento
    warning = warnings_saneamiento[-1]
    assert "count=2" in warning
    assert "conflicts=[" not in warning

    trazas_debug = [
        rec.message for rec in caplog.records if "[USAR_SANITIZE][CONFLICTS]" in rec.message
    ]
    assert trazas_debug
    assert "'conflicts':" in trazas_debug[-1]



def test_usar_warning_colision_alias_formato_compacto(monkeypatch, caplog):
    modulo = ModuleType("numero")
    modulo.__all__ = ["sumar"]
    modulo.sumar = lambda a, b: a + b
    modulo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/numero.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: modulo)
    monkeypatch.delenv("PCOBRA_DEBUG_RUNTIME", raising=False)
    monkeypatch.delenv("PCOBRA_DEBUG_TRACES", raising=False)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero"})
    interp.configurar_politica_colision_usar("warn_alias_required")
    interp.contextos[-1].define("sumar", lambda a, b: a - b)

    with pytest.raises(NameError):
        interp.ejecutar_nodo(NodoUsar("numero"))

    warnings_colision = [
        rec.message for rec in caplog.records if rec.message.startswith("WARNING: No se puede usar 'numero'")
    ]
    assert warnings_colision
    warning = warnings_colision[-1]
    assert warning == (
        "WARNING: No se puede usar 'numero': hay conflicto de símbolos en el contexto actual. "
        "Use alias explícito para resolver la colisión. module=numero count=1"
    )
    assert "{" not in warning
    assert "detalle=" not in warning


def test_repl_runtime_usar_datos_elemento_y_regresiones_con_errores_limpios(monkeypatch, capsys):
    import pcobra.standard_library.datos as modulo_datos

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: modulo_datos)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"datos": "datos"})

    _ejecutar_codigo('''usar "datos"
var ys = [10, 20, 30]
imprimir(elemento(ys, 0))
imprimir(elemento([1, 2, 3], 2))
imprimir(elemento(ys, 1))
imprimir(longitud([1, 2, 3]))''', interp)

    out = capsys.readouterr().out.strip().splitlines()
    assert "elemento" in interp.variables
    assert out[-4:] == ["10", "3", "20", "3"]

    with pytest.raises(IndexError, match="^Error: índice fuera de rango$") as err_indice:
        _ejecutar_codigo('''usar "datos"
var ys = [10, 20, 30]
elemento(ys, 99)''', interp)
    assert "Traceback" not in str(err_indice.value)

    with pytest.raises(TypeError, match="^Error: índice debe ser entero$") as err_tipo_indice:
        _ejecutar_codigo('''usar "datos"
var ys = [10, 20, 30]
elemento(ys, "0")''', interp)
    assert "Traceback" not in str(err_tipo_indice.value)

    with pytest.raises(TypeError, match="^Error: objeto no indexable$") as err_objeto:
        _ejecutar_codigo('''usar "datos"
elemento(10, 0)''', interp)
    assert "Traceback" not in str(err_objeto.value)

    with pytest.raises(PermissionError, match="No se puede usar 'numpy': módulo fuera del catálogo público"):
        _ejecutar_codigo('usar "numpy"', interp)

    with pytest.raises(InvalidTokenError, match="Se esperaba una cadena"):
        _ejecutar_codigo('usar archivo', interp)
