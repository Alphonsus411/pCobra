from __future__ import annotations

from pathlib import Path
from types import ModuleType
import asyncio
import importlib
import logging
import pytest
import httpx

from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.commands_v2.repl_cmd import ReplCommandV2
from pcobra.cobra.core.parser import ParserError
from pcobra.core import usar_loader as core_usar_loader
from pcobra.cobra import usar_loader as cli_usar_loader
from pcobra.cobra.core.runtime import InterpretadorCobra
from pcobra.core.ast_nodes import NodoUsar
from pcobra.cobra.usar_policy import REPL_COBRA_MODULE_MAP
import pcobra.core.interpreter as core_interpreter_module
import pcobra.core.usar_symbol_policy as usar_symbol_policy_module


def _modulo_numero_stub() -> ModuleType:
    mod = ModuleType("numero")
    mod.__all__ = ["es_finito", "signo"]
    mod.es_finito = lambda valor: valor == valor and valor not in (float("inf"), float("-inf"))
    mod.signo = lambda valor: -1 if valor < 0 else (1 if valor > 0 else 0)
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/numero.py"
    return mod


def _modulo_texto_stub() -> ModuleType:
    mod = ModuleType("texto")
    mod.__all__ = ["a_snake", "mayusculas", "recortar", "repetir", "quitar_acentos"]
    mod.a_snake = lambda texto: "hola_mundo" if texto == "HolaMundo" else str(texto)
    mod.mayusculas = lambda texto: str(texto).upper()
    mod.recortar = lambda texto: str(texto).strip()
    mod.repetir = lambda texto, veces=2: str(texto) * int(veces)
    mod.quitar_acentos = lambda texto: str(texto).translate(str.maketrans("áéíóú", "aeiou"))
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/texto.py"
    return mod


@pytest.mark.parametrize("factory", [lambda: InteractiveCommand(InterpretadorCobra()), ReplCommandV2])
def test_entrypoints_repl_configuran_restriccion_estricta(factory):
    cmd = factory()
    interp = cmd.interpretador if isinstance(cmd, InteractiveCommand) else cmd._delegate.interpretador
    assert interp._repl_usar_alias_map == REPL_COBRA_MODULE_MAP


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_contract_sintaxis_usar_compat_parser_semantica_plana_numero_sin_prefijo(factory, executor, get_interp, monkeypatch):
    mod_numero = _modulo_numero_stub()

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "numero":
            return mod_numero
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    # monkeypatch.setattr(
    #     core_interpreter_module,
    #     "build_and_validate_usar_symbol_metadata",
    #     lambda module_name, symbol_name, callable_obj: {"origin_kind": "usar", "module": module_name, "symbol": symbol_name, "sanitized": True, "public_api": True, "callable": True, "backend_exposed": False},
    # )

    # monkeypatch.setattr(
    #     usar_symbol_policy_module,
    #     "build_and_validate_usar_symbol_metadata",
    #     lambda module_name, symbol_name, callable_obj: {"origin_kind": "usar", "module": module_name, "symbol": symbol_name, "sanitized": True, "public_api": True, "callable": True, "backend_exposed": False},
    # )

    cmd = factory()
    interp = get_interp(cmd)

    executor(cmd, 'usar "numero"')
    executor(cmd, "es_finito(10)")

    assert interp.obtener_variable("es_finito")(10) is True
    assert interp.obtener_variable("signo")(-8) == -1


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_contract_sintaxis_usar_compat_parser_semantica_plana_texto_sin_prefijo(factory, executor, get_interp, monkeypatch):
    mod_texto = _modulo_texto_stub()

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "texto":
            return mod_texto
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))
    # monkeypatch.setattr(
    #     core_interpreter_module,
    #     "build_and_validate_usar_symbol_metadata",
    #     lambda module_name, symbol_name, callable_obj: {"origin_kind": "usar", "module": module_name, "symbol": symbol_name, "sanitized": True, "public_api": True, "callable": True, "backend_exposed": False},
    # )

    cmd = factory()
    interp = get_interp(cmd)

    executor(cmd, 'usar "texto"')
    executor(cmd, 'mayusculas("cobra")')

    assert interp.obtener_variable("mayusculas")("cobra") == "COBRA"
    assert interp.obtener_variable("recortar")(" cobra ") == "cobra"
    assert interp.obtener_variable("repetir")("co", 2) == "coco"
    assert interp.obtener_variable("quitar_acentos")("canción") == "cancion"


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_usar_texto_end_to_end_superficie_publica_callables(factory, executor, get_interp):
    cmd = factory()
    interp = get_interp(cmd)

    executor(cmd, 'usar "texto"')

    assert interp.obtener_variable("recortar")("  Cobra  ") == "Cobra"
    assert interp.obtener_variable("repetir")("ja", 3) == "jajaja"
    assert interp.obtener_variable("quitar_acentos")("canción") == "cancion"
    assert interp.obtener_variable("prefijo_comun")("cobra", "cobre") == "cobr"
    assert interp.obtener_variable("sufijo_comun")("programacion", "nacion") == "acion"


def test_repl_entrypoint_numero_es_finito_imprime_verdadero(capsys):
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "numero"')
    cmd._ejecutar_en_modo_normal("imprimir(es_finito(10))")

    salida = [linea.strip() for linea in capsys.readouterr().out.splitlines() if linea.strip()]
    assert "verdadero" in salida


def test_repl_entrypoint_archivo_existe_booleano_sin_error_metadata(capsys):
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "archivo"')
    cmd._ejecutar_en_modo_normal('imprimir(existe("README.md"))')

    salida = capsys.readouterr().out
    assert "Error: metadata" not in salida
    assert any(token in salida for token in ("verdadero", "falso"))


def test_repl_entrypoint_usar_archivo_sin_comillas_falla_por_sintaxis():
    cmd = ReplCommandV2()
    with pytest.raises(ParserError, match=r"Token inesperado|Token no reconocido|sintaxis|SyntaxError|ruta de módulo entre comillas"):
        cmd._ejecutar_en_modo_normal("usar archivo")


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_contract_sintaxis_usar_compat_parser_semantica_plana_numpy_restringido_atomico(factory, executor, get_interp, monkeypatch):
    mod_numero = _modulo_numero_stub()

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "numero":
            return mod_numero
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))
    # monkeypatch.setattr(
    #     core_interpreter_module,
    #     "build_and_validate_usar_symbol_metadata",
    #     lambda module_name, symbol_name, callable_obj: {"origin_kind": "usar", "module": module_name, "symbol": symbol_name, "sanitized": True, "public_api": True, "callable": True, "backend_exposed": False},
    # )

    cmd = factory()
    interp = get_interp(cmd)
    executor(cmd, 'usar "numero"')
    estado_pre_numpy = dict(interp.contextos[-1].values)
    simbolos_pre = set(interp.contextos[-1].values.keys())

    with pytest.raises(PermissionError, match=r"Importación no permitida en 'usar': 'numpy'.*usar_error\[modulo_fuera_catalogo_publico\]"):
        executor(cmd, 'usar "numpy"')

    # Contrato de Cobra: `usar` es plano (sin `.`), no se expone namespace tipo `numero.*`.
    assert "numpy" not in interp.variables
    assert "numpy" not in interp.contextos[-1].values
    assert estado_pre_numpy == interp.contextos[-1].values
    assert simbolos_pre == set(interp.contextos[-1].values.keys())

    # Después de usar "numero", es_finito debe estar disponible directamente
    assert interp.obtener_variable("es_finito")(10) is True





def _modulo_tiempo_stub() -> ModuleType:
    mod = ModuleType("tiempo")
    mod.__all__ = ["ahora"]
    mod.ahora = lambda: "2026-05-03T00:00:00"
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/tiempo.py"
    return mod


def _modulo_datos_stub() -> ModuleType:
    mod = ModuleType("datos")
    mod.__all__ = ["longitud", "elemento"]
    mod.longitud = lambda valores: len(valores)
    mod.elemento = lambda valores, indice: valores[indice]
    mod._backend = object()
    mod.module_object = object()
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/datos.py"
    return mod

def _modulo_numero_multi_export_stub() -> ModuleType:
    mod = ModuleType("numero")
    mod.__all__ = ["es_finito", "es_par"]
    mod.es_finito = lambda valor: valor == valor and valor not in (float("inf"), float("-inf"))
    mod.es_par = lambda valor: isinstance(valor, int) and valor % 2 == 0
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/numero.py"
    return mod


