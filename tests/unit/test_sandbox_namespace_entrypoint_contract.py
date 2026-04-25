from __future__ import annotations

import importlib
import sys
import tomllib
from pathlib import Path
from types import ModuleType

import pytest

from pcobra.cobra.cli.internal_compat import legacy_core_sandbox


ROOT = Path(__file__).resolve().parents[2]


def test_entrypoints_publicos_apuntan_al_namespace_pcobra() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = pyproject["project"]["scripts"]

    assert scripts["cobra"] == "pcobra.cli:main"

    source_main = (ROOT / "src" / "pcobra" / "__main__.py").read_text(encoding="utf-8")
    assert "from pcobra.cli import main" in source_main


def test_run_service_declara_solo_namespace_canonico_para_sandbox() -> None:
    source = (ROOT / "src" / "pcobra" / "cobra" / "cli" / "services" / "run_service.py").read_text(
        encoding="utf-8"
    )

    assert "from pcobra.core import sandbox as sandbox_module" in source
    assert 'import_module("core.sandbox")' not in source


def test_legacy_core_sandbox_emite_deprecacion_con_fecha(monkeypatch):
    canonical_error = ModuleNotFoundError("pcobra.core.sandbox")
    monkeypatch.setenv(legacy_core_sandbox.LEGACY_SANDBOX_COMPAT_FLAG, "1")

    module = ModuleType("core.sandbox")
    expected_path = (ROOT / "src" / "pcobra" / "core" / "sandbox.py").resolve()
    module.__file__ = str(expected_path)

    monkeypatch.setattr(
        legacy_core_sandbox.importlib,
        "import_module",
        lambda name: module if name == "core.sandbox" else (_ for _ in ()).throw(ModuleNotFoundError(name)),
    )

    with pytest.warns(DeprecationWarning, match=legacy_core_sandbox.LEGACY_SANDBOX_RETIREMENT_DATE):
        resolved = legacy_core_sandbox.load_legacy_core_sandbox(canonical_error=canonical_error)

    assert resolved is module


def test_legacy_core_sandbox_rechaza_modulo_homonimo(monkeypatch, tmp_path):
    canonical_error = ModuleNotFoundError("pcobra.core.sandbox")
    monkeypatch.setenv(legacy_core_sandbox.LEGACY_SANDBOX_COMPAT_FLAG, "1")

    fake = tmp_path / "core" / "sandbox.py"
    fake.parent.mkdir(parents=True)
    fake.write_text("", encoding="utf-8")

    module = ModuleType("core.sandbox")
    module.__file__ = str(fake)

    monkeypatch.setattr(
        legacy_core_sandbox.importlib,
        "import_module",
        lambda name: module if name == "core.sandbox" else (_ for _ in ()).throw(ModuleNotFoundError(name)),
    )

    with pytest.raises(ImportError, match="no apunta al paquete esperado"):
        legacy_core_sandbox.load_legacy_core_sandbox(canonical_error=canonical_error)


def test_namespace_instalado_resuelve_sandbox_canonico() -> None:
    for key in tuple(sys.modules):
        if key.startswith("pcobra.cobra.cli.services.run_service"):
            sys.modules.pop(key, None)

    run_service = importlib.import_module("pcobra.cobra.cli.services.run_service")
    resolved = run_service._importar_modulo_sandbox()

    assert resolved.__name__ == "pcobra.core.sandbox"
