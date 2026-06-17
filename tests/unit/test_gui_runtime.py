"""Pruebas unitarias para el runtime compartido de GUI."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from pcobra.cobra.core import Lexer, LexerError, Parser, ParserError
from pcobra.gui import runtime


def _deps_lexer_parser_reales() -> dict[str, object]:
    return {
        "Lexer": Lexer,
        "LexerError": LexerError,
        "Parser": Parser,
        "ParserError": ParserError,
    }


@pytest.fixture(autouse=True)
def _reset_cache():
    cache_clear = getattr(runtime.require_gui_dependencies, "cache_clear", None)
    if cache_clear is not None:
        cache_clear()
    yield
    cache_clear = getattr(runtime.require_gui_dependencies, "cache_clear", None)
    if cache_clear is not None:
        cache_clear()


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


def test_generar_reporte_sugerencias_valida_antes_de_sugerir(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """La ruta común de sugerencias debe ejecutar Lexer/Parser antes de Agix."""

    llamadas: list[str] = []

    def analizar_primero(codigo: str):
        llamadas.append(f"analizar:{codigo}")
        return ["TOKEN"], ["AST"]

    def sugerir_despues(codigo: str):
        llamadas.append(f"sugerir:{codigo}")
        return ["Usar nombres descriptivos para variables"]

    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {"LexerError": Exception, "ParserError": Exception},
    )
    monkeypatch.setattr(runtime, "analizar_codigo", analizar_primero)
    monkeypatch.setattr(runtime, "generar_sugerencias", sugerir_despues)

    reporte = runtime.generar_reporte_sugerencias("var x = 5")

    assert llamadas == ["analizar:var x = 5", "sugerir:var x = 5"]
    assert "No se detectaron errores" in reporte
    assert "- Usar nombres descriptivos para variables" in reporte


def test_generar_reporte_sugerencias_devuelve_error_parser_sin_correcciones(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si Parser falla, no se consulta Agix ni se proponen correcciones aplicables."""

    class FakeLexerError(Exception):
        pass

    class FakeParserError(Exception):
        pass

    def analizar_con_error_parser(_codigo: str):
        raise FakeParserError("Token inesperado en término: EOF")

    def no_debe_llamarse(_codigo: str):
        raise AssertionError("generar_sugerencias no debe ejecutarse tras ParserError")

    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {"LexerError": FakeLexerError, "ParserError": FakeParserError},
    )
    monkeypatch.setattr(runtime, "analizar_codigo", analizar_con_error_parser)
    monkeypatch.setattr(runtime, "generar_sugerencias", no_debe_llamarse)

    reporte = runtime.generar_reporte_sugerencias("var x =")

    assert reporte.startswith("Errores léxicos/sintácticos:")
    assert "Error de sintaxis" in reporte
    assert "Sugerencias estilísticas:" in reporte
    assert "Corrige primero los errores anteriores" in reporte
    assert "Usar nombres descriptivos" not in reporte


def test_generar_reporte_sugerencias_devuelve_error_lexer_sin_correcciones(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si Lexer falla, el reporte prioriza el error léxico y bloquea sugerencias."""

    class FakeLexerError(Exception):
        linea = 1
        columna = 11

    class FakeParserError(Exception):
        pass

    def analizar_con_error_lexer(_codigo: str):
        raise FakeLexerError("Token no reconocido: '¿'")

    def no_debe_llamarse(_codigo: str):
        raise AssertionError("generar_sugerencias no debe ejecutarse tras LexerError")

    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {"LexerError": FakeLexerError, "ParserError": FakeParserError},
    )
    monkeypatch.setattr(runtime, "analizar_codigo", analizar_con_error_lexer)
    monkeypatch.setattr(runtime, "generar_sugerencias", no_debe_llamarse)

    reporte = runtime.generar_reporte_sugerencias("var x = 5 ¿")

    assert reporte.startswith("Errores léxicos/sintácticos:")
    assert "Error léxico" in reporte
    assert "Sugerencias estilísticas:" in reporte
    assert "Corrige primero los errores anteriores" in reporte
    assert "Usar nombres descriptivos" not in reporte


def test_generar_reporte_sugerencias_codigo_cobra_valido_con_fixture_minimo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fixture mínimo con tokens y declaración soportados por Lexer/Parser."""

    llamadas: list[str] = []

    def analizar_fixture_minimo(codigo: str):
        llamadas.append(codigo)
        return ["VAR", "IDENTIFICADOR", "ASIGNAR", "ENTERO"], ["NodoAsignacion"]

    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {"LexerError": Exception, "ParserError": Exception},
    )
    monkeypatch.setattr(runtime, "analizar_codigo", analizar_fixture_minimo)
    monkeypatch.setattr(
        runtime,
        "generar_sugerencias",
        lambda _codigo: ["Usar nombres descriptivos para variables"],
    )

    reporte = runtime.generar_reporte_sugerencias("var x = 5")

    assert "No se detectaron errores con el Lexer y Parser de Cobra" in reporte
    assert "- Usar nombres descriptivos para variables" in reporte
    assert llamadas == ["var x = 5"]


