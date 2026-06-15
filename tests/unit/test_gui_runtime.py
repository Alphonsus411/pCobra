"""Pruebas unitarias para el runtime compartido de GUI."""

from __future__ import annotations

from pathlib import Path
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


def test_transpilar_codigo_usa_transpilador_python_registrado(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    llamadas = {"transpiler_inits": 0, "ast": None}

    class FakeLexer:
        def __init__(self, codigo: str):
            self.codigo = codigo

        def tokenizar(self):
            assert self.codigo == "imprimir('Hola')"
            return ["TOKEN"]

    class FakeParser:
        def __init__(self, tokens):
            assert tokens == ["TOKEN"]

        def parsear(self):
            return ["AST"]

    class TranspiladorPythonRegistrado:
        def __init__(self):
            llamadas["transpiler_inits"] += 1

        def generate_code(self, ast):
            llamadas["ast"] = ast
            return "codigo python registrado"

    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {
            "Lexer": FakeLexer,
            "Parser": FakeParser,
            "TRANSPILERS": {"python": TranspiladorPythonRegistrado},
        },
    )

    assert (
        runtime.transpilar_codigo("imprimir('Hola')", "python")
        == "codigo python registrado"
    )
    assert llamadas == {"transpiler_inits": 1, "ast": ["AST"]}

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


def test_accion_nuevo_archivo_reinicia_estado() -> None:
    estado = runtime.GuiFileState(
        ruta=Path("programa.cobra"),
        contenido_cargado="imprimir('x')",
        cambios_sin_guardar=True,
    )

    contenido, mensaje = runtime.crear_archivo_nuevo_en_editor(estado)

    assert contenido == ""
    assert mensaje == "Archivo nuevo creado en memoria."
    assert estado == runtime.GuiFileState()


def test_accion_abrir_archivo_desde_ruta(tmp_path: Path) -> None:
    archivo = tmp_path / "programa.cobra"
    archivo.write_text("imprimir('hola')", encoding="utf-8")
    estado = runtime.GuiFileState()

    contenido, mensaje = runtime.abrir_archivo_desde_ruta(archivo, estado)

    assert contenido == "imprimir('hola')"
    assert estado.ruta == archivo.resolve()
    assert estado.contenido_cargado == "imprimir('hola')"
    assert estado.cambios_sin_guardar is False
    assert mensaje == f"Archivo cargado: {archivo.resolve()}"


def test_accion_guardar_archivo_activo(tmp_path: Path) -> None:
    archivo = tmp_path / "programa.cobra"
    archivo.write_text("imprimir('antes')", encoding="utf-8")
    estado = runtime.GuiFileState(
        ruta=archivo.resolve(),
        contenido_cargado="imprimir('antes')",
        cambios_sin_guardar=True,
    )

    contenido, mensaje = runtime.guardar_archivo_activo("imprimir('despues')", estado)

    assert contenido == "imprimir('despues')"
    assert archivo.read_text(encoding="utf-8") == "imprimir('despues')"
    assert estado.contenido_cargado == "imprimir('despues')"
    assert estado.cambios_sin_guardar is False
    assert mensaje == f"Archivo guardado: {archivo.resolve()}"


def test_accion_guardar_archivo_activo_sin_ruta_falla() -> None:
    with pytest.raises(ValueError, match="No hay archivo activo"):
        runtime.guardar_archivo_activo("imprimir('x')", runtime.GuiFileState())


def test_accion_guardar_archivo_como(tmp_path: Path) -> None:
    destino = tmp_path / "nuevo.cobra"
    estado = runtime.GuiFileState()

    contenido, mensaje = runtime.guardar_archivo_como(
        destino, "imprimir('nuevo')", estado
    )

    assert contenido == "imprimir('nuevo')"
    assert destino.read_text(encoding="utf-8") == "imprimir('nuevo')"
    assert estado.ruta == destino.resolve()
    assert estado.contenido_cargado == "imprimir('nuevo')"
    assert estado.cambios_sin_guardar is False
    assert mensaje == f"Archivo guardado: {destino.resolve()}"