def _assert_contrato_simbolos_saneados(simbolos: set[str]) -> None:
    bloqueados_explicitos = {"self", "append", "map", "filter", "unwrap", "expect"}
    for simbolo in simbolos:
        assert "__" not in simbolo
        assert not simbolo.startswith("_")
        assert simbolo not in bloqueados_explicitos


def _modulo_holobit_publico_stub() -> ModuleType:
    mod = ModuleType("holobit")
    mod.__all__ = [
        "crear_holobit",
        "validar_holobit",
        "serializar_holobit",
        "deserializar_holobit",
        "proyectar",
        "transformar",
        "graficar",
        "combinar",
        "medir",
    ]
    for nombre in mod.__all__:
        setattr(mod, nombre, lambda *args, _nombre=nombre, **kwargs: {"ok": _nombre, "args": args, "kwargs": kwargs})
    mod.Holobit = object
    mod._to_sdk_holobit = lambda *_args, **_kwargs: None
    mod.holobit_sdk = object()
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/holobit.py"
    return mod


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_contract_sintaxis_usar_compat_parser_semantica_plana_colision_no_sobrescribe_usuario(factory, executor, get_interp, monkeypatch):
    mod_numero = _modulo_numero_multi_export_stub()
    mod_texto = _modulo_texto_stub()

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "numero":
            return mod_numero
        if nombre == "texto":
            return mod_texto
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))
    # monkeypatch.setattr(
    #     core_interpreter_module,
    #     "build_and_validate_usar_symbol_metadata",
    #     lambda module_name, symbol_name, callable_obj: {"origin_kind": "usar", "module": module_name, "symbol": symbol_name, "sanitized": True, "public_api": True, "callable": True, "backend_exposed": False},
    # )

    cmd = factory()
    interp = get_interp(cmd)
    interp.contextos[-1].define("es_finito", lambda _valor: "ocupado")

    with pytest.raises(NameError, match=r"No se puede usar( el módulo)? 'numero':"):
        executor(cmd, 'usar "numero"')

    assert interp.obtener_variable("es_finito")("x") == "ocupado"
    assert "es_par" not in interp.contextos[-1].values


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_rechazo_externo_no_inyecta_simbolos(factory, executor, get_interp, monkeypatch):
    mod_numero = _modulo_numero_stub()

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "numero":
            return mod_numero
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))


    cmd = factory()
    interp = get_interp(cmd)
    estado_pre = dict(interp.contextos[-1].values)

    with pytest.raises(PermissionError, match=r"(módulo fuera del catálogo público|modulo_fuera_catalogo_publico)"):
        executor(cmd, 'usar "requests"')

    assert estado_pre == interp.contextos[-1].values
    assert "requests" not in interp.contextos[-1].values


def test_interprete_corelibs_superficie_minima_requerida():
    interp = InterpretadorCobra()
    interp.ejecutar_nodo(NodoUsar("numero"))
    assert interp.obtener_variable("es_finito")(10) is True
    assert interp.obtener_variable("signo")(-8) == -1
    assert interp.obtener_variable("signo")(0 - 5) == -1

    interp.ejecutar_nodo(NodoUsar("texto"))
    assert interp.obtener_variable("mayusculas")("cobra") == "COBRA"
    assert interp.obtener_variable("recortar")(" cobra ") == "cobra"
    assert interp.obtener_variable("repetir")("co", 2) == "coco"
    assert interp.obtener_variable("quitar_acentos")("canción") == "cancion"

    interp.ejecutar_nodo(NodoUsar("logica"))
    assert interp.obtener_variable("conjuncion")(True, False) is False
    assert interp.obtener_variable("negacion")(False) is True

    interp.ejecutar_nodo(NodoUsar("tiempo"))
    epoch_valor = interp.obtener_variable("epoch")()
    assert isinstance(epoch_valor, (int, float))

    interp.ejecutar_nodo(NodoUsar("datos"))
    assert interp.obtener_variable("longitud")("cobra") == 5


def test_seguridad_usar_numpy_error_corto_sin_traceback_modo_normal(caplog, monkeypatch):
    monkeypatch.delenv("PCOBRA_DEBUG_RUNTIME", raising=False)
    monkeypatch.delenv("PCOBRA_DEBUG_TRACES", raising=False)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(REPL_COBRA_MODULE_MAP)

    with pytest.raises(PermissionError) as excinfo:
        interp.ejecutar_nodo(NodoUsar("numpy"))

    mensaje = str(excinfo.value)
    assert "Traceback" not in mensaje
    assert "Importación no permitida en 'usar': 'numpy'. Es un módulo backend/no canónico y no forma parte de la API pública." in mensaje
    assert "Traceback" not in caplog.text




@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_integracion_usar_modulos_publicos_end_to_end(factory, executor, get_interp):
    cmd = factory()
    interp = get_interp(cmd)

    executor(cmd, 'usar "numero"')
    executor(cmd, "es_finito(10)")
    assert interp.obtener_variable("es_finito")(10) is True
    assert interp.obtener_variable("signo")(-8) == -1
    assert interp.obtener_variable("signo")(0 - 5) == -1

    executor(cmd, 'usar "texto"')
    executor(cmd, 'mayusculas("cobra")')
    executor(cmd, 'recortar(" cobra ")')
    executor(cmd, 'repetir("co", 2)')
    executor(cmd, 'quitar_acentos("canción")')
    assert interp.obtener_variable("mayusculas")("cobra") == "COBRA"
    assert interp.obtener_variable("recortar")(" cobra ") == "cobra"
    assert interp.obtener_variable("repetir")("co", 2) == "coco"
    assert interp.obtener_variable("quitar_acentos")("canción") == "cancion"

    executor(cmd, 'usar "logica"')
    executor(cmd, "conjuncion(verdadero, falso)")
    executor(cmd, "negacion(falso)")
    assert interp.obtener_variable("conjuncion")(True, False) is False
    assert interp.obtener_variable("negacion")(False) is True

    executor(cmd, 'usar "tiempo"')
    executor(cmd, "epoch()")
    epoch_valor = interp.obtener_variable("epoch")()
    assert isinstance(epoch_valor, (int, float))
    assert 946684800 <= epoch_valor <= 4102444800

    executor(cmd, 'usar "datos"')
    executor(cmd, 'longitud("cobra")')
    assert interp.obtener_variable("longitud")("cobra") == 5


@pytest.mark.parametrize(
    ("factory", "executor"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code)),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code)),
    ],
)
def test_repl_seguridad_numpy_rechazado_mensaje_corto_sin_traceback(factory, executor, monkeypatch):
    monkeypatch.delenv("PCOBRA_DEBUG_RUNTIME", raising=False)
    monkeypatch.delenv("PCOBRA_DEBUG_TRACES", raising=False)

    cmd = factory()
    with pytest.raises(PermissionError) as excinfo:
        executor(cmd, 'usar "numpy"')

    mensaje = str(excinfo.value)
    assert "Importación no permitida en 'usar': 'numpy'. Es un módulo backend/no canónico y no forma parte de la API pública." in mensaje
    assert "Traceback" not in mensaje


