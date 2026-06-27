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
def _reset_cache(monkeypatch: pytest.MonkeyPatch):
    cache_clear = getattr(runtime.require_gui_dependencies, "cache_clear", None)
    if cache_clear is not None:
        cache_clear()
    motor_cache_clear = getattr(
        runtime.detectar_motor_ia_sugerencias, "cache_clear", None
    )
    if motor_cache_clear is not None:
        motor_cache_clear()
    monkeypatch.setattr(
        runtime,
        "detectar_motor_ia_sugerencias",
        lambda: runtime.MotorIASugerencias(disponible=True),
    )
    yield
    cache_clear = getattr(runtime.require_gui_dependencies, "cache_clear", None)
    if cache_clear is not None:
        cache_clear()
    motor_cache_clear = getattr(
        runtime.detectar_motor_ia_sugerencias, "cache_clear", None
    )
    if motor_cache_clear is not None:
        motor_cache_clear()


def _fake_flet_buttons():
    class ElevatedButton:
        def __init__(self, text, on_click=None, **kwargs):
            self.text = text
            self.on_click = on_click
            self.disabled = kwargs.get("disabled", False)
            self.tooltip = kwargs.get("tooltip", "")

    return SimpleNamespace(ElevatedButton=ElevatedButton)


def test_boton_sugerencias_se_habilita_si_motor_canonico_disponible(monkeypatch):
    handler = object()
    monkeypatch.setattr(
        runtime,
        "detectar_motor_ia_sugerencias",
        lambda: runtime.MotorIASugerencias(disponible=True),
    )

    boton = runtime.crear_boton_sugerencias_libro(
        _fake_flet_buttons(), on_click=handler
    )

    assert boton.text == runtime.SUGERENCIAS_BUTTON_TEXT
    assert boton.disabled is False
    assert boton.on_click is handler
    assert runtime.CANONICAL_SUGGESTION_ENGINE == "agix"
    assert "agi-core" not in boton.tooltip


def test_boton_sugerencias_se_deshabilita_y_menciona_paquete_correcto(monkeypatch):
    monkeypatch.setattr(
        runtime,
        "detectar_motor_ia_sugerencias",
        lambda: runtime.MotorIASugerencias(disponible=False),
    )

    boton = runtime.crear_boton_sugerencias_libro(
        _fake_flet_buttons(), on_click=object()
    )

    assert boton.disabled is True
    assert boton.on_click is None
    assert "agix" in boton.tooltip
    assert "agi-core" not in boton.tooltip


def test_es_archivo_cobra_reconoce_extensiones_seguras_documentadas() -> None:
    assert runtime.COBRA_FILE_EXTENSIONS == (".cobra", ".co")
    assert runtime.es_archivo_cobra("programa.co")
    assert runtime.es_archivo_cobra("modulo.COBRA")
    assert not runtime.es_archivo_cobra("notas.txt")


def test_detectar_tipo_archivo_clasifica_extensiones_y_nombres_conocidos() -> None:
    casos = {
        "programa.cobra": runtime.TIPO_ARCHIVO_COBRA,
        "programa.co": runtime.TIPO_ARCHIVO_COBRA,
        "README.md": runtime.TIPO_ARCHIVO_MARKDOWN,
        "manual.markdown": runtime.TIPO_ARCHIVO_MARKDOWN,
        "notas.txt": runtime.TIPO_ARCHIVO_TEXTO,
        "package.json": runtime.TIPO_ARCHIVO_CONFIG,
        "compose.yml": runtime.TIPO_ARCHIVO_CONFIG,
        "compose.yaml": runtime.TIPO_ARCHIVO_CONFIG,
        "pyproject.toml": runtime.TIPO_ARCHIVO_CONFIG,
        "Dockerfile": runtime.TIPO_ARCHIVO_DOCKER,
        "Dockerfile.dev": runtime.TIPO_ARCHIVO_DOCKER,
        ".gitignore": runtime.TIPO_ARCHIVO_IGNORE,
        ".dockerignore": runtime.TIPO_ARCHIVO_IGNORE,
        ".env.example": runtime.TIPO_ARCHIVO_ENV_EXAMPLE,
        "imagen.png": runtime.TIPO_ARCHIVO_DESCONOCIDO,
    }

    for ruta, tipo_esperado in casos.items():
        assert runtime.detectar_tipo_archivo(ruta) == tipo_esperado


