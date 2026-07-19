from argparse import Namespace
from unittest.mock import patch
import re
from pathlib import Path

import pytest

from pcobra.cobra.cli.cobrahub_packages import (
    limpiar_cache,
    listar_cache,
    validar_cache,
)
from pcobra.cobra.cli.commands.hub_cmd import HubCommand
from pcobra.cobra.cli.services.cobrahub_service import CobraHubService
from pcobra.cobra.packaging import construir_paquete, crear_paquete


@pytest.fixture(autouse=True)
def _perfil_cli_desarrollo(monkeypatch):
    monkeypatch.setenv("COBRA_CLI_COMMAND_PROFILE", "development")


def _crear_paquete_valido(tmp_path: Path, nombre: str = "demo") -> Path:
    proyecto = tmp_path / f"src-{nombre}"
    crear_paquete(proyecto, nombre=nombre, version="1.0.0")
    (proyecto / "src" / "main.cobra").write_text("imprimir('hola')\n", encoding="utf-8")
    return construir_paquete(proyecto, tmp_path / f"{nombre}.co")


@pytest.mark.parametrize(
    ("metodo", "argumentos"),
    [
        ("publicar_paquete", ("demo.co",)),
        ("buscar_paquetes", ("demo",)),
        ("instalar_paquete", ("demo",)),
    ],
)
def test_operaciones_remotas_requieren_dependencias_explicitas(metodo, argumentos):
    service = CobraHubService()

    with pytest.raises(RuntimeError, match="proveedor y un repositorio"):
        getattr(service, metodo)(*argumentos)