@pytest.mark.parametrize(
    ("factory", "executor"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code)),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code)),
    ],
)
def test_repl_rechazo_numpy_es_persistente(factory, executor):
    cmd = factory()
    for _ in range(2):
        with pytest.raises(PermissionError) as excinfo:
            executor(cmd, 'usar "numpy"')
        mensaje = str(excinfo.value)
        assert "Importación no permitida en 'usar': 'numpy'. Es un módulo backend/no canónico y no forma parte de la API pública." in mensaje


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_usar_datos_longitud_imprimir_lista_y_variable(factory, executor, get_interp, capsys):
    cmd = factory()
    interp = get_interp(cmd)

    executor(cmd, 'usar "datos"')

    assert callable(interp.obtener_variable("elemento"))
    assert interp.obtener_variable("elemento")([10, 20, 30], 0) == 10

    interp.contextos[-1].define("ys", [10, 20, 30])
    assert interp.obtener_variable("elemento")(interp.obtener_variable("ys"), 1) == 20
    assert interp.obtener_variable("elemento")([1, 2, 3], 2) == 3

    interp.contextos[-1].define("xs", [1, 2, 3])
    executor(cmd, "imprimir(longitud(xs))")
    executor(cmd, "imprimir(longitud([1,2,3]))")

    salida = capsys.readouterr().out
    assert salida.count("3") >= 2
    assert interp.obtener_variable("longitud")([1, 2, 3]) == 3


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_aceptacion_positiva_usar_archivo_existe_readme(factory, executor, get_interp, capsys):
    cmd = factory()
    _ = get_interp(cmd)

    executor(cmd, 'usar "archivo"')
    executor(cmd, 'imprimir(existe("README.md"))')

    salida = capsys.readouterr().out.strip().splitlines()
    assert salida
    assert salida[-1].strip() in {"verdadero", "falso"}
    assert all("Uso de primitiva peligrosa" not in linea for linea in salida)


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_numpy_rechazo_no_deja_estado_parcial(factory, executor, get_interp):
    cmd = factory()
    interp = get_interp(cmd)
    estado_pre = dict(interp.contextos[-1].values)

    with pytest.raises(PermissionError, match=r"Importación no permitida en 'usar': 'numpy'.*usar_error\[modulo_fuera_catalogo_publico\]"):
        executor(cmd, 'usar "numpy"')

    assert dict(interp.contextos[-1].values) == estado_pre
    assert "numpy" not in interp.contextos[-1].values
    assert "numpy" not in interp.variables


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_usar_no_expone_simbolos_no_publicos(factory, executor, get_interp):
    cmd = factory()
    interp = get_interp(cmd)

    executor(cmd, 'usar "texto"')

    assert "normalizar_unicode" not in interp.contextos[-1].values
    with pytest.raises(NameError, match=r"^Variable no declarada: normalizar_unicode$"):
        interp.contextos[-1].get("normalizar_unicode")

def test_logs_usar_conflictos_formato_resumido_sin_diccionario_gigante(caplog, monkeypatch):
    modulo = ModuleType("texto")
    modulo.__all__ = ["A_snake", "a_snake"]
    modulo.A_snake = lambda texto: texto
    modulo.a_snake = lambda texto: texto
    modulo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/texto.py"
    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre: modulo)
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: modulo)
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo", lambda _nombre: modulo)
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: modulo)
    monkeypatch.delenv("PCOBRA_DEBUG_RUNTIME", raising=False)
    monkeypatch.delenv("PCOBRA_DEBUG_TRACES", raising=False)
    caplog.set_level(logging.INFO)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"texto": "texto"})

    interp.ejecutar_nodo(NodoUsar("texto"))

    assert callable(interp.obtener_variable("a_snake"))
    with pytest.raises(NameError):
        interp.obtener_variable("A_snake")

    eventos = [rec.message for rec in caplog.records if "USAR_SANITIZE_REJECTION_METRICS" in rec.message]
    assert eventos
    ultimo = eventos[-1]
    assert "rejection_metrics_by_codigo" in ultimo
    assert "conflicts=[" not in ultimo
    assert "{'symbol'" not in ultimo


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_contract_resuelve_usar_datos_y_tiempo(factory, executor, get_interp, monkeypatch):
    mod_datos = _modulo_datos_stub()
    mod_tiempo = _modulo_tiempo_stub()

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "datos":
            return mod_datos
        if nombre == "tiempo":
            return mod_tiempo
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))
    # monkeypatch.setattr(
    #     core_interpreter_module,
    #     "build_and_validate_usar_symbol_metadata",
    #     lambda module_name, symbol_name, callable_obj: {"origin_kind": "usar", "module": module_name, "symbol": symbol_name, "sanitized": True, "public_api": True, "callable": True, "backend_exposed": False},
    # )

    cmd = factory()
    interp = get_interp(cmd)

    executor(cmd, 'usar "datos"')
    executor(cmd, 'usar "tiempo"')

    assert interp.obtener_variable("longitud")([1, 2, 3]) == 3
    assert interp.obtener_variable("ahora")() == "2026-05-03T00:00:00"


def test_repl_contract_seguridad_usar_holobit_restringe_internals_y_saneamiento(monkeypatch):
    mod_holobit = _modulo_holobit_publico_stub()
    rel_path_holobit = cli_usar_loader.REPL_COBRA_MODULE_INTERNAL_PATH_MAP["holobit"]
    mod_holobit.__file__ = str(
        (
            Path(cli_usar_loader.__file__).resolve().parents[3]
            / rel_path_holobit
        ).resolve()
    )

    alias_map = {**REPL_COBRA_MODULE_MAP, "holobit": "holobit"}

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "holobit":
            return mod_holobit
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(alias_map)
    interp._repl_usar_alias_map = alias_map

    class _NodoUsar:
        modulo = "holobit"

    interp.ejecutar_usar(_NodoUsar())
    simbolos_holobit = set(mod_holobit.__all__)

    for simbolo in simbolos_holobit:
        assert simbolo in interp.contextos[-1].values

    _assert_contrato_simbolos_saneados(simbolos_holobit)
    assert simbolos_holobit == {"crear_holobit", "validar_holobit", "serializar_holobit", "deserializar_holobit", "proyectar", "transformar", "graficar", "combinar", "medir"}

    assert "Holobit" not in interp.contextos[-1].values
    assert "crear_holobit" in interp.contextos[-1].values
    assert "_to_sdk_holobit" not in interp.contextos[-1].values
    assert "holobit_sdk" not in interp.contextos[-1].values

    cmd = InteractiveCommand(InterpretadorCobra())
    cmd.interpretador.configurar_restriccion_usar_repl(alias_map)
    estado_pre = dict(cmd.interpretador.contextos[-1].values)
    with pytest.raises(
        PermissionError,
        match=r"Importación no permitida en 'usar': 'holobit_sdk'.*usar_error\[modulo_fuera_catalogo_publico\]",
    ):
        cmd.ejecutar_codigo('usar "holobit_sdk"')

    assert estado_pre == cmd.interpretador.contextos[-1].values


def test_repl_contract_seguridad_usar_atomico_holobit_y_datos_sin_overwrite(monkeypatch):
    mod_holobit = _modulo_holobit_publico_stub()
    rel_path_holobit = cli_usar_loader.REPL_COBRA_MODULE_INTERNAL_PATH_MAP["holobit"]
    mod_holobit.__file__ = str(
        (
            Path(cli_usar_loader.__file__).resolve().parents[3]
            / rel_path_holobit
        ).resolve()
    )

    mod_datos = _modulo_datos_stub()
    rel_path_datos = cli_usar_loader.REPL_COBRA_MODULE_INTERNAL_PATH_MAP["datos"]
    mod_datos.__file__ = str(
        (
            Path(cli_usar_loader.__file__).resolve().parents[3]
            / rel_path_datos
        ).resolve()
    )
    alias_map = {**REPL_COBRA_MODULE_MAP, "holobit": "holobit"}

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "holobit":
            return mod_holobit
        if nombre == "datos":
            return mod_datos
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(alias_map)
    interp._repl_usar_alias_map = alias_map

    interp.contextos[-1].define("graficar", lambda _hb: "ocupado")
    estado_pre_holobit = dict(interp.contextos[-1].values)
    with pytest.raises(NameError) as exc_holobit:
        class _NodoUsarHolobit:
            modulo = "holobit"

        interp.ejecutar_usar(_NodoUsarHolobit())

    mensaje_holobit = str(exc_holobit.value)
    assert "'code': 'symbol_collision'" in mensaje_holobit
    assert "'symbol': 'graficar'" in mensaje_holobit
    assert "'module': 'holobit'" in mensaje_holobit
    assert "'phase': 'preflight'" in mensaje_holobit
    assert estado_pre_holobit == interp.contextos[-1].values

    assert interp.obtener_variable("graficar")({}) == "ocupado"

    interp.contextos[-1].define("longitud", lambda _v: -1)
    estado_pre_datos = dict(interp.contextos[-1].values)
    with pytest.raises(NameError) as exc_datos:
        class _NodoUsarDatos:
            modulo = "datos"

        interp.ejecutar_usar(_NodoUsarDatos())

    mensaje_datos = str(exc_datos.value)
    assert "'code': 'symbol_collision'" in mensaje_datos
    assert "'symbol': 'longitud'" in mensaje_datos
    assert "'module': 'datos'" in mensaje_datos
    assert "'phase': 'preflight'" in mensaje_datos
    assert estado_pre_datos == interp.contextos[-1].values

    assert interp.obtener_variable("longitud")([]) == -1


