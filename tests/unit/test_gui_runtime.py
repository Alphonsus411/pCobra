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
    class FakeLexerError(Exception):
        linea = 2
        columna = 4

    class FakeParserError(Exception):
        pass

    assert runtime.formatear_error(
        FakeLexerError("carácter inválido"),
        lexer_error_type=FakeLexerError,
        parser_error_type=FakeParserError,
    ).startswith("Error léxico")
    assert runtime.formatear_error(
        FakeParserError("faltó cierre"),
        lexer_error_type=FakeLexerError,
        parser_error_type=FakeParserError,
    ).startswith("Error de sintaxis")


def test_gui_target_choices_filtra_targets_no_oficiales(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {
            "target_cli_choices": lambda targets: tuple(sorted(targets)),
            "OFFICIAL_TARGETS": ("python", "javascript", "rust"),
            "TRANSPILERS": {"python": object, "backend_x": object, "rust": object},
        },
    )

    assert runtime.gui_target_choices() == ("python", "rust")


def test_require_flet_error_accionable(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = __import__

    def _import_fail_flet(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "flet":
            raise ModuleNotFoundError("No module named 'flet'", name="flet")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", _import_fail_flet)

    with pytest.raises(RuntimeError, match="pip install flet"):
        runtime.require_flet()


def test_require_gui_dependencies_error_accionable_modulo_ausente(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = __import__

    def _import_fail_core(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pcobra.cobra.gui" and fromlist:
            raise ModuleNotFoundError(
                "No module named 'pcobra.core.interpreter'", name="pcobra.core.interpreter"
            )
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", _import_fail_core)

    with pytest.raises(RuntimeError, match="faltante detectado 'pcobra.core.interpreter'") as excinfo:
        runtime.require_gui_dependencies()
    assert "Acción sugerida" in str(excinfo.value)


def test_require_gui_dependencies_error_accionable_simbolo_ausente(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = __import__

    def _import_fail_symbol(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pcobra.cobra.gui" and fromlist:
            raise ImportError("cannot import name 'Lexer' from 'pcobra.cobra.core'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", _import_fail_symbol)

    with pytest.raises(RuntimeError, match="faltante detectado 'pcobra.cobra.core.Lexer'") as excinfo:
        runtime.require_gui_dependencies()
    assert "corrige el import local de 'pcobra.cobra.core.Lexer'" in str(excinfo.value)


def test_require_gui_dependencies_cachea_resultado(monkeypatch: pytest.MonkeyPatch) -> None:
    llamadas = {"count": 0}
    fake_deps = SimpleNamespace(
        Lexer=object,
        LexerError=Exception,
        Parser=object,
        ParserError=Exception,
        target_cli_choices=lambda _targets: (),
        OFFICIAL_TARGETS=("python", "javascript", "rust"),
        InterpretadorCobra=object,
        get_transpilers=lambda: {"python": object},
    )
    real_import = __import__

    def _import_fake_gui(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pcobra.cobra.gui" and fromlist:
            llamadas["count"] += 1
            return SimpleNamespace(deps=fake_deps)
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", _import_fake_gui)

    deps_a = runtime.require_gui_dependencies()
    deps_b = runtime.require_gui_dependencies()

    assert deps_a is deps_b
    assert llamadas["count"] == 1


def test_formatear_error_no_masking_si_fallan_dependencias() -> None:
    exc = RuntimeError(
        "Error de importación GUI en 'pcobra.gui.runtime': faltante detectado 'x.y'. "
        "Detalle: No module named 'x.y'. Acción sugerida: instala la dependencia."
    )
    assert runtime.formatear_error(exc) == (
        "Error de ejecución: "
        "Error de importación GUI en 'pcobra.gui.runtime': faltante detectado 'x.y'. "
        "Detalle: No module named 'x.y'. Acción sugerida: instala la dependencia."
    )


def test_formatear_error_lexico_y_sintactico_sin_recargar_dependencias(monkeypatch) -> None:
    class FakeLexerError(Exception):
        def __init__(self):
            self.linea = 7
            self.columna = 3
            super().__init__("token inesperado")

    class FakeParserError(Exception):
        pass

    llamadas = {"count": 0}

    def _fail_if_called():
        llamadas["count"] += 1
        raise AssertionError("formatear_error no debe recargar dependencias")

    monkeypatch.setattr(runtime, "require_gui_dependencies", _fail_if_called)

    assert runtime.formatear_error(
        FakeLexerError(),
        lexer_error_type=FakeLexerError,
        parser_error_type=FakeParserError,
    ).startswith("Error léxico (línea 7, columna 3)")
    assert runtime.formatear_error(
        FakeParserError("faltó ')'"),
        lexer_error_type=FakeLexerError,
        parser_error_type=FakeParserError,
    ) == "Error de sintaxis: faltó ')'"
    assert llamadas["count"] == 0