def test_generar_reporte_sugerencias_codigo_valido_usa_lexer_parser_reales(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Con código Cobra válido, la GUI solo sugiere después del Lexer/Parser real."""

    monkeypatch.setattr(runtime, "require_gui_dependencies", _deps_lexer_parser_reales)
    llamadas: list[str] = []

    def sugerir_tras_validacion(codigo: str) -> list[str]:
        llamadas.append(codigo)
        return [
            "Usar nombres descriptivos para variables "
            "[regla: LP-3.1-NOMBRES-DESCRIPTIVOS; §3.1 Léxico]"
        ]

    monkeypatch.setattr(runtime, "generar_sugerencias", sugerir_tras_validacion)

    reporte = runtime.generar_reporte_sugerencias("var x = 5")

    assert llamadas == ["var x = 5"]
    assert "No se detectaron errores con el Lexer y Parser de Cobra" in reporte
    assert "LP-3.1-NOMBRES-DESCRIPTIVOS" in reporte
    assert "- Usar nombres descriptivos para variables" in reporte


@pytest.mark.parametrize(
    "codigo_invalido, tipo_error",
    [
        ("var x = 5 ¿", "Error léxico"),
        ("var x =", "Error de sintaxis"),
    ],
)
def test_generar_reporte_sugerencias_codigo_invalido_real_bloquea_estilo(
    monkeypatch: pytest.MonkeyPatch, codigo_invalido: str, tipo_error: str
) -> None:
    """La GUI muestra el error real y no genera sugerencias estilísticas aplicables."""

    monkeypatch.setattr(runtime, "require_gui_dependencies", _deps_lexer_parser_reales)

    def no_debe_sugerir(_codigo: str) -> list[str]:
        raise AssertionError("No se deben sugerir estilos con código inválido")

    monkeypatch.setattr(runtime, "generar_sugerencias", no_debe_sugerir)

    reporte = runtime.generar_reporte_sugerencias(codigo_invalido)

    assert reporte.startswith("Errores léxicos/sintácticos:")
    assert tipo_error in reporte
    assert "Corrige primero los errores anteriores" in reporte
    assert "LP-3.1-NOMBRES-DESCRIPTIVOS" not in reporte
    assert "Usar nombres descriptivos para variables" not in reporte


def test_generar_reporte_sugerencias_no_ejecuta_ia_hasta_lexer_y_parser_reales(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Código válido: la GUI obtiene sugerencias solo después del Lexer/Parser reales."""

    monkeypatch.setattr(runtime, "require_gui_dependencies", _deps_lexer_parser_reales)
    eventos: list[str] = []
    analizar_real = runtime.analizar_codigo

    def analizar_con_traza(codigo: str):
        eventos.append("lexer_parser")
        tokens, ast = analizar_real(codigo)
        assert tokens
        assert ast
        return tokens, ast

    def sugerir_con_traza(codigo: str) -> list[str]:
        eventos.append("sugerencias")
        assert eventos == ["lexer_parser", "sugerencias"]
        return [
            "Usar nombres descriptivos para variables "
            "[regla: LP-3.1-NOMBRES-DESCRIPTIVOS; §3.1 Léxico]"
        ]

    monkeypatch.setattr(runtime, "analizar_codigo", analizar_con_traza)
    monkeypatch.setattr(runtime, "generar_sugerencias", sugerir_con_traza)

    reporte = runtime.generar_reporte_sugerencias("var x = 5")

    assert eventos == ["lexer_parser", "sugerencias"]
    assert "No se detectaron errores con el Lexer y Parser de Cobra" in reporte
    assert "LP-3.1-NOMBRES-DESCRIPTIVOS" in reporte


@pytest.mark.parametrize(
    ("codigo_invalido", "tipo_error"),
    [
        ("var x = 5 ¿", "Error léxico"),
        ("var x =", "Error de sintaxis"),
    ],
)
def test_generar_reporte_sugerencias_gui_rechaza_invalidos_reales_sin_estilo_aplicable(
    monkeypatch: pytest.MonkeyPatch, codigo_invalido: str, tipo_error: str
) -> None:
    """Errores reales del Lexer/Parser se muestran en GUI y bloquean reglas de estilo."""

    monkeypatch.setattr(runtime, "require_gui_dependencies", _deps_lexer_parser_reales)
    llamadas_sugerencias = 0

    def no_sugerir(_codigo: str) -> list[str]:
        nonlocal llamadas_sugerencias
        llamadas_sugerencias += 1
        raise AssertionError("No debe generar sugerencias estilísticas aplicables")

    monkeypatch.setattr(runtime, "generar_sugerencias", no_sugerir)

    reporte = runtime.generar_reporte_sugerencias(codigo_invalido)

    assert llamadas_sugerencias == 0
    assert reporte.startswith("Errores léxicos/sintácticos:")
    assert tipo_error in reporte
    assert "Corrige primero los errores anteriores" in reporte
    assert "LP-3.1-NOMBRES-DESCRIPTIVOS" not in reporte
    assert "Usar nombres descriptivos para variables" not in reporte


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


def test_crear_handler_sugerencias_agix_delega_en_handler_comun(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entrada = SimpleNamespace(value="imprimir('Hola')")
    salida = SimpleNamespace(value="")
    page = SimpleNamespace(update=lambda: setattr(page, "updated", True))
    llamadas = []

    def _reporte(codigo: str) -> str:
        llamadas.append(codigo)
        return "reporte común"

    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {"LexerError": Exception, "ParserError": Exception},
    )
    monkeypatch.setattr(runtime, "generar_reporte_sugerencias", _reporte)

    handler = runtime.crear_handler_sugerencias_agix(
        entrada=entrada, salida=salida, page=page
    )
    handler(None)

    assert llamadas == ["imprimir('Hola')"]
    assert salida.value == "reporte común"
    assert page.updated is True
