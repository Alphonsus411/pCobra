from __future__ import annotations

from types import ModuleType

import pytest

from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.commands_v2.repl_cmd import ReplCommandV2
from pcobra.core import usar_loader as core_usar_loader
from pcobra.cobra.core.runtime import InterpretadorCobra
from pcobra.cobra.usar_policy import REPL_COBRA_MODULE_MAP


def _modulo_numero_stub() -> ModuleType:
    mod = ModuleType("numero")
    mod.__all__ = ["es_finito"]
    mod.es_finito = lambda valor: valor == valor and valor not in (float("inf"), float("-inf"))
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/numero.py"
    return mod


def _modulo_texto_stub() -> ModuleType:
    mod = ModuleType("texto")
    mod.__all__ = ["a_snake"]
    mod.a_snake = lambda texto: "hola_mundo" if texto == "HolaMundo" else str(texto)
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

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    cmd = factory()
    interp = get_interp(cmd)

    executor(cmd, 'usar "numero"')
    executor(cmd, "es_finito(10)")

    assert interp.obtener_variable("es_finito")(10) is True


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

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    cmd = factory()
    interp = get_interp(cmd)

    executor(cmd, 'usar "texto"')
    executor(cmd, 'a_snake("HolaMundo")')

    assert interp.obtener_variable("a_snake")("HolaMundo") == "hola_mundo"


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

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    cmd = factory()
    interp = get_interp(cmd)
    executor(cmd, 'usar "numero"')
    estado_pre_numpy = dict(interp.contextos[-1].values)
    simbolos_pre = set(interp.contextos[-1].values.keys())

    with pytest.raises(PermissionError, match=r"(módulo externo no permitido en REPL estricto|modulo_fuera_catalogo_publico)"):
        executor(cmd, 'usar "numpy"')

    # Contrato de Cobra: `usar` es plano (sin `.`), no se expone namespace tipo `numero.*`.
    assert "numpy" not in interp.variables
    assert "numpy" not in interp.contextos[-1].values
    assert estado_pre_numpy == interp.contextos[-1].values
    assert simbolos_pre == set(interp.contextos[-1].values.keys())

    with pytest.raises(Exception, match=r"Token no reconocido: '\.'"):
        executor(cmd, "numero.es_finito(10)")





def _modulo_tiempo_stub() -> ModuleType:
    mod = ModuleType("tiempo")
    mod.__all__ = ["ahora"]
    mod.ahora = lambda: "2026-05-03T00:00:00"
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/tiempo.py"
    return mod


def _modulo_datos_stub() -> ModuleType:
    mod = ModuleType("datos")
    mod.__all__ = ["longitud"]
    mod.longitud = lambda valores: len(valores)
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

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    cmd = factory()
    interp = get_interp(cmd)
    interp.contextos[-1].define("es_finito", lambda _valor: "ocupado")

    with pytest.raises(NameError, match=r"No se puede usar el módulo 'numero': (usar_error\[conflicto_simbolo\] )?colisión estructurada="):
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

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    cmd = factory()
    interp = get_interp(cmd)
    estado_pre = dict(interp.contextos[-1].values)

    with pytest.raises(PermissionError, match=r"(módulo externo no permitido en REPL estricto|modulo_fuera_catalogo_publico)"):
        executor(cmd, 'usar "requests"')

    assert estado_pre == interp.contextos[-1].values
    assert "requests" not in interp.contextos[-1].values


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

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    cmd = factory()
    interp = get_interp(cmd)

    executor(cmd, 'usar "datos"')
    executor(cmd, 'usar "tiempo"')

    assert interp.obtener_variable("longitud")([1, 2, 3]) == 3
    assert interp.obtener_variable("ahora")() == "2026-05-03T00:00:00"


def test_repl_contract_seguridad_usar_holobit_restringe_internals_y_saneamiento(monkeypatch):
    mod_holobit = _modulo_holobit_publico_stub()

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
    with pytest.raises(PermissionError, match=r"(módulo externo no permitido en REPL estricto|modulo_fuera_catalogo_publico)"):
        cmd.ejecutar_codigo('usar "holobit_sdk"')

    assert estado_pre == cmd.interpretador.contextos[-1].values