def test_listar_cache_devuelve_solo_paquetes_co_ordenados(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("COBRAHUB_CACHE_DIR", str(tmp_path))
    (tmp_path / "b.co").write_text("no importa para listar", encoding="utf-8")
    (tmp_path / "a.co").write_text("no importa para listar", encoding="utf-8")
    (tmp_path / "nota.txt").write_text("ignorado", encoding="utf-8")

    assert [path.name for path in listar_cache()] == ["a.co", "b.co"]


def test_limpiar_cache_borra_todo_o_por_nombre(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("COBRAHUB_CACHE_DIR", str(tmp_path))
    for nombre in ["demo.co", "demo-1.0.0.co", "otro.co", "nota.txt"]:
        (tmp_path / nombre).write_text("x", encoding="utf-8")

    assert limpiar_cache("demo") == 2
    assert not (tmp_path / "demo.co").exists()
    assert not (tmp_path / "demo-1.0.0.co").exists()
    assert (tmp_path / "otro.co").exists()
    assert limpiar_cache() == 1
    assert (tmp_path / "nota.txt").exists()


def test_validar_cache_reutiliza_validadores_de_paquetes(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("COBRAHUB_CACHE_DIR", str(tmp_path / "cache"))
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    paquete = _crear_paquete_valido(tmp_path, "demo")
    paquete.replace(cache_dir / "demo.co")
    (cache_dir / "roto.co").write_text("var x = 1", encoding="utf-8")

    resultados = {path.name: (ok, error) for path, ok, error in validar_cache()}

    assert resultados["demo.co"] == (True, None)
    assert resultados["roto.co"][0] is False
    assert "No es un paquete Cobra" in resultados["roto.co"][1]


def test_cli_hub_cache_validar_devuelve_error_si_hay_invalidos(
    tmp_path: Path, monkeypatch, capsys
):
    monkeypatch.setenv("COBRAHUB_CACHE_DIR", str(tmp_path))
    (tmp_path / "roto.co").write_text("var x = 1", encoding="utf-8")

    codigo = HubCommand().run(Namespace(accion="cache", cache_accion="validar"))

    salida = capsys.readouterr().out
    assert codigo == 1
    assert "roto.co" in salida
    assert "inválido" in salida


def test_cli_hub_cache_limpiar_informa_total(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setenv("COBRAHUB_CACHE_DIR", str(tmp_path))
    (tmp_path / "demo.co").write_text("x", encoding="utf-8")

    codigo = HubCommand().run(
        Namespace(accion="cache", cache_accion="limpiar", nombre=None)
    )

    assert codigo == 0
    assert "Paquetes eliminados de caché: 1" in capsys.readouterr().out
    assert listar_cache() == []


def test_cli_hub_publicar_delega_en_cobrahub_packages_sin_red():
    args = Namespace(accion="publicar", paquete=Path("dist/demo.co"))

    with patch(
        "pcobra.cobra.cli.commands.hub_cmd.CobraHubPackages.publicar_paquete",
        return_value=True,
    ) as publicar:
        codigo = HubCommand().run(args)

    assert codigo == 0
    publicar.assert_called_once_with("dist/demo.co")


def test_cli_hub_buscar_imprime_resultados_normalizados(capsys):
    args = Namespace(accion="buscar", consulta="demo")
    resultados = [
        {"name": "demo", "version": "1.2.3"},
        {"nombre": "ejemplo", "version": "2.0.0"},
        {"version": "0.1.0"},
    ]

    with patch(
        "pcobra.cobra.cli.commands.hub_cmd.CobraHubPackages.buscar_paquetes",
        return_value=resultados,
    ) as buscar:
        codigo = HubCommand().run(args)

    salida = capsys.readouterr().out
    assert codigo == 0
    buscar.assert_called_once_with("demo")
    assert "demo 1.2.3" in salida
    assert "ejemplo 2.0.0" in salida
    assert "paquete 0.1.0" in salida


def test_cli_hub_instalar_delega_en_cobrahub_packages_sin_red():
    args = Namespace(
        accion="instalar",
        nombre="demo",
        version="1.2.3",
        destino=Path("ruta"),
    )

    with patch(
        "pcobra.cobra.cli.commands.hub_cmd.CobraHubPackages.instalar_paquete",
        return_value=True,
    ) as instalar:
        codigo = HubCommand().run(args)

    assert codigo == 0
    instalar.assert_called_once_with("demo", "ruta", "1.2.3")


def test_cli_hub_publicar_e_instalar_devuelven_error_si_falla_operacion():
    with patch(
        "pcobra.cobra.cli.commands.hub_cmd.CobraHubPackages.publicar_paquete",
        return_value=False,
    ):
        codigo_publicar = HubCommand().run(
            Namespace(accion="publicar", paquete=Path("dist/demo.co"))
        )

    with patch(
        "pcobra.cobra.cli.commands.hub_cmd.CobraHubPackages.instalar_paquete",
        return_value=False,
    ):
        codigo_instalar = HubCommand().run(
            Namespace(accion="instalar", nombre="demo", version=None, destino=None)
        )

    assert codigo_publicar != 0
    assert codigo_instalar != 0


def test_cli_hub_cache_listar_conserva_salida_ordenada(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setenv("COBRAHUB_CACHE_DIR", str(tmp_path))
    (tmp_path / "b.co").write_text("x", encoding="utf-8")
    (tmp_path / "a.co").write_text("x", encoding="utf-8")
    (tmp_path / "nota.txt").write_text("x", encoding="utf-8")

    codigo = HubCommand().run(Namespace(accion="cache", cache_accion="listar"))

    lineas = [
        re.sub(r"\x1b\[[0-9;]*m", "", line.strip())
        for line in capsys.readouterr().out.splitlines()
        if line.strip()
    ]
    assert codigo == 0
    assert lineas == [str(tmp_path / "a.co"), str(tmp_path / "b.co")]


def test_main_cobra_cli_hub_publicar_delega_sin_red():
    from cobra.cli.cli import main

    with patch(
        "pcobra.cobra.cli.commands.hub_cmd.CobraHubPackages.publicar_paquete",
        return_value=True,
    ) as publicar:
        codigo = main(["hub", "publicar", "dist/demo.co"])

    assert codigo == 0
    publicar.assert_called_once_with("dist/demo.co")