def test_capacidades_archivo_reservan_acciones_cobra_para_codigo_cobra() -> None:
    acciones_cobra = {
        runtime.ACCION_EJECUTAR,
        runtime.ACCION_TOKENS,
        runtime.ACCION_AST,
        runtime.ACCION_SUGERENCIAS,
        runtime.ACCION_CORRECCION,
    }
    acciones_base = {
        runtime.ACCION_EDITAR,
        runtime.ACCION_GUARDAR,
        runtime.ACCION_RECARGAR,
        runtime.ACCION_BORRAR,
    }

    assert acciones_cobra <= runtime.obtener_capacidades_archivo("programa.cobra")
    assert acciones_base <= runtime.obtener_capacidades_archivo("programa.cobra")

    for ruta in [
        "README.md",
        "notas.txt",
        "package.json",
        "Dockerfile",
        ".gitignore",
        ".env.example",
        "imagen.png",
    ]:
        capacidades = runtime.obtener_capacidades_archivo(ruta)
        assert capacidades == acciones_base
        assert not any(
            runtime.archivo_permite_accion(ruta, accion) for accion in acciones_cobra
        )


def test_listar_directorio_cobra_modo_seguro_filtra_archivos_no_cobra(
    tmp_path: Path,
) -> None:
    (tmp_path / "zeta").mkdir()
    (tmp_path / "beta.co").write_text("", encoding="utf-8")
    (tmp_path / "alfa.cobra").write_text("", encoding="utf-8")
    (tmp_path / "ignorado.py").write_text("", encoding="utf-8")
    (tmp_path / "README.md").write_text("", encoding="utf-8")

    assert runtime.MOSTRAR_TODOS_LOS_ARCHIVOS_IDLE is False
    assert [path.name for path in runtime.listar_directorio_cobra(tmp_path)] == [
        "zeta",
        "alfa.cobra",
        "beta.co",
    ]


def test_listar_directorio_cobra_opcion_interna_muestra_todos_los_archivos(
    tmp_path: Path,
) -> None:
    (tmp_path / "zeta").mkdir()
    (tmp_path / "beta.co").write_text("", encoding="utf-8")
    (tmp_path / "alfa.cobra").write_text("", encoding="utf-8")
    (tmp_path / "README.md").write_text("", encoding="utf-8")
    (tmp_path / "script.py").write_text("", encoding="utf-8")

    assert [
        path.name
        for path in runtime.listar_directorio_cobra(tmp_path, mostrar_todos=True)
    ] == [
        "zeta",
        "alfa.cobra",
        "beta.co",
        "README.md",
        "script.py",
    ]


def test_crear_arbol_directorios_acepta_root_path_path_y_str_con_entradas_reales(
    tmp_path: Path,
) -> None:
    class Text:
        def __init__(self, value="", **_kwargs):
            self.value = value

    class Icon:
        def __init__(self, name):
            self.name = name

    class ListTile:
        def __init__(self, title=None, leading=None, data=None, on_click=None):
            self.title = title
            self.leading = leading
            self.data = data
            self.on_click = on_click

    class ExpansionTile:
        def __init__(self, title=None, leading=None, controls=None):
            self.title = title
            self.leading = leading
            self.controls = controls or []

    class Column:
        def __init__(self, controls=None, **kwargs):
            self.controls = controls or []
            self.scroll = kwargs.get("scroll")

    ft = SimpleNamespace(
        Text=Text,
        Icon=Icon,
        ListTile=ListTile,
        ExpansionTile=ExpansionTile,
        Column=Column,
        Icons=SimpleNamespace(INSERT_DRIVE_FILE="file", FOLDER="folder"),
        ScrollMode=SimpleNamespace(ALWAYS="always"),
    )
    (tmp_path / "programa.cobra").write_text("imprimir('cobra')", encoding="utf-8")
    (tmp_path / "modulo.co").write_text("imprimir('co')", encoding="utf-8")

    arbol_desde_path = runtime.crear_arbol_directorios(
        ft, on_click=lambda _e: None, root_path=tmp_path
    )
    arbol_desde_str = runtime.crear_arbol_directorios(
        ft, on_click=lambda _e: None, root_path=str(tmp_path)
    )

    assert [control.title.value for control in arbol_desde_path.controls] == [
        "modulo.co",
        "programa.cobra",
    ]
    assert [control.title.value for control in arbol_desde_str.controls] == [
        "modulo.co",
        "programa.cobra",
    ]
    assert all(
        Path(control.data).exists()
        for arbol in (arbol_desde_path, arbol_desde_str)
        for control in arbol.controls
    )


