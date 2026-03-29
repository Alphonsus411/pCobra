"""Pruebas unitarias para el runtime compartido de GUI."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from pcobra.gui import runtime


@pytest.fixture(autouse=True)
def _reset_cache():
    runtime.require_gui_dependencies.cache_clear()
    yield
    runtime.require_gui_dependencies.cache_clear()


def test_normalizar_codigo_admite_none_y_texto() -> None:
    assert runtime.normalizar_codigo(None) == ""
    assert runtime.normalizar_codigo("imprimir('x')") == "imprimir('x')"


def test_ejecutar_transpilar_tokens_y_ast() -> None:
    codigo = "imprimir('Hola')"
    assert runtime.ejecutar_codigo(codigo) == "Hola\n"
    assert runtime.transpilar_codigo(codigo, "python").strip()
    assert "Token(" in runtime.mostrar_tokens(codigo)
    assert "NodoImprimir" in runtime.mostrar_ast(codigo)


def test_formatear_error_lexico_y_sintaxis() -> None:
    deps = runtime.require_gui_dependencies()

    try:
        deps["Lexer"]("\x00").tokenizar()
    except Exception as exc:
        mensaje = runtime.formatear_error(exc)
        assert mensaje.startswith("Error léxico")
    else:  # pragma: no cover
        pytest.fail("Se esperaba error léxico")

    try:
        tokens = deps["Lexer"]("imprimir('x'").tokenizar()
        deps["Parser"](tokens).parsear()
    except Exception as exc:
        mensaje = runtime.formatear_error(exc)
        assert mensaje.startswith("Error de sintaxis")
    else:  # pragma: no cover
        pytest.fail("Se esperaba error de sintaxis")


def test_gui_target_choices_filtra_targets_no_oficiales(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {
            "target_cli_choices": lambda targets: tuple(sorted(targets)),
            "OFFICIAL_TARGETS": ("python", "java", "asm"),
            "TRANSPILERS": {"python": object, "backend_x": object, "asm": object},
        },
    )

    assert runtime.gui_target_choices() == ("asm", "python")


def test_require_flet_error_accionable(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = __import__

    def _import_fail_flet(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "flet":
            raise ModuleNotFoundError("No module named 'flet'", name="flet")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", _import_fail_flet)

    with pytest.raises(RuntimeError, match="pip install flet"):
        runtime.require_flet()


def test_require_gui_dependencies_error_accionable(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = __import__

    def _import_fail_core(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pcobra.core.interpreter":
            raise ModuleNotFoundError(
                "No module named 'pcobra.core.interpreter'", name="pcobra.core.interpreter"
            )
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", _import_fail_core)

    with pytest.raises(RuntimeError, match="pcobra.core.interpreter"):
        runtime.require_gui_dependencies()


def test_require_gui_dependencies_cachea_resultado() -> None:
    deps_a = runtime.require_gui_dependencies()
    deps_b = runtime.require_gui_dependencies()
    assert deps_a is deps_b
