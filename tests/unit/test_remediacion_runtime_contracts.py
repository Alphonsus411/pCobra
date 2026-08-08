from __future__ import annotations

import asyncio
import importlib.machinery
import sys
from types import ModuleType

import pytest

from pcobra.cobra.usar_capabilities import capacidades_de
from pcobra.cobra.usar_loader import usar_modulo
from pcobra.cobra.usar_policy import CANONICAL_MODULE_SURFACE_CONTRACTS
from pcobra.corelibs import compresion, red, sistema
from pcobra.core.ast_nodes import NodoUsar
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython


@pytest.mark.parametrize(
    "modulo,nombre",
    [
        (modulo, nombre)
        for modulo, contrato in CANONICAL_MODULE_SURFACE_CONTRACTS.items()
        for nombre, capacidades in contrato.symbol_capabilities.items()
        if capacidades
        & {
            "process.spawn",
            "process.shell",
            "network.get",
            "network.post",
            "network.download",
            "filesystem.read",
            "filesystem.write",
        }
    ],
)
def test_todo_simbolo_effectful_usa_la_clasificacion_canonica_y_se_bloquea(modulo, nombre):
    esperadas = CANONICAL_MODULE_SURFACE_CONTRACTS[modulo].symbol_capabilities[nombre]
    assert esperadas
    assert {capacidad.value for capacidad in capacidades_de(modulo, nombre)} == esperadas
    simbolo = usar_modulo(modulo, safe_mode=True)[nombre]
    if callable(simbolo):
        try:
            resultado = simbolo()
        except PermissionError:
            return
        if hasattr(resultado, "__anext__"):
            with pytest.raises(PermissionError):
                asyncio.run(resultado.__anext__())
        elif hasattr(resultado, "__await__"):
            with pytest.raises(PermissionError):
                asyncio.run(resultado)
        else:
            pytest.fail("un símbolo effectful invocable alcanzó el runtime en safe_mode")


@pytest.mark.parametrize(
    "nombre", ("ejecutar_async", "ejecutar_stream", "ejecutar_comando_async")
)
def test_sistema_safe_mode_bloquea_allowlist_del_caller(nombre):
    funcion = usar_modulo("sistema", safe_mode=True)[nombre]
    with pytest.raises(PermissionError, match="process.spawn"):
        resultado = funcion([sys.executable], permitidos=[sys.executable])
        if hasattr(resultado, "close"):
            resultado.close()


def test_modulo_oficial_preinyectado_sin_procedencia_es_rechazado(monkeypatch):
    falso = ModuleType("pcobra.corelibs.numero")
    falso.__spec__ = importlib.machinery.ModuleSpec(falso.__name__, loader=None)
    monkeypatch.setitem(sys.modules, falso.__name__, falso)

    with pytest.raises(PermissionError, match="procedencia_no_oficial"):
        usar_modulo("numero")


@pytest.mark.parametrize("modulo", ("red", "proceso"))
def test_transpilador_python_propaga_safe_mode_explicito(modulo):
    inseguro = TranspiladorPython(safe_mode=False).generate_code([NodoUsar(modulo)])
    seguro = TranspiladorPython(safe_mode=True).generate_code([NodoUsar(modulo)])

    assert f"usar_modulo('{modulo}', safe_mode=False)" in inseguro
    assert f"usar_modulo('{modulo}', safe_mode=True)" in seguro


def test_zip_crear_listar_extraer_comparte_sandbox(monkeypatch, tmp_path):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    (tmp_path / "entrada.txt").write_text("contenido", encoding="utf-8")

    assert compresion.crear_zip("a.zip", "entrada.txt") == ["entrada.txt"]
    assert compresion.listar_zip("a.zip") == ["entrada.txt"]
    compresion.extraer_zip("a.zip", "salida")

    assert (tmp_path / "salida" / "entrada.txt").read_text(encoding="utf-8") == "contenido"


@pytest.mark.asyncio
async def test_descarga_cancelada_limpia_temporal_y_preserva_destino(monkeypatch, tmp_path):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    destino = tmp_path / "destino.bin"
    destino.write_bytes(b"previo")

    async def cancelar(*args, archivo_destino, **kwargs):
        archivo_destino.write(b"parcial")
        raise asyncio.CancelledError

    monkeypatch.setattr(red, "_realizar_peticion_async", cancelar)
    with pytest.raises(asyncio.CancelledError):
        await red.descargar_archivo("https://example.com", "destino.bin")

    assert destino.read_bytes() == b"previo"
    assert list(tmp_path.glob(".pcobra-download-*")) == []


@pytest.mark.asyncio
async def test_timeout_stream_no_cancela_await_del_consumidor():
    generador = sistema.ejecutar_stream(
        [sys.executable, "-c", "print('primera', flush=True)"],
        permitidos=[sys.executable],
        timeout=0.1,
    )

    assert await generador.__anext__() == "primera\n"
    await asyncio.sleep(0.2)
    await generador.aclose()
