import sys
from types import ModuleType

import cobra.cli.commands.execute_cmd as execute_cmd
import pcobra.jupyter_kernel as jupyter_kernel
import pytest


def _sandbox_mod() -> ModuleType:
    module = ModuleType("pcobra.core.sandbox")
    module.__file__ = "/workspace/pCobra/src/pcobra/core/sandbox.py"
    module.ejecutar_en_sandbox = lambda *_a, **_k: None
    module.ejecutar_en_contenedor = lambda *_a, **_k: None
    module.SecurityError = RuntimeError
    module.validar_dependencias = lambda *_a, **_k: None
    return module


def test_execute_cmd_prioriza_sandbox_canonico(monkeypatch):
    calls: list[str] = []
    canonical = _sandbox_mod()

    def fake_import(name: str):
        calls.append(name)
        if name == "pcobra.core.sandbox":
            return canonical
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(execute_cmd.importlib, "import_module", fake_import)
    resolved = execute_cmd._importar_modulo_sandbox()

    assert resolved is canonical
    assert calls == ["pcobra.core.sandbox"]


def test_execute_cmd_hace_fallback_legacy_si_falta_canonico(monkeypatch, caplog):
    calls: list[str] = []
    legacy = _sandbox_mod()
    legacy.__name__ = "core.sandbox"

    def fake_import(name: str):
        calls.append(name)
        if name == "pcobra.core.sandbox":
            raise ModuleNotFoundError(name)
        if name == "core.sandbox":
            return legacy
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(execute_cmd.importlib, "import_module", fake_import)
    with caplog.at_level("WARNING"):
        resolved = execute_cmd._importar_modulo_sandbox()

    assert resolved is legacy
    assert calls == ["pcobra.core.sandbox", "core.sandbox"]
    assert "compatibilidad legacy" in caplog.text


def test_execute_cmd_rechaza_fallback_legacy_fuera_de_pcobra(monkeypatch):
    legacy = _sandbox_mod()
    legacy.__name__ = "core.sandbox"
    legacy.__file__ = "/tmp/fake/core/sandbox.py"

    def fake_import(name: str):
        if name == "pcobra.core.sandbox":
            raise ModuleNotFoundError(name)
        if name == "core.sandbox":
            return legacy
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(execute_cmd.importlib, "import_module", fake_import)
    with pytest.raises(ImportError, match="no apunta al paquete esperado"):
        execute_cmd._importar_modulo_sandbox()


def test_execute_cmd_no_usa_core_falso_inyectado_en_sys_path(monkeypatch, tmp_path):
    fake_core = tmp_path / "core"
    fake_core.mkdir()
    (fake_core / "__init__.py").write_text("", encoding="utf-8")
    (fake_core / "sandbox.py").write_text(
        "RASTRO_FAKE = True\n"
        "def ejecutar_en_sandbox(*_a, **_k):\n    raise RuntimeError('fake')\n"
        "def ejecutar_en_contenedor(*_a, **_k):\n    raise RuntimeError('fake')\n"
        "class SecurityError(Exception):\n    pass\n"
        "def validar_dependencias(*_a, **_k):\n    return None\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.delitem(sys.modules, "core", raising=False)
    monkeypatch.delitem(sys.modules, "core.sandbox", raising=False)

    resolved = execute_cmd._importar_modulo_sandbox()

    assert getattr(resolved, "RASTRO_FAKE", False) is False
    assert resolved.__name__ == "pcobra.core.sandbox"


def test_kernel_resuelve_dependencias_con_namespace_canonico(monkeypatch):
    calls: list[str] = []
    core_mod = ModuleType("pcobra.cobra.core")
    core_mod.Lexer = object
    core_mod.Parser = object
    core_utils = ModuleType("pcobra.cobra.core.utils")
    core_utils.PALABRAS_RESERVADAS = ["imprimir"]
    interpreter = ModuleType("pcobra.core.interpreter")
    interpreter.InterpretadorCobra = object
    qualia = ModuleType("pcobra.core.qualia_bridge")
    qualia.get_suggestions = lambda: ["uno"]
    sandbox = _sandbox_mod()

    modules = {
        "pcobra.cobra.core": core_mod,
        "pcobra.cobra.core.utils": core_utils,
        "pcobra.core.interpreter": interpreter,
        "pcobra.core.qualia_bridge": qualia,
        "pcobra.core.sandbox": sandbox,
    }

    def fake_import(name: str):
        calls.append(name)
        if name in modules:
            return modules[name]
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(jupyter_kernel.importlib, "import_module", fake_import)
    deps = jupyter_kernel._resolver_dependencias_kernel()

    assert deps["Lexer"] is object
    assert deps["sandbox"] is sandbox
    assert calls == [
        "pcobra.cobra.core",
        "pcobra.cobra.core.utils",
        "pcobra.core.interpreter",
        "pcobra.core.qualia_bridge",
        "pcobra.core.sandbox",
    ]