def test_crear_arbol_directorios_sin_root_path_usa_workspace_idle(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class Text:
        def __init__(self, value=None, **_kwargs):
            self.value = value

    class Column:
        def __init__(self, controls=None, **kwargs):
            self.controls = controls or []
            self.scroll = kwargs.get("scroll")

    ft = SimpleNamespace(
        Text=Text,
        Column=Column,
        ScrollMode=SimpleNamespace(ALWAYS="always"),
    )
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    llamadas = []

    def fake_resolver_workspace_root_idle() -> Path:
        llamadas.append("resolver")
        return workspace

    monkeypatch.setattr(
        runtime, "resolver_workspace_root_idle", fake_resolver_workspace_root_idle
    )

    arbol = runtime.crear_arbol_directorios(ft, on_click=lambda _e: None)

    assert llamadas == ["resolver"]
    assert arbol.scroll == ft.ScrollMode.ALWAYS
    assert arbol.controls[0].value == "No hay archivos Cobra en esta carpeta"


def test_crear_arbol_directorios_propaga_file_not_found_en_ruta_inexistente(
    tmp_path: Path,
) -> None:
    ft = SimpleNamespace()
    ruta_inexistente = tmp_path / "no_existe"

    with pytest.raises(FileNotFoundError):
        runtime.crear_arbol_directorios(
            ft, on_click=lambda _e: None, root_path=ruta_inexistente
        )


def test_crear_arbol_directorios_propaga_permission_error_sin_tocar_permisos(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    ft = SimpleNamespace()

    def fake(_root_path):
        raise PermissionError("sin permiso portable")

    monkeypatch.setattr(runtime, "listar_directorio_cobra", fake)

    with pytest.raises(PermissionError, match="sin permiso portable"):
        runtime.crear_arbol_directorios(
            ft, on_click=lambda _e: None, root_path=tmp_path
        )


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
    """La ruta común de sugerencias debe ejecutar Lexer/Parser antes del motor opcional."""

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
    assert "- Léxico/sintaxis:" in reporte
    assert "- Estilo:" in reporte
    assert "- Nombres:" in reporte
    assert "- Forma canónica:" in reporte
    assert "- Observabilidad:" in reporte


def test_generar_reporte_sugerencias_sin_motor_no_importa_ia(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sin motor IA instalado, la GUI conserva validación y muestra aviso seguro."""

    llamadas: list[str] = []

    def analizar_primero(codigo: str):
        llamadas.append(f"analizar:{codigo}")
        return ["TOKEN"], ["AST"]

    def no_debe_importar_ia(_codigo: str):
        raise AssertionError("No debe cargar la integración IA si el motor falta")

    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {"LexerError": Exception, "ParserError": Exception},
    )
    monkeypatch.setattr(runtime, "analizar_codigo", analizar_primero)
    monkeypatch.setattr(runtime, "generar_sugerencias", no_debe_importar_ia)
    monkeypatch.setattr(
        runtime,
        "detectar_motor_ia_sugerencias",
        lambda: runtime.MotorIASugerencias(
            disponible=False,
            detalle="Sugerencias deshabilitadas: falta 'agix'.",
        ),
    )

    reporte = runtime.generar_reporte_sugerencias("var x = 5")

    assert llamadas == ["analizar:var x = 5"]
    assert "No se detectaron errores" in reporte
    assert "Sugerencias deshabilitadas" in reporte
    assert "falta 'agix'" in reporte


def test_generar_reporte_sugerencias_devuelve_error_parser_sin_correcciones(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si Parser falla, no se consulta el motor opcional ni se proponen correcciones aplicables."""

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
    assert "Sugerencias del Libro:" in reporte
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
    assert "Sugerencias del Libro:" in reporte
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


@pytest.mark.parametrize(
    ("codigo", "esperado"),
    [
        ("var x = 5", "Sugerencias del Libro:"),
        ("var x =", "Error de sintaxis"),
        ("var x = 5 ¿", "Error léxico"),
    ],
)
def test_ruta_sugerencias_cubre_fixtures_minimos_reales_de_cobra(
    monkeypatch: pytest.MonkeyPatch, codigo: str, esperado: str
) -> None:
    """Fixtures mínimos reales: declaración válida y errores Lexer/Parser."""

    monkeypatch.setattr(runtime, "require_gui_dependencies", _deps_lexer_parser_reales)
    llamadas_sugerencias: list[str] = []

    def sugerir_solo_si_parsea(codigo_validado: str) -> list[str]:
        llamadas_sugerencias.append(codigo_validado)
        return ["Usar nombres descriptivos para variables"]

    monkeypatch.setattr(runtime, "generar_sugerencias", sugerir_solo_si_parsea)

    reporte = runtime.generar_reporte_sugerencias(codigo)

    assert esperado in reporte
    if codigo == "var x = 5":
        assert llamadas_sugerencias == [codigo]
        assert "No se detectaron errores con el Lexer y Parser de Cobra" in reporte
        assert "- Usar nombres descriptivos para variables" in reporte
    else:
        assert llamadas_sugerencias == []
        assert "Corrige primero los errores anteriores" in reporte
        assert "- Usar nombres descriptivos para variables" not in reporte


def test_ruta_sugerencias_parser_fallido_no_expone_correccion_aplicable_real(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Un ParserError real corta la ruta antes del motor opcional y de reglas aplicables."""

    monkeypatch.setattr(runtime, "require_gui_dependencies", _deps_lexer_parser_reales)

    def no_sugerir(_codigo: str) -> list[str]:
        raise AssertionError("No debe proponer correcciones si Parser falla")

    monkeypatch.setattr(runtime, "generar_sugerencias", no_sugerir)

    reporte = runtime.generar_reporte_sugerencias("var x =")

    assert reporte.startswith("Errores léxicos/sintácticos:")
    assert "Error de sintaxis" in reporte
    assert "Corrige primero los errores anteriores" in reporte
    assert "Sugerencias del Libro:" in reporte
    assert "Usar nombres descriptivos" not in reporte


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


def test_gui_target_choices_filtra_targets_no_oficiales(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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


def test_accion_abrir_archivo_desde_ruta(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    archivo = tmp_path / "programa.cobra"
    archivo.write_text("imprimir('hola')", encoding="utf-8")
    estado = runtime.GuiFileState()

    contenido, mensaje = runtime.abrir_archivo_desde_ruta(archivo, estado)

    assert contenido == "imprimir('hola')"
    assert estado.ruta == archivo.resolve()
    assert estado.contenido_cargado == "imprimir('hola')"
    assert estado.cambios_sin_guardar is False
    assert mensaje == f"Archivo cargado: {archivo.resolve()}"


def test_accion_guardar_archivo_activo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
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


def test_accion_guardar_archivo_como(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
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


def test_accion_abrir_archivo_respeta_sandbox_con_ruta_absoluta(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    archivo = tmp_path / "programa.cobra"
    archivo.write_text("imprimir('sandbox')", encoding="utf-8")
    estado = runtime.GuiFileState()

    contenido, mensaje = runtime.abrir_archivo_desde_ruta(archivo.resolve(), estado)

    assert contenido == "imprimir('sandbox')"
    assert estado.ruta == archivo.resolve()
    assert mensaje == f"Archivo cargado: {archivo.resolve()}"


def test_accion_guardar_archivo_activo_respeta_sandbox(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    archivo = tmp_path / "programa.cobra"
    archivo.write_text("imprimir('antes')", encoding="utf-8")
    estado = runtime.GuiFileState(ruta=archivo.resolve(), cambios_sin_guardar=True)

    contenido, mensaje = runtime.guardar_archivo_activo("imprimir('despues')", estado)

    assert contenido == "imprimir('despues')"
    assert archivo.read_text(encoding="utf-8") == "imprimir('despues')"
    assert estado.ruta == archivo.resolve()
    assert estado.cambios_sin_guardar is False
    assert mensaje == f"Archivo guardado: {archivo.resolve()}"


def test_accion_guardar_archivo_como_respeta_sandbox_con_ruta_relativa(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    estado = runtime.GuiFileState()

    contenido, mensaje = runtime.guardar_archivo_como(
        "nuevo.cobra", "imprimir('nuevo')", estado
    )

    destino = tmp_path / "nuevo.cobra"
    assert contenido == "imprimir('nuevo')"
    assert destino.read_text(encoding="utf-8") == "imprimir('nuevo')"
    assert estado.ruta == destino.resolve()
    assert mensaje == f"Archivo guardado: {destino.resolve()}"


@pytest.mark.parametrize(
    ("accion", "argumentos"),
    [
        ("abrir", lambda fuera: (fuera,)),
        ("guardar", lambda fuera: (fuera, "imprimir('x')")),
        ("guardar_como", lambda fuera: (fuera, "imprimir('x')")),
    ],
)
def test_acciones_archivo_rechazan_rutas_fuera_del_sandbox(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    accion: str,
    argumentos,
) -> None:
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    fuera = tmp_path.parent / "fuera.cobra"
    fuera.write_text("imprimir('fuera')", encoding="utf-8")
    estado = runtime.GuiFileState(ruta=fuera if accion == "guardar" else None)

    with pytest.raises(ValueError, match="fuera del directorio permitido"):
        if accion == "abrir":
            runtime.abrir_archivo_desde_ruta(*argumentos(fuera), estado)
        elif accion == "guardar":
            runtime.guardar_archivo_activo(argumentos(fuera)[1], estado)
        else:
            runtime.guardar_archivo_como(*argumentos(fuera), estado)


def test_accion_recargar_archivo_activo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
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


def test_accion_cargar_archivo_desde_arbol_filtra_extensiones(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
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
                "No module named 'pcobra.core.interpreter'",
                name="pcobra.core.interpreter",
            )
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", _import_fail_core)

    with pytest.raises(
        RuntimeError, match="faltante detectado 'pcobra.core.interpreter'"
    ) as excinfo:
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

    with pytest.raises(
        RuntimeError, match="faltante detectado 'pcobra.cobra.core.Lexer'"
    ) as excinfo:
        runtime.require_gui_dependencies()
    assert "corrige el import local de 'pcobra.cobra.core.Lexer'" in str(excinfo.value)


def test_require_gui_dependencies_cachea_resultado(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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


def test_formatear_error_lexico_y_sintactico_sin_recargar_dependencias(
    monkeypatch,
) -> None:
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
    assert (
        runtime.formatear_error(
            FakeParserError("faltó ')'"),
            lexer_error_type=FakeLexerError,
            parser_error_type=FakeParserError,
        )
        == "Error de sintaxis: faltó ')'"
    )
    assert llamadas["count"] == 0


def test_crear_handler_sugerencias_usa_ruta_canonica(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entrada = SimpleNamespace(value="imprimir('Hola')")
    salida = SimpleNamespace(value="")
    page = SimpleNamespace(updated=False, update=lambda: setattr(page, "updated", True))
    llamadas: list[str] = []

    def _generar_reporte(codigo: str) -> str:
        llamadas.append(codigo)
        return "reporte común"

    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {"LexerError": Exception, "ParserError": Exception},
    )
    monkeypatch.setattr(runtime, "generar_reporte_sugerencias", _generar_reporte)

    handler = runtime.crear_handler_sugerencias(
        entrada=entrada, salida=salida, page=page
    )
    handler(None)

    assert llamadas == ["imprimir('Hola')"]
    assert salida.value == "reporte común"
    assert page.updated is True


def test_crear_handler_sugerencias_agix_es_alias_deprecado_interno(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entrada = SimpleNamespace(value="imprimir('Hola')")
    salida = SimpleNamespace(value="")
    page = SimpleNamespace(updated=False)
    llamadas = []

    def _handler(evento: object) -> None:
        llamadas.append((entrada, salida, page, evento))
        salida.value = "reporte común"
        page.updated = True

    def _crear_handler_sugerencias(**kwargs: object) -> object:
        assert kwargs == {"entrada": entrada, "salida": salida, "page": page}
        return _handler

    monkeypatch.setattr(
        runtime, "crear_handler_sugerencias", _crear_handler_sugerencias
    )

    with pytest.warns(DeprecationWarning, match="crear_handler_sugerencias"):
        handler = runtime.crear_handler_sugerencias_agix(
            entrada=entrada, salida=salida, page=page
        )
    handler(None)

    assert llamadas == [(entrada, salida, page, None)]
    assert salida.value == "reporte común"
    assert page.updated is True


def test_guardar_como_por_ruta_y_filepicker_actualizan_estado_igual(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    destino_ruta = tmp_path / "desde_ruta.cobra"
    destino_picker = tmp_path / "desde_picker.cobra"
    codigo = "imprimir('mismo')"

    estado_ruta = runtime.GuiFileState(cambios_sin_guardar=True)
    contenido, mensaje = runtime.guardar_archivo_como(destino_ruta, codigo, estado_ruta)

    picker_creados = []

    class Text:
        def __init__(self, value="", **_kwargs):
            self.value = value

    class FilePicker:
        def __init__(self, on_result=None):
            self.on_result = on_result
            self.save_file_args = None
            picker_creados.append(self)

        def save_file(self, **kwargs):
            self.save_file_args = kwargs

    flet_runtime = SimpleNamespace(Text=Text, FilePicker=FilePicker)
    monkeypatch.setattr(runtime, "require_flet", lambda: flet_runtime)

    estado_picker = runtime.GuiFileState(cambios_sin_guardar=True)
    entrada = SimpleNamespace(value=codigo)
    page = SimpleNamespace(
        overlay=[],
        snack_bar=SimpleNamespace(open=False, content=None),
        update=lambda: None,
    )

    handler = runtime.crear_handler_guardar_como(
        entrada=entrada, estado_archivo=estado_picker, page=page
    )
    handler(None)
    assert page.overlay == picker_creados
    picker_creados[0].on_result(SimpleNamespace(path=str(destino_picker)))

    assert contenido == codigo
    assert destino_ruta.read_text(encoding="utf-8") == codigo
    assert destino_picker.read_text(encoding="utf-8") == codigo
    assert estado_ruta.ruta == destino_ruta.resolve()
    assert estado_picker.ruta == destino_picker.resolve()
    assert estado_ruta.contenido_cargado == estado_picker.contenido_cargado == codigo
    assert estado_ruta.cambios_sin_guardar is estado_picker.cambios_sin_guardar is False
    assert mensaje == f"Archivo guardado: {destino_ruta.resolve()}"
    assert page.snack_bar.open is True
    assert (
        page.snack_bar.content.value == f"Archivo guardado: {destino_picker.resolve()}"
    )


def test_guardar_como_filepicker_usa_mensaje_de_exito_compartido(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    destino = tmp_path / "mensaje.cobra"

    class Text:
        def __init__(self, value="", **_kwargs):
            self.value = value

    class FilePicker:
        def __init__(self, on_result=None):
            self.on_result = on_result

        def save_file(self, **_kwargs):
            pass

    picker = None

    class CapturingFilePicker(FilePicker):
        def __init__(self, on_result=None):
            nonlocal picker
            super().__init__(on_result=on_result)
            picker = self

    monkeypatch.setattr(
        runtime,
        "require_flet",
        lambda: SimpleNamespace(Text=Text, FilePicker=CapturingFilePicker),
    )
    page = SimpleNamespace(
        overlay=[],
        snack_bar=SimpleNamespace(open=False, content=None),
        update=lambda: None,
    )
    estado = runtime.GuiFileState()
    handler = runtime.crear_handler_guardar_como(
        entrada=SimpleNamespace(value="imprimir('ok')"),
        estado_archivo=estado,
        page=page,
    )

    handler(None)
    picker.on_result(SimpleNamespace(path=str(destino)))

    assert page.snack_bar.content.value == f"Archivo guardado: {destino.resolve()}"
    assert estado.ruta == destino.resolve()
    assert estado.contenido_cargado == "imprimir('ok')"
    assert estado.cambios_sin_guardar is False


def test_resolver_ruta_archivo_en_project_root_relativa_y_extension_por_defecto(
    tmp_path: Path,
) -> None:
    destino = runtime.resolver_ruta_archivo_en_project_root("src/programa", tmp_path)

    assert destino == (tmp_path / "src" / "programa.cobra").resolve()


@pytest.mark.parametrize(
    ("ruta", "esperado"),
    [
        ("main", "main.cobra"),
        ("src/main", "src/main.cobra"),
        ("main.co", "main.co"),
        ("main.cobra", "main.cobra"),
    ],
)
def test_resolver_ruta_archivo_en_project_root_normaliza_extensiones_cobra(
    tmp_path: Path, ruta: str, esperado: str
) -> None:
    destino = runtime.resolver_ruta_archivo_en_project_root(ruta, tmp_path)

    assert destino == (tmp_path / esperado).resolve()


def test_resolver_ruta_archivo_en_project_root_rechaza_extension_no_cobra(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="extensión .cobra o .co"):
        runtime.resolver_ruta_archivo_en_project_root("main.txt", tmp_path)


def test_resolver_ruta_archivo_en_project_root_acepta_absoluta_interna(
    tmp_path: Path,
) -> None:
    archivo = tmp_path / "programa.co"

    destino = runtime.resolver_ruta_archivo_en_project_root(archivo, tmp_path)

    assert destino == archivo.resolve()


def test_resolver_ruta_archivo_en_project_root_rechaza_absoluta_externa(
    tmp_path: Path,
) -> None:
    archivo_externo = tmp_path.parent / "externo_idle_helper.cobra"
    archivo_externo.write_text("imprimir('externo')", encoding="utf-8")

    try:
        with pytest.raises(ValueError, match="dentro de la raíz del proyecto"):
            runtime.resolver_ruta_archivo_en_project_root(archivo_externo, tmp_path)
    finally:
        archivo_externo.unlink(missing_ok=True)


@pytest.mark.parametrize("ruta", ["../escape.cobra", "programa.txt"])
def test_resolver_ruta_archivo_en_project_root_rechaza_rutas_invalidas(
    tmp_path: Path, ruta: str
) -> None:
    with pytest.raises(ValueError):
        runtime.resolver_ruta_archivo_en_project_root(ruta, tmp_path)


def test_resolver_ruta_archivo_en_project_root_rechaza_directorios(
    tmp_path: Path,
) -> None:
    directorio = tmp_path / "directorio.cobra"
    directorio.mkdir()

    with pytest.raises(NotADirectoryError):
        runtime.resolver_ruta_archivo_en_project_root(directorio, tmp_path)


def test_resolver_ruta_archivo_en_project_root_rechaza_directorio_sin_extension(
    tmp_path: Path,
) -> None:
    directorio = tmp_path / "directorio"
    directorio.mkdir()

    with pytest.raises(NotADirectoryError):
        runtime.resolver_ruta_archivo_en_project_root(directorio, tmp_path)


def test_resolver_ruta_archivo_en_project_root_rechaza_symlink_externo(
    tmp_path: Path,
) -> None:
    externo = tmp_path.parent / "externo_idle_helper.cobra"
    externo.write_text("imprimir('externo')", encoding="utf-8")
    enlace = tmp_path / "enlace.cobra"
    enlace.symlink_to(externo)

    try:
        with pytest.raises(ValueError, match="dentro de la raíz del proyecto"):
            runtime.resolver_ruta_archivo_en_project_root(enlace, tmp_path)
    finally:
        externo.unlink(missing_ok=True)