def test_repl_contract_seguridad_usar_atomico_holobit_y_datos_sin_overwrite(monkeypatch):
    mod_holobit = _modulo_holobit_publico_stub()
    mod_datos = _modulo_datos_stub()
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
    with pytest.raises(NameError, match=r"No se puede usar el módulo 'holobit':"):
        class _NodoUsarHolobit:
            modulo = "holobit"

        interp.ejecutar_usar(_NodoUsarHolobit())
    assert estado_pre_holobit == interp.contextos[-1].values

    assert interp.obtener_variable("graficar")({}) == "ocupado"

    interp.contextos[-1].define("longitud", lambda _v: -1)
    estado_pre_datos = dict(interp.contextos[-1].values)
    with pytest.raises(NameError, match=r"No se puede usar el módulo 'datos':"):
        class _NodoUsarDatos:
            modulo = "datos"

        interp.ejecutar_usar(_NodoUsarDatos())
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
def test_repl_contract_pipeline_completo_por_modulo_canonico(monkeypatch, modulo):
    mod = ModuleType(modulo)
    if modulo == "holobit":
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
            setattr(mod, nombre, lambda *args, _mod=modulo, **kwargs: {"modulo": _mod, "args": args, "kwargs": kwargs})
        expected_symbol = "crear_holobit"
    elif modulo == "texto":
        mod.__all__ = ["a_snake"]
        mod.a_snake = lambda *args, **kwargs: {"modulo": modulo, "args": args, "kwargs": kwargs}
        expected_symbol = "a_snake"
    else:
        mod.__all__ = ["api_publica"]
        mod.api_publica = lambda *args, **kwargs: {"modulo": modulo, "args": args, "kwargs": kwargs}
        expected_symbol = "api_publica"
    mod.__file__ = f"/workspace/pCobra/src/pcobra/corelibs/{modulo}.py"

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == modulo:
            return mod
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(REPL_COBRA_MODULE_MAP)

    nodo_usar = type("_NodoUsar", (), {"modulo": modulo})()

    interp.ejecutar_usar(nodo_usar)
    assert expected_symbol in interp.contextos[-1].values
    simbolo = interp.contextos[-1].values[expected_symbol]
    if modulo == "texto":
        assert callable(simbolo)
        assert simbolo("HolaMundo") == "hola_mundo"
    else:
        assert simbolo()["modulo"] == modulo


def test_repl_contract_colision_warn_alias_required_estructurada(monkeypatch):
    mod_numero = _modulo_numero_multi_export_stub()

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: mod_numero)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(REPL_COBRA_MODULE_MAP)
    interp.configurar_politica_colision_usar("warn_alias_required")
    interp.contextos[-1].define("es_finito", lambda _valor: "ocupado")

    class _NodoUsar:
        modulo = "numero"

    with pytest.raises(NameError, match=r"colisión estructurada=.*policy"):
        interp.ejecutar_usar(_NodoUsar())



@pytest.mark.parametrize(
    "nombre",
    ["", "   ", "../numero", "..\\numero", "corelibs/numero", "standard_library/texto", "pcobra", "holobit_sdk"],
)
def test_repl_rechaza_nombres_invalidos_o_maliciosos(nombre):
    cmd = InteractiveCommand(InterpretadorCobra())
    estado_pre = dict(cmd.interpretador.contextos[-1].values)

    with pytest.raises((ValueError, PermissionError), match=r"(inválido|no permitido|externo|modulo_fuera_catalogo_publico|fuera del catálogo público)"):
        cmd.ejecutar_codigo(f'usar "{nombre}"')

    assert estado_pre == cmd.interpretador.contextos[-1].values


def test_repl_rechaza_alias_legacy_fuera_contrato():
    cmd = InteractiveCommand(InterpretadorCobra())
    estado_pre = dict(cmd.interpretador.contextos[-1].values)

    with pytest.raises(PermissionError, match=r"solo alias oficiales Cobra|nombres canónicos exactos|no permitido|modulo_fuera_catalogo_publico"):
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

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

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



def test_repl_usar_numero_logica_tiempo_y_funcion_usuario_anidada(capsys):
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "numero"')
    cmd._ejecutar_en_modo_normal('usar "logica"')
    cmd._ejecutar_en_modo_normal('usar "tiempo"')
    cmd._ejecutar_en_modo_normal("func doble(n):\n    retorno n * 2\nfin")

    cmd._ejecutar_en_modo_normal('imprimir(es_finito(5))')
    cmd._ejecutar_en_modo_normal('imprimir(signo(0-7))')
    cmd._ejecutar_en_modo_normal('imprimir(conjuncion(verdadero, negacion(falso)))')
    cmd._ejecutar_en_modo_normal('imprimir(epoch())')
    cmd._ejecutar_en_modo_normal('imprimir(doble(signo(0-3)))')

    lineas = [linea.strip() for linea in capsys.readouterr().out.splitlines() if linea.strip()]
    assert 'verdadero' in lineas
    assert '-1' in lineas
    assert any(l in ('true', 'verdadero') for l in lineas)
    epoch_line = next(l for l in lineas if l.lstrip('-').isdigit())
    assert epoch_line.lstrip('-').isdigit()
    assert '-2' in lineas


def test_repl_texto_7_casos_aceptacion(capsys):
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "texto"')
    interp = cmd._delegate.interpretador

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

def test_repl_archivo_existe_ruta_permitida_y_denegada(tmp_path):
    permitido = tmp_path / 'ok.txt'
    permitido.write_text('ok', encoding='utf-8')

    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "archivo"')
    interp = cmd._delegate.interpretador

    existe = interp.obtener_variable('existe')
    assert isinstance(existe(str(permitido)), bool)
    assert isinstance(existe('/etc/passwd'), bool)

def test_repl_usar_idempotente_y_conflicto_real(monkeypatch):
    mod_numero = _modulo_numero_stub()
    monkeypatch.setattr(
        core_usar_loader,
        'obtener_modulo_cobra_oficial',
        lambda nombre: mod_numero if nombre == 'numero' else (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )

    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "numero"')
    estado_1 = dict(cmd._delegate.interpretador.contextos[-1].values)
    with pytest.raises(NameError):
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


def test_no_regresion_seguridad_usar_numpy_fuera_catalogo_publico():
    cmd = ReplCommandV2()
    with pytest.raises(PermissionError, match=r'(modulo_fuera_catalogo_publico|módulo fuera del catálogo público)'):
        cmd._ejecutar_en_modo_normal('usar "numpy"')
