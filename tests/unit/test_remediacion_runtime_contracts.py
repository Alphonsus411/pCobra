from __future__ import annotations

import asyncio
import importlib.machinery
import sys
from types import ModuleType

import pytest

from pcobra.cobra.usar_capabilities import capacidades_de
from pcobra.cobra.usar_loader import usar_modulo
from pcobra.cobra.usar_policy import (
    CANONICAL_MODULE_SURFACE_CONTRACTS,
    FILESYSTEM_SYMBOL_POLICIES,
)
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
        }
    ],
)
def test_simbolos_restringidos_usan_clasificacion_canonica_y_se_bloquean(
    modulo, nombre
):
    esperadas = CANONICAL_MODULE_SURFACE_CONTRACTS[modulo].symbol_capabilities[nombre]
    assert esperadas
    assert {
        capacidad.value for capacidad in capacidades_de(modulo, nombre)
    } == esperadas
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
            pytest.fail(
                "un símbolo effectful invocable alcanzó el runtime en safe_mode"
            )


@pytest.mark.parametrize(
    "modulo,nombre",
    [
        (modulo, nombre)
        for modulo, contrato in CANONICAL_MODULE_SURFACE_CONTRACTS.items()
        for nombre, capacidades in contrato.symbol_capabilities.items()
        if capacidades & {"filesystem.read", "filesystem.write"}
    ],
)
def test_simbolos_filesystem_conservan_clasificacion_canonica(modulo, nombre):
    esperadas = CANONICAL_MODULE_SURFACE_CONTRACTS[modulo].symbol_capabilities[nombre]

    assert esperadas
    assert {
        capacidad.value for capacidad in capacidades_de(modulo, nombre)
    } == esperadas


def test_matriz_filesystem_expone_decision_verificable_completa():
    esperados = {
        (modulo, nombre)
        for modulo, contrato in CANONICAL_MODULE_SURFACE_CONTRACTS.items()
        for nombre, capacidades in contrato.symbol_capabilities.items()
        if capacidades & {"filesystem.read", "filesystem.write"}
    }

    assert set(FILESYSTEM_SYMBOL_POLICIES) == esperados
    for (modulo, nombre), policy in FILESYSTEM_SYMBOL_POLICIES.items():
        assert (
            policy.capabilities
            == CANONICAL_MODULE_SURFACE_CONTRACTS[modulo].symbol_capabilities[nombre]
        )
        assert policy.safe_mode_decision == (
            "allow" if policy.sandbox_confined else "deny"
        )


def test_safe_mode_permite_archivo_confinado_y_rechaza_acceso_externo(
    monkeypatch, tmp_path
):
    sandbox = tmp_path / "sandbox"
    outside = tmp_path / "outside"
    sandbox.mkdir()
    outside.mkdir()
    secreto = outside / "secreto.txt"
    secreto.write_text("intacto", encoding="utf-8")
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(sandbox))
    archivo = usar_modulo("archivo", safe_mode=True)

    archivo["escribir"]("permitido.txt", "dentro")
    assert archivo["leer"]("permitido.txt") == "dentro"
    assert (sandbox / "permitido.txt").read_text(encoding="utf-8") == "dentro"
    with pytest.raises(ValueError, match="fuera del directorio permitido"):
        archivo["eliminar"](secreto)
    assert secreto.read_text(encoding="utf-8") == "intacto"


def test_safe_mode_bloquea_lectura_escritura_y_limpieza_no_confinadas(
    monkeypatch, tmp_path
):
    sandbox = tmp_path / "sandbox"
    outside = tmp_path / "outside"
    sandbox.mkdir()
    outside.mkdir()
    externo = outside / "datos.json"
    externo.write_text('{"valor": 1}', encoding="utf-8")
    directorio = outside / "borrar"
    directorio.mkdir()
    (directorio / "testigo").write_text("intacto", encoding="utf-8")
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(sandbox))

    serializacion = usar_modulo("serializacion", safe_mode=True)
    with pytest.raises(PermissionError, match="filesystem.read"):
        serializacion["leer_json"](externo)
    with pytest.raises(PermissionError, match="filesystem.write"):
        serializacion["escribir_json"](externo, {"valor": 2})
    with pytest.raises(PermissionError, match="filesystem.write"):
        usar_modulo("temporal", safe_mode=True)["limpiar"](directorio.resolve())

    assert externo.read_text(encoding="utf-8") == '{"valor": 1}'
    assert (directorio / "testigo").read_text(encoding="utf-8") == "intacto"