def test_holobit_corelib_exporta_solo_simbolos_canonicos_publicos():
    import importlib.util
    from pathlib import Path

    ruta = Path("src/pcobra/corelibs/holobit.py").resolve()
    spec = importlib.util.spec_from_file_location("_holobit_corelib_blackbox", ruta)
    assert spec is not None and spec.loader is not None
    holobit_corelib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(holobit_corelib)

    assert set(holobit_corelib.__all__) == {
        "crear_holobit",
        "validar_holobit",
        "serializar_holobit",
        "deserializar_holobit",
        "proyectar",
        "transformar",
        "graficar",
        "combinar",
        "medir",
    }
    for simbolo in holobit_corelib.__all__:
        assert callable(getattr(holobit_corelib, simbolo))

    assert not hasattr(holobit_corelib, "__all__") or "Holobit" not in holobit_corelib.__all__
    assert "holobit_sdk" not in holobit_corelib.__all__
    assert "_to_sdk_holobit" not in holobit_corelib.__all__
    assert all("__" not in simbolo for simbolo in holobit_corelib.__all__)


@pytest.mark.parametrize("modulo", sorted(REPL_COBRA_MODULE_MAP.keys()))
def test_repl_contract_pipeline_completo_por_modulo_canonico(monkeypatch, tmp_path, modulo):
    mod = ModuleType(modulo)
    expected_symbols = []

    if modulo == "holobit":
        expected_symbols = [
            "crear_holobit",
            "validar_holobit",
            "serializar_holobit",
            "deserializar_holobit",
            "proyectar",
            "transformar",
            "graficar",
            "combinar",
            "medir",
        ]
        for nombre in expected_symbols:
            setattr(mod, nombre, lambda *args, _mod=modulo, _nombre=nombre, **kwargs: {"modulo": _mod, "simbolo": _nombre, "args": args, "kwargs": kwargs})
        monkeypatch.setattr("pcobra.corelibs.holobit._runtime_graficar", lambda _hb: "holobit-render")
    elif modulo == "numero":
        expected_symbols = ["es_finito", "signo"]
        setattr(mod, "es_finito", lambda valor: valor == valor and valor not in (float("inf"), float("-inf")))
        setattr(mod, "signo", lambda valor: -1 if valor < 0 else (1 if valor > 0 else 0))
    elif modulo == "texto":
        expected_symbols = ["mayusculas", "recortar", "repetir", "quitar_acentos"]
        setattr(mod, "mayusculas", lambda texto: str(texto).upper())
        setattr(mod, "recortar", lambda texto: str(texto).strip())
        setattr(mod, "repetir", lambda texto, veces=2: str(texto) * int(veces))
        setattr(mod, "quitar_acentos", lambda texto: str(texto).translate(str.maketrans("áéíóú", "aeiou")))
    elif modulo == "datos":
        expected_symbols = ["longitud", "elemento"]
        setattr(mod, "longitud", lambda valores: len(valores))
        setattr(mod, "elemento", lambda valores, indice: valores[indice])
    elif modulo == "logica":
        expected_symbols = ["conjuncion", "negacion"]
        setattr(mod, "conjuncion", lambda a, b: a and b)
        setattr(mod, "negacion", lambda a: not a)
    elif modulo == "tiempo":
        expected_symbols = ["ahora"]
        setattr(mod, "ahora", lambda: "2026-05-03T00:00:00")
    elif modulo == "archivo":
        expected_symbols = ["existe"]
        setattr(mod, "existe", lambda ruta: True)
    elif modulo == "sistema":
        expected_symbols = ["obtener_os", "ejecutar", "ejecutar_async", "ejecutar_stream", "obtener_env", "listar_dir", "directorio_actual"]
        setattr(mod, "obtener_os", lambda: "windows")
        setattr(mod, "ejecutar", lambda comando, permitidos=None: {"salida": "", "error": "", "codigo": 0})
        setattr(mod, "ejecutar_async", lambda comando, permitidos=None: asyncio.Future())
        setattr(mod, "ejecutar_stream", lambda comando, permitidos=None: [])
        setattr(mod, "obtener_env", lambda nombre: "valor")
        setattr(mod, "listar_dir", lambda ruta: [])
        setattr(mod, "directorio_actual", lambda: Path("."))
        monkeypatch.setattr("pcobra.corelibs.sistema._verificar_ruta", lambda exe_real, st_dev, st_ino: None)
        monkeypatch.setattr("pcobra.corelibs.sistema._resolver_ejecutable", lambda comando, permitidos: ([r"C:\\cobra\\mock.exe", *list(comando)[1:]], r"C:\\cobra\\mock.exe", 10, 1, 2))
        monkeypatch.setattr("pcobra.corelibs.sistema._verificar_descriptor", lambda *args: None)
        monkeypatch.setattr("os.close", lambda _fd: None)
        monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: type("Result", (object,), {"stdout": "", "stderr": "", "returncode": 0})())
    elif modulo == "red":
        expected_symbols = ["obtener_url", "enviar_post", "obtener_url_async", "enviar_post_async", "descargar_archivo", "obtener_json", "obtener_url_texto"]
        for nombre in expected_symbols:
            if nombre == "obtener_url":
                setattr(mod, nombre, lambda url, permitir_redirecciones=False: "")
            elif nombre == "enviar_post":
                setattr(mod, nombre, lambda url, datos, permitir_redirecciones=False: "")
            elif nombre == "obtener_url_async":
                setattr(mod, nombre, lambda url, permitir_redirecciones=False: "")
            elif nombre == "enviar_post_async":
                setattr(mod, nombre, lambda url, datos, permitir_redirecciones=False: "")
            elif nombre == "descargar_archivo":
                setattr(mod, nombre, lambda url, destino, permitir_redirecciones=False, crear_padres=True: Path(destino))
            elif nombre == "obtener_url_texto":
                setattr(mod, nombre, lambda url, permitir_redirecciones=False: "")
            elif nombre == "obtener_json":
                setattr(mod, nombre, lambda url, permitir_redirecciones=False: {})
        monkeypatch.setattr("pcobra.corelibs.red._validar_esquema", lambda url: None)
        monkeypatch.setattr("pcobra.corelibs.red._obtener_hosts_permitidos", lambda: {"example.com"})
        class _Response:
            status_code = 200
            url = "https://example.com"
            headers = {}
            encoding = "utf-8"

            def raise_for_status(self):
                return None

            def iter_content(self, chunk_size=8192):
                _ = chunk_size
                yield b"{}"

            def close(self):
                return None

        monkeypatch.setattr("requests.get", lambda *args, **kwargs: _Response())
        monkeypatch.setattr("requests.post", lambda *args, **kwargs: _Response())
        monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: type("Response", (object,), {"status_code": 200, "raise_for_status": lambda: None, "url": "http://example.com", "headers": {}, "iter_content": lambda chunk_size: [b""]})(), raising=False)
        monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: type("Response", (object,), {"status_code": 200, "raise_for_status": lambda: None, "url": "http://example.com", "headers": {}, "iter_content": lambda chunk_size: [b""]})(), raising=False)
    elif modulo == "asincrono":
        expected_symbols = ["grupo_tareas", "limitar_tiempo", "proteger_tarea", "ejecutar_en_hilo", "reintentar_async", "recolectar"]
        for nombre in expected_symbols:
            if nombre == "proteger_tarea":
                setattr(mod, nombre, lambda awaitable: asyncio.Future())
            elif nombre == "limitar_tiempo":
                setattr(mod, nombre, lambda segundos, mensaje=None: None)
            elif nombre == "ejecutar_en_hilo":
                setattr(mod, nombre, lambda funcion, *args, **kwargs: None)
            elif nombre == "recolectar":
                setattr(mod, nombre, lambda *corutinas, return_exceptions=False: [])
            elif nombre == "reintentar_async":
                setattr(mod, nombre, lambda funcion, intentos=3, excepciones=(Exception,), retardo_inicial=0.1, factor_backoff=2.0, max_retardo=None, jitter=None: asyncio.Future())
            elif nombre == "grupo_tareas":
                setattr(mod, nombre, lambda: None)
    else:
        # Para el resto del catálogo, reutilizar la API pública canónica
        # en lugar de mantener listas duplicadas y propensas a quedar obsoletas.
        modulo_real = importlib.import_module(f"pcobra.corelibs.{modulo}")
        expected_symbols = list(getattr(modulo_real, "__all__", ()))

        if not expected_symbols:
            raise AssertionError(
                f"El módulo canónico {modulo!r} no declara símbolos públicos en __all__"
            )

        for nombre in expected_symbols:
            setattr(mod, nombre, getattr(modulo_real, nombre))

    mod.__all__ = expected_symbols
    rel_path = cli_usar_loader.REPL_COBRA_MODULE_INTERNAL_PATH_MAP[modulo]
    mod.__file__ = str(
        (
            Path(cli_usar_loader.__file__).resolve().parents[3]
            / rel_path
        ).resolve()
    )

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == modulo:
            return mod
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(REPL_COBRA_MODULE_MAP)

    nodo_usar = type("_NodoUsar", (), {"modulo": modulo})()

    interp.ejecutar_usar(nodo_usar)
    for symbol in expected_symbols:
        assert symbol in interp.contextos[-1].values
        # Llamar a la función con argumentos ficticios si es necesario
        if modulo == "archivo" and symbol == "existe":
            interp.contextos[-1].values[symbol]("dummy_path")
        elif modulo == "datos" and symbol == "longitud":
            interp.contextos[-1].values[symbol]([])
        elif modulo == "datos" and symbol == "elemento":
            interp.contextos[-1].values[symbol]([1], 0)
        elif modulo == "holobit" and symbol == "crear_holobit":
            interp.contextos[-1].values[symbol](valores={})
        elif modulo == "holobit" and symbol == "validar_holobit":
            interp.contextos[-1].values[symbol]({})
        elif modulo == "holobit" and symbol == "serializar_holobit":
            interp.contextos[-1].values[symbol]({"tipo": "holobit", "valores": [1, 2, 3]})
        elif modulo == "holobit" and symbol == "deserializar_holobit":
            interp.contextos[-1].values[symbol]('{"tipo":"holobit","valores":[1,2,3]}')
        elif modulo == "holobit" and symbol == "proyectar":
            interp.contextos[-1].values[symbol]({"tipo": "holobit", "valores": [1, 2, 3]}, "2d")
        elif modulo == "holobit" and symbol == "transformar":
            interp.contextos[-1].values[symbol]({"tipo": "holobit", "valores": [1, 2, 3]}, "rotar", "x", 90)
        elif modulo == "holobit" and symbol == "graficar":
            interp.contextos[-1].values[symbol]({"tipo": "holobit", "valores": [1, 2, 3]})
        elif modulo == "holobit" and symbol == "combinar":
            interp.contextos[-1].values[symbol]({"tipo": "holobit", "valores": [1, 2]}, {"tipo": "holobit", "valores": [3, 4]})
        elif modulo == "holobit" and symbol == "medir":
            interp.contextos[-1].values[symbol]({"tipo": "holobit", "valores": [1, 2, 3]})
        elif modulo == "logica" and symbol == "conjuncion":
            interp.contextos[-1].values[symbol](True, False)
        elif modulo == "logica" and symbol == "negacion":
            interp.contextos[-1].values[symbol](True)
        elif modulo == "numero" and symbol == "es_finito":
            interp.contextos[-1].values[symbol](10)
        elif modulo == "numero" and symbol == "signo":
            interp.contextos[-1].values[symbol](-1)
        elif modulo == "texto" and symbol == "mayusculas":
            interp.contextos[-1].values[symbol]("cobra")
        elif modulo == "texto" and symbol == "recortar":
            interp.contextos[-1].values[symbol](" cobra ")
        elif modulo == "texto" and symbol == "repetir":
            interp.contextos[-1].values[symbol]("co", 2)
        elif modulo == "texto" and symbol == "quitar_acentos":
            interp.contextos[-1].values[symbol]("canción")
        elif modulo == "sistema" and symbol == "ejecutar":
            interp.contextos[-1].values[symbol](["cobra"], permitidos=[r"C:\\cobra\\mock.exe"])
        elif modulo == "sistema" and symbol == "ejecutar_async":
            interp.contextos[-1].values[symbol](["cobra"], permitidos=[r"C:\\cobra\\mock.exe"])
        elif modulo == "sistema" and symbol == "ejecutar_stream":
            interp.contextos[-1].values[symbol](["cobra"], permitidos=[r"C:\\cobra\\mock.exe"])
        elif modulo == "sistema" and symbol == "obtener_env":
            interp.contextos[-1].values[symbol]("PATH")
        elif modulo == "sistema" and symbol == "listar_dir":
            interp.contextos[-1].values[symbol](".")
        elif modulo == "red" and symbol == "obtener_url":
            interp.contextos[-1].values[symbol]("https://example.com")
        elif modulo == "red" and symbol == "enviar_post":
            interp.contextos[-1].values[symbol]("https://example.com", {})
        elif modulo == "red" and symbol == "obtener_url_async":
            interp.contextos[-1].values[symbol]("http://example.com")
        elif modulo == "red" and symbol == "enviar_post_async":
            interp.contextos[-1].values[symbol]("http://example.com", {})
        elif modulo == "red" and symbol == "descargar_archivo":
            interp.contextos[-1].values[symbol]("http://example.com", "dummy_path")
        elif modulo == "red" and symbol == "obtener_url_texto":
            interp.contextos[-1].values[symbol]("http://example.com")
        elif modulo == "red" and symbol == "obtener_json":
            interp.contextos[-1].values[symbol]("http://example.com")
        elif modulo == "asincrono" and symbol == "proteger_tarea":
            interp.contextos[-1].values[symbol](asyncio.Future())
        elif modulo == "asincrono" and symbol == "limitar_tiempo":
            interp.contextos[-1].values[symbol](1)
        elif modulo == "asincrono" and symbol == "ejecutar_en_hilo":
            interp.contextos[-1].values[symbol](lambda: None)
        elif modulo == "asincrono" and symbol == "recolectar":
            interp.contextos[-1].values[symbol]()
        elif modulo == "asincrono" and symbol == "carrera":
            interp.contextos[-1].values[symbol](asyncio.Future())
        elif modulo == "asincrono" and symbol == "primero_exitoso":
            interp.contextos[-1].values[symbol](asyncio.Future())
        elif modulo == "asincrono" and symbol == "esperar_timeout":
            interp.contextos[-1].values[symbol](asyncio.Future(), 1)
        elif modulo == "asincrono" and symbol == "reintentar_async":
            interp.contextos[-1].values[symbol](lambda: asyncio.Future())
        elif modulo == "asincrono" and symbol == "grupo_tareas":
            interp.contextos[-1].values[symbol]()
        elif modulo == "tiempo" and symbol == "ahora":
            interp.contextos[-1].values[symbol]()
        elif modulo == "argumentos" and symbol == "contiene_flag":
            interp.contextos[-1].values[symbol]("debug", ["--debug"])
        elif modulo == "argumentos" and symbol == "obtener_opcion":
            interp.contextos[-1].values[symbol]("salida", ["--salida", "out"])
        elif modulo == "compresion" and symbol == "crear_zip":
            fuente = tmp_path / "fuente.txt"
            fuente.write_text("cobra", encoding="utf-8")
            interp.contextos[-1].values[symbol](tmp_path / "archivo.zip", [fuente])
        elif modulo == "compresion" and symbol == "extraer_zip":
            fuente = tmp_path / "fuente.txt"
            fuente.write_text("cobra", encoding="utf-8")
            zip_path = tmp_path / "archivo.zip"
            interp.contextos[-1].values["crear_zip"](zip_path, [fuente])
            interp.contextos[-1].values[symbol](zip_path, tmp_path / "extraido")
        elif modulo == "compresion" and symbol == "listar_zip":
            fuente = tmp_path / "fuente.txt"
            fuente.write_text("cobra", encoding="utf-8")
            zip_path = tmp_path / "archivo.zip"
            interp.contextos[-1].values["crear_zip"](zip_path, [fuente])
            interp.contextos[-1].values[symbol](zip_path)
        elif modulo == "configuracion" and symbol == "leer_toml":
            config = tmp_path / "cobra.toml"
            config.write_text("[proyecto]\nnombre = 'cobra'\n", encoding="utf-8")
            interp.contextos[-1].values[symbol](config)
        elif modulo == "configuracion" and symbol == "leer_ini":
            config = tmp_path / "cobra.ini"
            config.write_text("[proyecto]\nnombre = cobra\n", encoding="utf-8")
            interp.contextos[-1].values[symbol](config)
        elif modulo == "configuracion" and symbol == "leer_configuracion":
            config = tmp_path / "cobra.toml"
            config.write_text("[proyecto]\nnombre = 'cobra'\n", encoding="utf-8")
            interp.contextos[-1].values[symbol](config)
        elif modulo == "cripto" and symbol in {"sha256", "sha512"}:
            interp.contextos[-1].values[symbol]("cobra")
        elif modulo == "cripto" and symbol == "comparar_seguro":
            interp.contextos[-1].values[symbol]("cobra", "cobra")
        elif modulo == "proceso" and symbol in {"ejecutar", "capturar"}:
            interp.contextos[-1].values[symbol](["python", "--version"])
        elif modulo == "proceso" and symbol == "codigo_salida":
            interp.contextos[-1].values[symbol]({"codigo": 0})
        elif modulo == "proceso" and symbol == "salida":
            interp.contextos[-1].values[symbol]({"salida": "cobra"})
        elif modulo == "proceso" and symbol == "errores":
            interp.contextos[-1].values[symbol]({"error": ""})
        elif modulo == "pruebas" and symbol == "igual":
            interp.contextos[-1].values[symbol](1, 1)
        elif modulo == "pruebas" and symbol == "verdadero":
            interp.contextos[-1].values[symbol](True)
        elif modulo == "pruebas" and symbol == "falso":
            interp.contextos[-1].values[symbol](False)
        elif modulo == "pruebas" and symbol == "contiene":
            interp.contextos[-1].values[symbol]([1], 1)
        elif modulo == "pruebas" and symbol == "lanza_error":
            interp.contextos[-1].values[symbol](lambda: (_ for _ in ()).throw(ValueError()), ValueError)
        elif modulo == "regex" and symbol in {"buscar", "coincidir", "dividir", "encontrar_todos"}:
            interp.contextos[-1].values[symbol]("co", "cobra")
        elif modulo == "regex" and symbol == "reemplazar":
            interp.contextos[-1].values[symbol]("co", "Co", "cobra")
        elif modulo == "registro" and symbol in {"debug", "info", "aviso", "error"}:
            interp.contextos[-1].values[symbol]("mensaje")
        elif modulo == "ruta" and symbol == "unir":
            interp.contextos[-1].values[symbol]("cobra", "mod")
        elif modulo == "ruta" and symbol in {"normalizar", "nombre", "extension", "padre", "existe", "es_absoluta", "absoluta", "relativa"}:
            interp.contextos[-1].values[symbol]("cobra/mod.co")
        elif modulo == "serializacion" and symbol == "codificar_json":
            interp.contextos[-1].values[symbol]({"cobra": True})
        elif modulo == "serializacion" and symbol == "decodificar_json":
            interp.contextos[-1].values[symbol]('{"cobra": true}')
        elif modulo == "serializacion" and symbol == "leer_json":
            ruta_json = tmp_path / "datos.json"
            ruta_json.write_text('{"cobra": true}', encoding="utf-8")
            interp.contextos[-1].values[symbol](ruta_json)
        elif modulo == "serializacion" and symbol == "escribir_json":
            interp.contextos[-1].values[symbol](tmp_path / "datos.json", {"cobra": True})
        elif modulo == "serializacion" and symbol == "leer_csv":
            ruta_csv = tmp_path / "datos.csv"
            ruta_csv.write_text("nombre\ncobra\n", encoding="utf-8")
            interp.contextos[-1].values[symbol](ruta_csv)
        elif modulo == "serializacion" and symbol == "escribir_csv":
            interp.contextos[-1].values[symbol](tmp_path / "datos.csv", [{"nombre": "cobra"}])
        elif modulo == "temporal" and symbol == "limpiar":
            temporal = tmp_path / "temporal.txt"
            temporal.write_text("cobra", encoding="utf-8")
            interp.contextos[-1].values[symbol](temporal)
        else:
            # Para funciones sin argumentos o con argumentos por defecto
            interp.contextos[-1].values[symbol]()


