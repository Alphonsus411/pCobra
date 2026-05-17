from __future__ import annotations

import subprocess
import sys
from types import ModuleType

import pytest

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.commands_v2.repl_cmd import ReplCommandV2
from pcobra.core import usar_loader as core_usar_loader
from pcobra.cobra.core.runtime import InterpretadorCobra

_USAR_METADATA_CANONICAL_KEYS = frozenset(
    {
        "origin_kind",
        "module",
        "symbol",
        "sanitized",
        "safe_wrapper",
        "public_api",
        "backend_exposed",
        "callable",
        "python_module",
        "callable_id",
        "stable_signature",
    }
)


def _modulo_stub(nombre: str, exports: dict[str, object], file_path: str) -> ModuleType:
    mod = ModuleType(nombre)
    mod.__all__ = list(exports)
    for k, v in exports.items():
        setattr(mod, k, v)
    mod.__file__ = file_path
    return mod


def _crear_numero() -> ModuleType:
    return _modulo_stub(
        "numero",
        {"es_finito": lambda valor: valor == valor and valor not in (float("inf"), float("-inf"))},
        "/workspace/pCobra/src/pcobra/corelibs/numero.py",
    )


def _crear_texto() -> ModuleType:
    return _modulo_stub(
        "texto",
        {"a_snake": lambda texto: "hola_mundo" if texto == "HolaMundo" else str(texto)},
        "/workspace/pCobra/src/pcobra/corelibs/texto.py",
    )


def _crear_datos() -> ModuleType:
    return _modulo_stub(
        "datos",
        {"longitud": lambda valores: len(valores)},
        "/workspace/pCobra/src/pcobra/corelibs/datos.py",
    )


def _crear_holobit() -> ModuleType:
    return _modulo_stub(
        "holobit",
        {"crear_holobit": lambda nombre: {"nombre": nombre}},
        "/workspace/pCobra/src/pcobra/corelibs/holobit.py",
    )


def _crear_comando(factory):
    cmd = factory()
    if isinstance(cmd, InteractiveCommand):
        return cmd, (lambda code: cmd.ejecutar_codigo(code)), cmd.interpretador
    return cmd, (lambda code: cmd._ejecutar_en_modo_normal(code)), cmd._delegate.interpretador


@pytest.mark.parametrize("factory", [lambda: InteractiveCommand(InterpretadorCobra()), ReplCommandV2])
def test_caso_1_numero_superficie_publica_espanol(factory, monkeypatch):
    mod_numero = _crear_numero()
    resolver = lambda nombre, **_kwargs: mod_numero if nombre == "numero" else (_ for _ in ()).throw(ModuleNotFoundError(nombre))
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", resolver)

    _cmd, ejecutar, interp = _crear_comando(factory)
    ejecutar('usar "numero"')

    assert "es_finito" in interp.contextos[-1].values
    assert "isfinite" not in interp.contextos[-1].values


@pytest.mark.parametrize("factory", [lambda: InteractiveCommand(InterpretadorCobra()), ReplCommandV2])
def test_caso_2_texto_superficie_publica_espanol(factory, monkeypatch):
    mod_texto = _crear_texto()
    resolver = lambda nombre, **_kwargs: mod_texto if nombre == "texto" else (_ for _ in ()).throw(ModuleNotFoundError(nombre))
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", resolver)

    _cmd, ejecutar, interp = _crear_comando(factory)
    ejecutar('usar "texto"')

    assert "a_snake" in interp.contextos[-1].values
    assert "to_snake" not in interp.contextos[-1].values


def test_caso_3_datos_superficie_publica_espanol():
    mod_datos = core_usar_loader.obtener_modulo_cobra_oficial("datos")
    simbolos = set(getattr(mod_datos, "__all__", ()))

    assert "longitud" in simbolos
    assert "leer_csv" in simbolos
    assert "read_csv" not in simbolos


