from __future__ import annotations

import importlib.util
import runpy
import sys
from io import StringIO
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

import pytest

from cobra.cli.cli import main

WRAPPER_FILES = (
    ("src/cli/cli.py", "cli.cli"),
    ("src/cobra/cli/cli.py", "cobra.cli.cli"),
    ("cobra/cli/cli.py", "cobra.cli.cli"),
)



def _instalar_stubs_cli(monkeypatch: pytest.MonkeyPatch):
    llamadas_main: list[list[str] | None] = []
    llamadas_legacy: list[str] = []

    modulo_canonico = ModuleType("pcobra.cobra.cli.cli")

    def _main_stub(argv=None):
        llamadas_main.append(argv)
        return 37

    modulo_canonico.main = _main_stub
    monkeypatch.setitem(sys.modules, "pcobra.cobra.cli.cli", modulo_canonico)

    modulo_pcobra_cli = ModuleType("pcobra.cli")

    def _build_stub(ruta_modulo: str):
        llamadas_legacy.append(ruta_modulo)
        return _main_stub

    modulo_pcobra_cli.build_legacy_cli_shim_main = _build_stub
    monkeypatch.setitem(sys.modules, "pcobra.cli", modulo_pcobra_cli)

    return llamadas_main, llamadas_legacy


def _cargar_modulo_desde_archivo(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_init_creates_project(tmp_path):
    ruta = tmp_path / "proy"
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["init", str(ruta)])
    assert (ruta / "main.co").exists()
    assert "Proyecto Cobra inicializado" in out.getvalue()


@pytest.mark.parametrize(("wrapper_path", "legacy_route"), WRAPPER_FILES)
def test_wrappers_delegan_al_entrypoint_canonico(wrapper_path, legacy_route, monkeypatch):
    llamadas_main, llamadas_legacy = _instalar_stubs_cli(monkeypatch)
    modulo = _cargar_modulo_desde_archivo(
        f"test_wrapper_{wrapper_path.replace('/', '_').replace('.', '_')}",
        Path(wrapper_path),
    )

    assert modulo.main(["--version"]) == 37
    assert llamadas_main == [["--version"]]
    assert llamadas_legacy == [legacy_route]


@pytest.mark.parametrize(("wrapper_path", "legacy_route"), WRAPPER_FILES)
def test_wrappers_ejecutan_como_script(wrapper_path, legacy_route, monkeypatch):
    llamadas_main, llamadas_legacy = _instalar_stubs_cli(monkeypatch)

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(wrapper_path, run_name="__main__")

    assert exc_info.value.code == 37
    assert llamadas_main == [None]
    assert llamadas_legacy == [legacy_route]