def test_accion_recargar_archivo_activo(tmp_path: Path) -> None:
    archivo = tmp_path / "programa.cobra"
    archivo.write_text("imprimir('disco')", encoding="utf-8")
    estado = runtime.GuiFileState(
        ruta=archivo.resolve(),
        contenido_cargado="imprimir('memoria')",
        cambios_sin_guardar=True,
    )

    contenido, mensaje = runtime.recargar_archivo_activo(estado)

    assert contenido == "imprimir('disco')"
    assert estado.contenido_cargado == "imprimir('disco')"
    assert estado.cambios_sin_guardar is False
    assert mensaje == f"Archivo cargado: {archivo.resolve()}"


def test_accion_cargar_archivo_desde_arbol_filtra_extensiones(tmp_path: Path) -> None:
    archivo = tmp_path / "arbol.co"
    archivo.write_text("imprimir('arbol')", encoding="utf-8")
    estado = runtime.GuiFileState()

    contenido, mensaje = runtime.cargar_archivo_desde_arbol(archivo, estado)

    assert contenido == "imprimir('arbol')"
    assert mensaje == f"Archivo cargado: {archivo.resolve()}"
    with pytest.raises(ValueError, match="archivo Cobra"):
        runtime.cargar_archivo_desde_arbol(tmp_path / "notas.txt", estado)


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


def test_crear_handler_sugerencias_agix_exitosas(monkeypatch: pytest.MonkeyPatch) -> None:
    entrada = SimpleNamespace(value="imprimir('Hola')")
    salida = SimpleNamespace(value="")
    page = SimpleNamespace(update=lambda: setattr(page, "updated", True))

    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {"LexerError": Exception, "ParserError": Exception},
    )
    monkeypatch.setattr(
        runtime,
        "generar_sugerencias",
        lambda codigo: [f"Sugerencia para {codigo}"],
    )

    handler = runtime.crear_handler_sugerencias_agix(
        entrada=entrada, salida=salida, page=page
    )
    handler(None)

    assert salida.value == "Sugerencias de Agix:\n- Sugerencia para imprimir('Hola')"
    assert page.updated is True


def test_crear_handler_sugerencias_agix_dependencia_ausente(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entrada = SimpleNamespace(value="imprimir('Hola')")
    salida = SimpleNamespace(value="")
    page = SimpleNamespace(update=lambda: setattr(page, "updated", True))

    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {"LexerError": Exception, "ParserError": Exception},
    )

    def _generar_sugerencias(_codigo: str) -> list[str]:
        raise ImportError("La dependencia opcional 'agix' no está instalada")

    monkeypatch.setattr(runtime, "generar_sugerencias", _generar_sugerencias)

    handler = runtime.crear_handler_sugerencias_agix(
        entrada=entrada, salida=salida, page=page
    )
    handler(None)

    assert "dependencia opcional agix no está instalada" in salida.value
    assert "pip install agix" in salida.value
    assert "dependencia opcional 'agix'" in salida.value
    assert page.updated is True


def test_crear_handler_sugerencias_agix_error_lexico_sintactico_claro(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLexerError(Exception):
        linea = 3
        columna = 9

    class FakeParserError(Exception):
        pass

    entrada = SimpleNamespace(value="@")
    salida = SimpleNamespace(value="")
    page = SimpleNamespace(update=lambda: setattr(page, "updated", True))

    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {"LexerError": FakeLexerError, "ParserError": FakeParserError},
    )

    def _generar_sugerencias(_codigo: str) -> list[str]:
        raise FakeLexerError("carácter inválido")

    monkeypatch.setattr(runtime, "generar_sugerencias", _generar_sugerencias)

    handler = runtime.crear_handler_sugerencias_agix(
        entrada=entrada, salida=salida, page=page
    )
    handler(None)

    assert salida.value == "Error léxico (línea 3, columna 9): carácter inválido"
    assert page.updated is True