@pytest.mark.parametrize("modulo_externo", ["numpy", "node-fetch", "serde", "holobit_sdk"])
@pytest.mark.parametrize("factory", [lambda: InteractiveCommand(InterpretadorCobra()), ReplCommandV2])
def test_casos_4_a_7_rechaza_modulos_no_permitidos(modulo_externo, factory, monkeypatch):
    mod_numero = _crear_numero()
    resolver = lambda nombre, **_kwargs: mod_numero if nombre == "numero" else (_ for _ in ()).throw(ModuleNotFoundError(nombre))
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", resolver)

    _cmd, ejecutar, interp = _crear_comando(factory)
    ejecutar('usar "numero"')
    estado_pre = dict(interp.contextos[-1].values)

    with pytest.raises(PermissionError, match=r"módulo externo no permitido en REPL estricto"):
        ejecutar(f'usar "{modulo_externo}"')

    assert interp.contextos[-1].values == estado_pre


def test_caso_8_no_exponer_simbolos_privados_ni_bloqueados_en_corelibs_publicas():
    bloqueados = {"self", "append", "map", "filter", "unwrap", "expect"}
    for modulo in (_crear_numero(), _crear_texto(), _crear_datos(), core_usar_loader.obtener_modulo_cobra_oficial("holobit")):
        for simbolo in modulo.__all__:
            assert "__" not in simbolo
            assert simbolo not in bloqueados


@pytest.mark.parametrize("modulo", ["numero", "texto", "datos", "holobit"])
@pytest.mark.parametrize("factory", [lambda: InteractiveCommand(InterpretadorCobra()), ReplCommandV2])
def test_usar_modulos_canonicos_solo_exponen_superficie_espanol(modulo, factory, monkeypatch):
    stubs = {
        "numero": _crear_numero(),
        "texto": _crear_texto(),
        "datos": _crear_datos(),
        "holobit": _crear_holobit(),
    }
    resolver = lambda nombre, **_kwargs: stubs[nombre] if nombre in stubs else (_ for _ in ()).throw(ModuleNotFoundError(nombre))
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", resolver)

    _cmd, ejecutar, interp = _crear_comando(factory)
    ejecutar(f'usar "{modulo}"')
    estado = interp.contextos[-1].values
    bloqueados = {"self", "append", "map", "filter", "unwrap", "expect"}
    assert estado, "el entorno no debe quedar vacío tras usar módulo canónico"
    for simbolo in estado:
        assert "__" not in simbolo
        assert simbolo not in bloqueados


def test_caso_9_startup_runtime_y_cli_no_cargan_backends_legacy():
    comandos = [
        [sys.executable, "-c", "import pcobra; print('ok')"],
        [sys.executable, "-m", "pcobra.cli", "--help"],
        [sys.executable, "-m", "pcobra.cli", "repl", "--help"],
    ]
    for cmd in comandos:
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        salida = f"{result.stdout}\n{result.stderr}".lower()
        assert "legacy backend" not in salida


def test_caso_10_public_backends_contrato_exacto():
    assert PUBLIC_BACKENDS == ("python", "javascript", "rust")


@pytest.mark.parametrize("factory", [lambda: InteractiveCommand(InterpretadorCobra(safe_mode=True)), ReplCommandV2])
def test_usar_reimportes_reinyecciones_metadata_canonica_e_idempotente(factory):
    cmd, ejecutar, interp = _crear_comando(factory)
    if hasattr(cmd, "_delegate"):
        cmd._delegate.interpretador.safe_mode = True
    for modulo in ("datos", "numero", "archivo"):
        ejecutar(f'usar "{modulo}"')
        snapshot_interp_1 = dict(interp._usar_symbol_metadata)
        snapshot_val_1 = dict(getattr(interp._validador, "_metadata_simbolos_usar", {}))
        ejecutar(f'usar "{modulo}"')
        snapshot_interp_2 = dict(interp._usar_symbol_metadata)
        snapshot_val_2 = dict(getattr(interp._validador, "_metadata_simbolos_usar", {}))
        assert snapshot_interp_1 == snapshot_interp_2
        assert set(snapshot_val_1.keys()).issubset(set(snapshot_val_2.keys()))
        assert snapshot_interp_2 == snapshot_val_2

    for nombre, metadata in interp._usar_symbol_metadata.items():
        assert isinstance(metadata, dict), f"metadata de {nombre} debe ser dict"
        assert set(metadata).issubset(_USAR_METADATA_CANONICAL_KEYS)