def test_repl_contract_colision_warn_alias_required_estructurada(monkeypatch):
    mod_numero = _modulo_numero_multi_export_stub()

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: mod_numero)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(REPL_COBRA_MODULE_MAP)
    interp.configurar_politica_colision_usar("warn_alias_required")
    interp.contextos[-1].define("es_finito", lambda _valor: "ocupado")

    class _NodoUsar:
        modulo = "numero"

    with pytest.raises(NameError, match=r"No se puede usar 'numero': hay conflicto de símbolos en el contexto actual\. Símbolo conflictivo: es_finito\."):
        interp.ejecutar_usar(_NodoUsar())



@pytest.mark.parametrize(
    "nombre",
    ["", "   ", "../numero", "..\\numero", "corelibs/numero", "standard_library/texto", "pcobra", "holobit_sdk"],
)
def test_repl_rechaza_nombres_invalidos_o_maliciosos(nombre):
    cmd = InteractiveCommand(InterpretadorCobra())
    estado_pre = dict(cmd.interpretador.contextos[-1].values)

    with pytest.raises((ValueError, PermissionError), match=r"(inválido|no permitid|externo|modulo_fuera_catalogo_publico|Nombre de módulo vacío en 'usar')"):
        cmd.ejecutar_codigo(f'usar "{nombre}"')

    assert estado_pre == cmd.interpretador.contextos[-1].values


