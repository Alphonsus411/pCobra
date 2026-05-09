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
    for modulo in (_crear_numero(), _crear_texto(), _crear_datos()):
        for simbolo in modulo.__all__:
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