def test_safe_mode_false_conserva_filesystem_proceso_y_red(monkeypatch, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    externo = outside / "datos.json"
    serializacion = usar_modulo("serializacion", safe_mode=False)
    serializacion["escribir_json"](externo, {"valor": 2})
    assert serializacion["leer_json"](externo) == {"valor": 2}

    resultado = usar_modulo("proceso", safe_mode=False)["ejecutar"](
        [sys.executable, "-c", "print('ok')"]
    )
    assert resultado["salida"].strip() == "ok"

    monkeypatch.setattr(red, "obtener_url", lambda *_args, **_kwargs: "red-ok")
    assert (
        usar_modulo("red", safe_mode=False)["obtener_url"]("https://example.com")
        == "red-ok"
    )

    assert usar_modulo("temporal", safe_mode=False)["limpiar"](externo) is True
    assert not externo.exists()


def test_safe_mode_bloquea_proceso_y_red_antes_de_operar():
    with pytest.raises(PermissionError, match="process.spawn"):
        usar_modulo("proceso", safe_mode=True)["ejecutar"](
            [sys.executable], permitidos=[sys.executable]
        )
    with pytest.raises(PermissionError, match="network.get"):
        usar_modulo("red", safe_mode=True)["obtener_url"]("https://example.com")


def test_codigo_transpilado_usa_contrato_filesystem_seguro_por_defecto(
    monkeypatch, tmp_path
):
    outside = tmp_path / "outside"
    outside.mkdir()
    testigo = outside / "testigo.txt"
    testigo.write_text("intacto", encoding="utf-8")
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path / "sandbox"))
    (tmp_path / "sandbox").mkdir()

    codigo = TranspiladorPython().generate_code([NodoUsar("temporal")])
    entorno: dict[str, object] = {}
    exec(codigo, entorno)
    with pytest.raises(PermissionError, match="filesystem.write"):
        entorno["limpiar"](str(outside.resolve()))  # type: ignore[operator]
    assert testigo.read_text(encoding="utf-8") == "intacto"


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


@pytest.mark.parametrize("modulo", ("red", "proceso", "numero"))
def test_transpilador_python_propaga_safe_mode_explicito(modulo):
    predeterminado = TranspiladorPython().generate_code([NodoUsar(modulo)])
    inseguro = TranspiladorPython(safe_mode=False).generate_code([NodoUsar(modulo)])
    seguro = TranspiladorPython(safe_mode=True).generate_code([NodoUsar(modulo)])

    assert f"usar_modulo('{modulo}', safe_mode=True)" in predeterminado
    assert f"usar_modulo('{modulo}', safe_mode=False)" in inseguro
    assert f"usar_modulo('{modulo}', safe_mode=True)" in seguro


def test_zip_crear_listar_extraer_comparte_sandbox(monkeypatch, tmp_path):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    (tmp_path / "entrada.txt").write_text("contenido", encoding="utf-8")

    assert compresion.crear_zip("a.zip", "entrada.txt") == ["entrada.txt"]
    assert compresion.listar_zip("a.zip") == ["entrada.txt"]
    compresion.extraer_zip("a.zip", "salida")

    assert (tmp_path / "salida" / "entrada.txt").read_text(
        encoding="utf-8"
    ) == "contenido"


@pytest.mark.asyncio
async def test_descarga_cancelada_limpia_temporal_y_preserva_destino(
    monkeypatch, tmp_path
):
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