def test_repl_rechaza_alias_legacy_fuera_contrato():
    cmd = InteractiveCommand(InterpretadorCobra())
    estado_pre = dict(cmd.interpretador.contextos[-1].values)

    with pytest.raises(PermissionError, match=r"solo alias oficiales Cobra|nombres canónicos exactos|no permitid|modulo_fuera_catalogo_publico"):
        cmd.ejecutar_codigo('usar "node-fetch"')

    assert estado_pre == cmd.interpretador.contextos[-1].values


@pytest.mark.parametrize(
    ("factory", "executor"),
    [
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code)),
    ],
)
def test_repl_usar_datos_longitud_salida_exacta(factory, executor, monkeypatch, capsys):
    mod_datos = _modulo_datos_stub()

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "datos":
            return mod_datos
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    cmd = factory()
    executor(cmd, 'usar "datos"')
    executor(cmd, "imprimir(longitud([1,2,3]))")

    lineas = [linea.strip() for linea in capsys.readouterr().out.splitlines() if linea.strip()]
    assert lineas == ["3"]

    simbolos = set((cmd.interpretador if isinstance(cmd, InteractiveCommand) else cmd._delegate.interpretador).contextos[-1].values.keys())
    assert "longitud" in simbolos
    assert "_backend" not in simbolos
    assert "module_object" not in simbolos


def test_repl_usar_texto_expone_funciones_objetivo_y_mantiene_comunes(monkeypatch):
    mod_texto = ModuleType("texto")
    mod_texto.__all__ = ["recortar", "repetir", "quitar_acentos", "prefijo_comun", "sufijo_comun"]
    mod_texto.recortar = lambda texto: str(texto).strip()
    mod_texto.repetir = lambda texto, veces: str(texto) * int(veces)
    mod_texto.quitar_acentos = lambda texto: str(texto).translate(str.maketrans("áéíóú", "aeiou"))
    mod_texto.prefijo_comun = lambda a, b: next((str(a)[:i] for i in range(min(len(str(a)), len(str(b))), -1, -1) if str(a)[:i] == str(b)[:i]), "")
    mod_texto.sufijo_comun = lambda a, b: next((str(a)[len(str(a))-i:] for i in range(min(len(str(a)), len(str(b))), -1, -1) if str(a)[len(str(a))-i:] == str(b)[len(str(b))-i:]), "")
    mod_texto.__file__ = "/workspace/pCobra/src/pcobra/corelibs/texto.py"

    monkeypatch.setattr(
        core_usar_loader,
        "obtener_modulo_cobra_oficial",
        lambda nombre: mod_texto if nombre == "texto" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )

    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "texto"')

    for simbolo in ("recortar", "repetir", "quitar_acentos", "prefijo_comun", "sufijo_comun"):
        assert callable(cmd._delegate.interpretador.obtener_variable(simbolo))


