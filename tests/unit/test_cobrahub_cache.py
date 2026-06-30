from argparse import Namespace
from pathlib import Path

from pcobra.cobra.cli.cobrahub_packages import (
    limpiar_cache,
    listar_cache,
    validar_cache,
)
from pcobra.cobra.cli.commands.hub_cmd import HubCommand
from pcobra.cobra.packaging import construir_paquete, crear_paquete


def _crear_paquete_valido(tmp_path: Path, nombre: str = "demo") -> Path:
    proyecto = tmp_path / f"src-{nombre}"
    crear_paquete(proyecto, nombre=nombre, version="1.0.0")
    (proyecto / "src" / "main.cobra").write_text("imprimir('hola')\n", encoding="utf-8")
    return construir_paquete(proyecto, tmp_path / f"{nombre}.co")


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