def test_repl_usar_numero_es_finito_y_signo_siguen_operativos(monkeypatch, capsys):
    mod_numero = ModuleType("numero")
    mod_numero.__all__ = ["es_finito", "signo"]
    mod_numero.es_finito = lambda valor: valor == valor and valor not in (float("inf"), float("-inf"))
    mod_numero.signo = lambda valor: -1 if valor < 0 else (1 if valor > 0 else 0)
    mod_numero.__file__ = "/workspace/pCobra/src/pcobra/corelibs/numero.py"

    monkeypatch.setattr(
        core_usar_loader,
        "obtener_modulo_cobra_oficial",
        lambda nombre: mod_numero if nombre == "numero" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )

    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "numero"')
    cmd._ejecutar_en_modo_normal("imprimir(es_finito(10))")
    cmd._ejecutar_en_modo_normal("imprimir(signo(0 - 5))")

    lineas = [linea.strip() for linea in capsys.readouterr().out.splitlines() if linea.strip() and not linea.startswith("WARNING:")]
    assert lineas == ["verdadero", "-1"]



def test_repl_usar_modulos_numero_logica_tiempo_y_datos_con_epoch_rango(capsys):
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "numero"')
    cmd._ejecutar_en_modo_normal('usar "logica"')
    cmd._ejecutar_en_modo_normal('usar "tiempo"')
    cmd._ejecutar_en_modo_normal("func doble(n):\n    retorno n * 2\nfin")

    cmd._ejecutar_en_modo_normal('imprimir(es_finito(5))')
    cmd._ejecutar_en_modo_normal('imprimir(signo(0-5))')
    cmd._ejecutar_en_modo_normal('imprimir(conjuncion(verdadero, negacion(falso)))')
    cmd._ejecutar_en_modo_normal('imprimir(epoch())')
    cmd._ejecutar_en_modo_normal('usar "datos"')
    cmd._ejecutar_en_modo_normal('imprimir(longitud("cobra"))')
    cmd._ejecutar_en_modo_normal('imprimir(doble(signo(0-3)))')

    lineas = [linea.strip() for linea in capsys.readouterr().out.splitlines() if linea.strip()]
    assert 'verdadero' in lineas
    assert '-1' in lineas
    assert any(l in ('true', 'verdadero') for l in lineas)
    epoch_value = next(
        float(l)
        for l in lineas
        if l.replace('.', '', 1).lstrip('-').isdigit() and abs(float(l)) > 10**8
    )
    assert 946684800 <= epoch_value <= 4102444800
    assert '5' in lineas
    assert '-2' in lineas


def test_repl_contrato_cli_superficie_publica_y_error_corto_numpy(capsys):
    cmd = ReplCommandV2()

    cmd._ejecutar_en_modo_normal('usar "numero"')
    cmd._ejecutar_en_modo_normal("imprimir(es_finito(10))")
    cmd._ejecutar_en_modo_normal("imprimir(signo(0-5))")

    cmd._ejecutar_en_modo_normal('usar "texto"')
    cmd._ejecutar_en_modo_normal('imprimir(mayusculas("cobra"))')
    cmd._ejecutar_en_modo_normal('imprimir(recortar(" cobra "))')
    cmd._ejecutar_en_modo_normal('imprimir(repetir("co", 2))')
    cmd._ejecutar_en_modo_normal('imprimir(quitar_acentos("canción"))')

    cmd._ejecutar_en_modo_normal('usar "logica"')
    cmd._ejecutar_en_modo_normal("imprimir(conjuncion(verdadero, falso))")
    cmd._ejecutar_en_modo_normal("imprimir(negacion(falso))")

    cmd._ejecutar_en_modo_normal('usar "tiempo"')
    cmd._ejecutar_en_modo_normal("imprimir(epoch())")

    cmd._ejecutar_en_modo_normal('usar "datos"')
    cmd._ejecutar_en_modo_normal('imprimir(longitud("cobra"))')

    lineas = [linea.strip() for linea in capsys.readouterr().out.splitlines() if linea.strip()]
    assert "verdadero" in lineas
    assert "-1" in lineas
    assert "COBRA" in lineas
    assert "cobra" in lineas
    assert "coco" in lineas
    assert "cancion" in lineas
    assert "falso" in lineas
    assert lineas[-1] == "5"

    epoch_value = next(float(v) for v in lineas if v.replace(".", "", 1).isdigit() and float(v) >= 946684800)
    assert 946684800 <= epoch_value <= 4102444800

    simbolos = set(cmd._delegate.interpretador.contextos[-1].values)
    assert "normalizar_unicode" not in simbolos
    assert "_backend" not in simbolos
    assert "__all__" not in simbolos

    with pytest.raises(PermissionError, match=r"Importación no permitida en 'usar': 'numpy'.*usar_error\[modulo_fuera_catalogo_publico\]"):
        cmd._ejecutar_en_modo_normal('usar "numpy"')
    salida_error = capsys.readouterr().out
    assert "Traceback" not in salida_error


def test_repl_texto_aceptacion_mayusculas_recortar_repetir_quitar_acentos(capsys):
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "texto"')
    interp = cmd._delegate.interpretador

    assert interp.obtener_variable('mayusculas')('cobra') == 'COBRA'
    assert interp.obtener_variable('recortar')('  Cobra  ') == 'Cobra'
    assert interp.obtener_variable('repetir')('ja', 3) == 'jajaja'
    assert interp.obtener_variable('quitar_acentos')('canción') == 'cancion'
    assert interp.obtener_variable('prefijo_comun')('cobra', 'cobre') == 'cobr'
    assert interp.obtener_variable('sufijo_comun')('programacion', 'nacion') == 'acion'
    assert interp.obtener_variable('reemplazar')('cobra', 'co', 'CO') == 'CObra'
    assert interp.obtener_variable('quitar_acentos')('pingüino') == 'pinguino'

def test_repl_datos_longitud_y_agregar_si_disponible():
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "datos"')
    interp = cmd._delegate.interpretador

    assert interp.obtener_variable('longitud')('ab') == 2
    if 'agregar' in interp.contextos[-1].values:
        resultado = interp.obtener_variable('agregar')([], {'id': 3})
        assert resultado is not None



def test_repl_archivo_existe_emitir_booleano_sin_primitiva_peligrosa():
    cmd = ReplCommandV2()

    cmd._ejecutar_en_modo_normal('usar "archivo"')
    existe = cmd._delegate.interpretador.obtener_variable('existe')

    assert isinstance(existe('README.md'), bool)


def test_repl_archivo_existe_bloquea_traversal_relativo_con_error_controlado():
    cmd = ReplCommandV2()

    cmd._ejecutar_en_modo_normal('usar "archivo"')
    existe = cmd._delegate.interpretador.obtener_variable('existe')

    assert existe('../archivo_fuera_del_proyecto') is False


def test_repl_archivo_existe_bloquea_ruta_absoluta_con_error_controlado():
    cmd = ReplCommandV2()

    cmd._ejecutar_en_modo_normal('usar "archivo"')
    existe = cmd._delegate.interpretador.obtener_variable('existe')

    assert existe('/ruta/absoluta/sensible') is False


def test_repl_archivo_existe_bloquea_ruta_absoluta_windows_con_error_controlado():
    cmd = ReplCommandV2()

    cmd._ejecutar_en_modo_normal('usar "archivo"')
    existe = cmd._delegate.interpretador.obtener_variable('existe')

    assert existe(r'C:\\ruta\\absoluta\\sensible') is False





def test_repl_archivo_invocacion_cruda_sin_usar_permanece_bloqueada():
    cmd = ReplCommandV2()

    with pytest.raises(Exception, match='Uso de primitiva peligrosa'):
        cmd._ejecutar_en_modo_normal('imprimir(existe("README.md"))')

def test_repl_archivo_invocacion_directa_permitida_tras_usar_sin_traceback(capsys):
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "archivo"')

    cmd._ejecutar_en_modo_normal('imprimir(existe("README.md"))')

    salida = capsys.readouterr().out.strip()
    lineas = [linea.strip() for linea in salida.splitlines() if linea.strip()]
    assert 'Traceback' not in salida
    assert lineas[-1] in {'verdadero', 'falso'}
    assert len(lineas) <= 2


def test_repl_archivo_hardening_no_expone_backend_crudo():
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "archivo"')

    with pytest.raises(NameError):
        cmd._delegate.interpretador.obtener_variable('_backend')


def test_repl_usar_archivo_requiere_cadena_entre_comillas():
    cmd = ReplCommandV2()
    with pytest.raises(Exception, match=r"Se esperaba una ruta de módulo entre comillas"):
        cmd._ejecutar_en_modo_normal("usar archivo")



def test_repl_usar_idempotente_y_conflicto_real(monkeypatch):
    mod_numero = _modulo_numero_stub()
    monkeypatch.setattr(
        core_usar_loader,
        'obtener_modulo',
        lambda nombre: mod_numero if nombre == 'numero' else (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )
    monkeypatch.setattr(
        core_usar_loader,
        'obtener_modulo_cobra_oficial',
        lambda nombre: mod_numero if nombre == 'numero' else (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )
    monkeypatch.setattr(
        cli_usar_loader,
        'obtener_modulo',
        lambda nombre: mod_numero if nombre == 'numero' else (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )
    monkeypatch.setattr(
        cli_usar_loader,
        'obtener_modulo_cobra_oficial',
        lambda nombre: mod_numero if nombre == 'numero' else (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )

    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "numero"')
    estado_1 = dict(cmd._delegate.interpretador.contextos[-1].values)
    cmd._ejecutar_en_modo_normal('usar "numero"')
    assert estado_1 == cmd._delegate.interpretador.contextos[-1].values

def test_repl_ux_error_salida_corta_vs_debug(capsys, caplog):
    cmd = ReplCommandV2()
    with pytest.raises(Exception):
        cmd._ejecutar_en_modo_normal('imprimir(variable_inexistente)')
    salida_normal = capsys.readouterr().out
    assert 'Traceback' not in salida_normal

    cmd_debug = ReplCommandV2()
    cmd_debug._delegate._debug_mode = True
    with pytest.raises(Exception):
        cmd_debug._ejecutar_en_modo_normal('imprimir(variable_inexistente)')
    _ = capsys.readouterr().out
    assert all('Traceback' not in r.message for r in caplog.records if r.levelname != 'DEBUG')



def test_no_regresion_seguridad_usar_numpy_error_corto_sin_traceback(capsys):
    cmd = ReplCommandV2()
    with pytest.raises(PermissionError, match=r"Importación no permitida en 'usar': 'numpy'.*usar_error\[modulo_fuera_catalogo_publico\]"):
        cmd._ejecutar_en_modo_normal('usar "numpy"')

    salida = capsys.readouterr().out
    assert 'Traceback' not in salida


def test_repl_no_expone_simbolos_no_publicos_modulos_estandar():
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "texto"')
    cmd._ejecutar_en_modo_normal('usar "numero"')

    simbolos = set(cmd._delegate.interpretador.contextos[-1].values)
    assert '_backend' not in simbolos
    assert '_impl' not in simbolos
    assert '__all__' not in simbolos

def test_no_regresion_seguridad_usar_numpy_fuera_catalogo_publico():
    cmd = ReplCommandV2()
    with pytest.raises(PermissionError, match=r"Importación no permitida en 'usar': 'numpy'.*usar_error\[modulo_fuera_catalogo_publico\]"):
        cmd._ejecutar_en_modo_normal('usar "numpy"')


def test_repl_usar_numpy_error_explicito_corto_sin_traceback_en_modo_normal(capsys):
    cmd = ReplCommandV2()
    with pytest.raises(PermissionError) as excinfo:
        cmd._ejecutar_en_modo_normal('usar "numpy"')

    mensaje = str(excinfo.value)
    assert "Traceback" not in mensaje
    assert "detalle=" not in mensaje
    assert len(mensaje) < 220
    assert "Importación no permitida en 'usar': 'numpy'. Es un módulo backend/no canónico y no forma parte de la API pública. Módulos permitidos: numero, texto, datos, logica, asincrono, sistema, archivo, tiempo, red, holobit." in mensaje

    salida = capsys.readouterr().out
    assert "Traceback" not in salida


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_regresion_metadata_usar_none_pre_auditoria(factory, executor, get_interp, capsys, monkeypatch):
    """regresion_metadata_usar_none_pre_auditoria"""
    mod_datos = _modulo_datos_stub()
    mod_numero = _modulo_numero_stub()
    mod_archivo = ModuleType("archivo")
    mod_archivo.__all__ = ["existe"]
    mod_archivo.existe = lambda _ruta: True
    mod_archivo.__file__ = "/workspace/pCobra/src/pcobra/corelibs/archivo.py"

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "datos":
            return mod_datos
        if nombre == "numero":
            return mod_numero
        if nombre == "archivo":
            return mod_archivo
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo", lambda nombre: _resolver_modulo(nombre))
    monkeypatch.setattr(cli_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    cmd = factory()
    interp = get_interp(cmd)

    assert isinstance(interp._validador._metadata_simbolos_usar, dict)

    executor(cmd, "var xs = [1, 2, 3]")

    executor(cmd, 'usar "datos"')
    metadata_longitud = interp._validador._metadata_simbolos_usar.get("longitud")
    if not isinstance(metadata_longitud, dict):
        metadata_longitud = interp._usar_symbol_metadata.get("longitud")
    assert isinstance(metadata_longitud, dict)
    assert metadata_longitud["origin_kind"] == "usar"
    assert metadata_longitud["module"] == "datos"
    assert metadata_longitud["symbol"] == "longitud"
    assert metadata_longitud["sanitized"] is True
    assert metadata_longitud["public_api"] is True
    assert metadata_longitud["backend_exposed"] is False
    assert metadata_longitud["callable"] is True

    executor(cmd, "imprimir(longitud(xs))")
    executor(cmd, "imprimir(longitud([1, 2, 3]))")

    salida_datos = capsys.readouterr()
    assert "invalid_container" not in salida_datos.out
    assert "NoneType" not in salida_datos.out
    assert "invalid_container" not in salida_datos.err
    assert "NoneType" not in salida_datos.err
    lineas_datos = [linea.strip() for linea in salida_datos.out.splitlines() if linea.strip()]
    assert lineas_datos.count("3") >= 2

    executor(cmd, 'usar "numero"')
    assert callable(interp.obtener_variable("es_finito"))
    executor(cmd, "imprimir(es_finito(10))")
    salida_numero = capsys.readouterr()
    combinado_numero = f"{salida_numero.out}\n{salida_numero.err}"
    assert "invalid_container" not in combinado_numero
    assert "NoneType" not in combinado_numero
    lineas_numero = [linea.strip() for linea in salida_numero.out.splitlines() if linea.strip()]
    assert lineas_numero and lineas_numero[-1] == "verdadero"

    executor(cmd, 'usar "archivo"')
    executor(cmd, 'imprimir(existe("README.md"))')
    salida_archivo = capsys.readouterr()
    combinado_archivo = f"{salida_archivo.out}\n{salida_archivo.err}"
    assert "invalid_container" not in combinado_archivo
    assert "_metadata_simbolos_usar" not in combinado_archivo
    assert "NoneType" not in combinado_archivo

    lineas_archivo = [linea.strip() for linea in salida_archivo.out.splitlines() if linea.strip()]
    ultimo = lineas_archivo[-1] if lineas_archivo else ""
    assert (
        ultimo in {"verdadero", "falso"}
        or "Uso de primitiva peligrosa" in combinado_archivo
    )

    with pytest.raises(PermissionError, match=r"Importación no permitida en 'usar': 'numpy'.*usar_error\[modulo_fuera_catalogo_publico\]"):
        executor(cmd, 'usar "numpy"')


def test_repl_usar_datos_numero_archivo_contrato_basico_sin_errores_metadata(capsys):
    cmd = ReplCommandV2()

    cmd._ejecutar_en_modo_normal('usar "datos"')
    cmd._ejecutar_en_modo_normal('var xs = [1, 2, 3]')
    cmd._ejecutar_en_modo_normal('imprimir(longitud(xs))')

    cmd._ejecutar_en_modo_normal('usar "numero"')
    cmd._ejecutar_en_modo_normal('imprimir(es_finito(10))')

    cmd._ejecutar_en_modo_normal('usar "archivo"')
    cmd._ejecutar_en_modo_normal('imprimir(existe("README.md"))')

    salida = capsys.readouterr().out
    assert 'Traceback' not in salida
    assert 'metadata' not in salida.lower()
    assert '3' in salida
    assert 'verdadero' in salida or 'falso' in salida
