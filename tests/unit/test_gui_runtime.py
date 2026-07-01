"""Pruebas unitarias para el runtime compartido de GUI."""

from __future__ import annotations

import ast
import zipfile
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


def test_detectar_tipo_archivo_co_de_texto_sigue_siendo_archivo_cobra(
    tmp_path: Path,
) -> None:
    archivo = tmp_path / "programa.co"
    archivo.write_text("imprimir('hola')\n", encoding="utf-8")

    assert runtime.detectar_tipo_archivo(archivo) == runtime.TIPO_ARCHIVO_COBRA
    assert runtime.es_archivo_cobra(archivo)


def test_detectar_tipo_archivo_co_zip_con_manifest_es_paquete_cobra(
    tmp_path: Path,
) -> None:
    paquete = tmp_path / "paquete.co"
    with zipfile.ZipFile(paquete, "w") as zf:
        zf.writestr("cobra.pkg.json", '{"name":"demo","version":"1.0.0"}')
        zf.writestr("main.co", "imprimir('hola')\n")

    assert runtime.detectar_tipo_archivo(paquete) == runtime.TIPO_ARCHIVO_PAQUETE_COBRA
    assert runtime.es_paquete_cobra_gui(paquete)
    assert not runtime.es_archivo_cobra(paquete)


def test_detectar_tipo_archivo_co_zip_sin_manifest_no_es_paquete_cobra_valido(
    tmp_path: Path,
) -> None:
    archivo = tmp_path / "archivo.co"
    with zipfile.ZipFile(archivo, "w") as zf:
        zf.writestr("main.co", "imprimir('hola')\n")

    assert runtime.detectar_tipo_archivo(archivo) == runtime.TIPO_ARCHIVO_COBRA
    assert not runtime.es_paquete_cobra_gui(archivo)
    assert runtime.es_archivo_cobra(archivo)


def test_cargar_archivo_desde_arbol_no_lee_paquete_cobra_zip_como_texto(
    tmp_path: Path,
) -> None:
    paquete = tmp_path / "paquete.co"
    with zipfile.ZipFile(paquete, "w") as zf:
        zf.writestr("cobra.pkg.json", '{"name":"demo","version":"1.0.0"}')
        zf.writestr("main.co", "imprimir('hola')\n")
    estado = runtime.GuiFileState()

    contenido, mensaje = runtime.cargar_archivo_desde_arbol(paquete, estado)

    assert contenido == ""
    assert "Paquete Cobra seleccionado" in mensaje
    assert estado.ruta == paquete.resolve()
    assert estado.contenido_cargado == ""
    assert not estado.cambios_sin_guardar


def test_detectar_tipo_archivo_clasifica_extensiones_y_nombres_conocidos() -> None:
    casos = {
        "main.cobra": runtime.TIPO_ARCHIVO_COBRA,
        "main.co": runtime.TIPO_ARCHIVO_COBRA,
        "README.md": runtime.TIPO_ARCHIVO_MARKDOWN,
        "README.markdown": runtime.TIPO_ARCHIVO_MARKDOWN,
        "notas.txt": runtime.TIPO_ARCHIVO_TEXTO,
        "docker-compose.yml": runtime.TIPO_ARCHIVO_DOCKER,
        "config.json": runtime.TIPO_ARCHIVO_CONFIG,
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


def test_etiqueta_tipo_archivo_devuelve_textos_visibles() -> None:
    casos = {
        "programa.cobra": "Archivo Cobra",
        "README.md": "Archivo Markdown",
        "notas.txt": "Archivo de texto",
        "pyproject.toml": "Archivo de configuración",
        "Dockerfile": "Archivo Docker",
        ".gitignore": "Archivo ignore",
        ".env.example": "Archivo de entorno de ejemplo",
        "imagen.png": "Archivo de texto",
    }

    for ruta, etiqueta_esperada in casos.items():
        assert runtime.etiqueta_tipo_archivo(ruta) == etiqueta_esperada


def test_crear_titulo_archivo_antepone_etiqueta_y_conserva_asterisco() -> None:
    estado = runtime.GuiFileState(ruta=Path("README.md"), cambios_sin_guardar=True)

    assert runtime.crear_titulo_archivo(estado) == "Archivo Markdown: README.md *"


def test_crear_titulo_archivo_sin_ruta_mantiene_texto_de_archivo_nuevo() -> None:
    estado = runtime.GuiFileState(cambios_sin_guardar=True)

    assert runtime.crear_titulo_archivo(estado) == "Archivo nuevo (sin guardar) *"


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
        "config.json",
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


def test_archivo_permite_accion_bloquea_acciones_cobra_para_archivos_config() -> None:
    acciones_cobra = {
        runtime.ACCION_EJECUTAR,
        runtime.ACCION_TOKENS,
        runtime.ACCION_AST,
        runtime.ACCION_SUGERENCIAS,
        runtime.ACCION_CORRECCION,
    }
    config_file = "config.json"

    for accion in acciones_cobra:
        assert not runtime.archivo_permite_accion(config_file, accion)

    # Verify base actions are still allowed
    assert runtime.archivo_permite_accion(config_file, runtime.ACCION_EDITAR)
    assert runtime.archivo_permite_accion(config_file, runtime.ACCION_GUARDAR)
    assert runtime.archivo_permite_accion(config_file, runtime.ACCION_RECARGAR)
    assert runtime.archivo_permite_accion(config_file, runtime.ACCION_BORRAR)


def test_listar_directorio_cobra_modo_seguro_incluye_texto_auxiliar_clasificado(
    tmp_path: Path,
) -> None:
    (tmp_path / "zeta").mkdir()
    (tmp_path / "beta.co").write_text("", encoding="utf-8")
    (tmp_path / "alfa.cobra").write_text("", encoding="utf-8")
    (tmp_path / "ignorado.py").write_text("", encoding="utf-8")
    (tmp_path / "README.md").write_text("", encoding="utf-8")
    (tmp_path / "notas.txt").write_text("", encoding="utf-8")

    assert [path.name for path in runtime.listar_directorio_cobra(tmp_path)] == [
        "zeta",
        "alfa.cobra",
        "beta.co",
        "ignorado.py",
        "notas.txt",
        "README.md",
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
    assert arbol.controls[0].value == "No hay archivos visibles en esta carpeta"


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

    monkeypatch.setattr(runtime, "listar_directorio_idle", fake)

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
    archivo = tmp_path / "notas.txt"
    archivo.write_text("notas del proyecto", encoding="utf-8")
    estado = runtime.GuiFileState()

    contenido, mensaje = runtime.cargar_archivo_desde_arbol(archivo, estado)

    assert runtime.detectar_tipo_archivo(archivo) == runtime.TIPO_ARCHIVO_TEXTO
    assert not runtime.es_archivo_cobra(archivo)
    assert contenido == "notas del proyecto"
    assert estado.ruta == archivo.resolve()
    assert estado.contenido_cargado == "notas del proyecto"
    assert estado.cambios_sin_guardar is False
    assert mensaje == f"Archivo cargado: {archivo.resolve()}"

    desconocido = tmp_path / "imagen.png"
    desconocido.write_bytes(b"texto plano compatible utf-8")

    contenido_desconocido, mensaje_desconocido = runtime.cargar_archivo_desde_arbol(
        desconocido, estado
    )

    assert (
        runtime.detectar_tipo_archivo(desconocido) == runtime.TIPO_ARCHIVO_DESCONOCIDO
    )
    assert contenido_desconocido == "texto plano compatible utf-8"
    assert estado.ruta == desconocido.resolve()
    assert estado.contenido_cargado == "texto plano compatible utf-8"
    assert mensaje_desconocido == f"Archivo cargado: {desconocido.resolve()}"


def _crear_proyecto_cobra_minimo(tmp_path: Path) -> Path:
    project_root = tmp_path / "paquete_demo"
    (project_root / "src").mkdir(parents=True)
    (project_root / "assets").mkdir()
    (project_root / "src" / "main.cobra").write_text(
        "imprimir('hola paquete')\n", encoding="utf-8"
    )
    (project_root / "README.md").write_text("# Paquete demo\n", encoding="utf-8")
    (project_root / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
    (project_root / "assets" / "recurso.txt").write_text("recurso\n", encoding="utf-8")
    return project_root


def test_idle_crear_paquete_crea_manifest_en_proyecto_minimo(tmp_path: Path) -> None:
    project_root = _crear_proyecto_cobra_minimo(tmp_path)

    manifest = runtime.idle_crear_paquete(project_root, "paquete demo", version="1.2.3")

    assert manifest == project_root / "cobra.pkg.json"
    data = manifest.read_text(encoding="utf-8")
    assert '"name": "paquete-demo"' in data
    assert '"version": "1.2.3"' in data
    assert (project_root / "src" / "main.cobra").read_text(
        encoding="utf-8"
    ) == "imprimir('hola paquete')\n"
    assert (project_root / "README.md").read_text(
        encoding="utf-8"
    ) == "# Paquete demo\n"
    assert (project_root / "Dockerfile").read_text(encoding="utf-8") == "FROM scratch\n"
    assert (project_root / "assets" / "recurso.txt").read_text(
        encoding="utf-8"
    ) == "recurso\n"


def test_idle_construir_y_validar_paquete_incluye_archivos_del_proyecto_minimo(
    tmp_path: Path,
) -> None:
    project_root = _crear_proyecto_cobra_minimo(tmp_path)
    runtime.idle_crear_paquete(project_root, "paquete-demo", version="1.0.0")
    salida = tmp_path / "dist" / "paquete-demo.co"

    paquete = runtime.idle_construir_paquete(project_root, salida)
    inspection = runtime.idle_validar_paquete(paquete)

    assert paquete == salida
    assert inspection.manifest["name"] == "paquete-demo"
    assert inspection.manifest["version"] == "1.0.0"
    assert "src/main.cobra" in inspection.files
    assert "README.md" in inspection.files
    assert "Dockerfile" in inspection.files
    assert "assets/recurso.txt" in inspection.files


def test_idle_abrir_paquete_extrae_proyecto_minimo(tmp_path: Path) -> None:
    project_root = _crear_proyecto_cobra_minimo(tmp_path)
    runtime.idle_crear_paquete(project_root, "paquete-demo", version="1.0.0")
    paquete = runtime.idle_construir_paquete(project_root)
    destino = tmp_path / "extraido"
    destino.mkdir()

    extraido = runtime.idle_abrir_paquete(paquete, destino)

    assert extraido == destino.resolve()
    assert (destino / "src" / "main.cobra").read_text(
        encoding="utf-8"
    ) == "imprimir('hola paquete')\n"
    assert (destino / "README.md").read_text(encoding="utf-8") == "# Paquete demo\n"
    assert (destino / "Dockerfile").read_text(encoding="utf-8") == "FROM scratch\n"
    assert (destino / "assets" / "recurso.txt").read_text(
        encoding="utf-8"
    ) == "recurso\n"


def test_idle_validar_paquete_muestra_error_para_paquete_invalido(tmp_path: Path) -> None:
    paquete = tmp_path / "invalido.co"
    paquete.write_text("no es un zip cobra", encoding="utf-8")

    with pytest.raises(ValueError, match="paquete Cobra válido"):
        runtime.idle_validar_paquete(paquete)


def test_idle_abrir_paquete_falla_si_destino_no_existe(tmp_path: Path) -> None:
    project_root = _crear_proyecto_cobra_minimo(tmp_path)
    runtime.idle_crear_paquete(project_root, "paquete-demo", version="1.0.0")
    paquete = runtime.idle_construir_paquete(project_root)
    destino = tmp_path / "destino-inexistente"

    with pytest.raises(FileNotFoundError, match="Destino de extracción inexistente"):
        runtime.idle_abrir_paquete(paquete, destino)


def test_idle_construir_paquete_falla_si_falta_manifest(tmp_path: Path) -> None:
    project_root = _crear_proyecto_cobra_minimo(tmp_path)

    with pytest.raises(FileNotFoundError, match="Usa 'Crear paquete' antes de construir"):
        runtime.idle_construir_paquete(project_root)


def test_idle_publicar_paquete_expone_fallo_de_publicacion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paquete = tmp_path / "paquete.co"
    paquete.write_text("contenido", encoding="utf-8")

    def publicar_mock(self, ruta: str) -> bool:
        return False

    monkeypatch.setattr(
        "pcobra.cobra.cli.cobrahub_packages.CobraHubPackages.publicar_paquete",
        publicar_mock,
    )

    assert runtime.idle_publicar_paquete(paquete) is False


def test_botones_idle_de_paquetes_delegan_solo_en_helpers_runtime() -> None:
    source = Path("src/pcobra/gui/idle.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    package_handlers = {
        "crear_paquete_handler": "idle_crear_paquete",
        "abrir_paquete_handler": "idle_abrir_paquete",
        "validar_paquete_handler": "idle_validar_paquete",
        "construir_paquete_handler": "idle_construir_paquete",
        "publicar_paquete_handler": "idle_publicar_paquete",
    }
    handler_nodes = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name in package_handlers
    }

    assert set(handler_nodes) == set(package_handlers)
    for handler_name, helper_name in package_handlers.items():
        runtime_calls = [
            call.func.attr
            for call in ast.walk(handler_nodes[handler_name])
            if isinstance(call, ast.Call)
            and isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "runtime"
        ]
        assert helper_name in runtime_calls

    forbidden_imports = {
        "pcobra.cobra.packaging",
        "pcobra.cobra.cli.cobrahub_client",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.module not in forbidden_imports
        elif isinstance(node, ast.Import):
            assert all(alias.name not in forbidden_imports for alias in node.names)


def test_idle_publicar_paquete_delega_en_cobrahub_packages_sin_red(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = _crear_proyecto_cobra_minimo(tmp_path)
    runtime.idle_crear_paquete(project_root, "paquete-demo", version="1.0.0")
    paquete = runtime.idle_construir_paquete(project_root)
    llamadas: list[str] = []

    def publicar_mock(self, ruta: str) -> bool:
        llamadas.append(ruta)
        return True

    monkeypatch.setattr(
        "pcobra.cobra.cli.cobrahub_packages.CobraHubPackages.publicar_paquete",
        publicar_mock,
    )

    assert runtime.idle_publicar_paquete(paquete) is True
    assert llamadas == [str(paquete)]


def test_idle_publicar_paquete_no_delega_en_metodo_legacy_del_cliente(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paquete = tmp_path / "paquete.co"
    paquete.write_text("contenido", encoding="utf-8")
    llamadas: list[str] = []

    def publicar_packages_mock(self, ruta: str) -> bool:
        llamadas.append(ruta)
        return True

    def publicar_cliente_legacy_mock(self, ruta: str) -> bool:
        raise AssertionError(
            "El IDLE no debe publicar mediante CobraHubClient.publicar_paquete"
        )

    monkeypatch.setattr(
        "pcobra.cobra.cli.cobrahub_packages.CobraHubPackages.publicar_paquete",
        publicar_packages_mock,
    )
    monkeypatch.setattr(
        "pcobra.cobra.cli.cobrahub_client.CobraHubClient.publicar_paquete",
        publicar_cliente_legacy_mock,
    )

    assert runtime.idle_publicar_paquete(paquete) is True
    assert llamadas == [str(paquete)]

def test_helpers_idle_de_paquetes_no_importan_lexer_ni_parser_y_delegan_en_packaging(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = _crear_proyecto_cobra_minimo(tmp_path)
    paquete = tmp_path / "paquete.co"
    destino = tmp_path / "destino"
    destino.mkdir()
    llamadas: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    def fake_crear_paquete(*args, **kwargs):
        llamadas.append(("crear_paquete", args, kwargs))
        return project_root / "cobra.pkg.json"

    def fake_validar_paquete(*args, **kwargs):
        llamadas.append(("validar_paquete", args, kwargs))
        return SimpleNamespace(path=paquete)

    def fake_construir_paquete(*args, **kwargs):
        llamadas.append(("construir_paquete", args, kwargs))
        return paquete

    def fake_extraer_paquete(*args, **kwargs):
        llamadas.append(("extraer_paquete", args, kwargs))
        return destino

    monkeypatch.setattr("pcobra.cobra.packaging.crear_paquete", fake_crear_paquete)
    monkeypatch.setattr("pcobra.cobra.packaging.validar_paquete", fake_validar_paquete)
    monkeypatch.setattr(
        "pcobra.cobra.packaging.construir_paquete", fake_construir_paquete
    )
    monkeypatch.setattr("pcobra.cobra.packaging.extraer_paquete", fake_extraer_paquete)

    real_import = __import__

    def fail_lexer_parser_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pcobra.cobra.core" and {"Lexer", "Parser"} & set(
            fromlist or ()
        ):  # pragma: no cover - solo falla si hay regresión
            raise AssertionError(
                "Los helpers IDLE de paquetes no deben importar Lexer ni Parser"
            )
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fail_lexer_parser_import)

    manifest = project_root / "cobra.pkg.json"
    manifest.write_text("{}", encoding="utf-8")

    assert (
        runtime.idle_crear_paquete(project_root, "paquete-demo", version="2.0.0")
        == project_root / "cobra.pkg.json"
    )
    assert runtime.idle_validar_paquete(paquete).path == paquete
    assert runtime.idle_construir_paquete(project_root, paquete) == paquete
    assert runtime.idle_abrir_paquete(paquete, destino) == destino

    assert llamadas == [
        (
            "crear_paquete",
            (project_root.resolve(),),
            {"nombre": "paquete-demo", "version": "2.0.0"},
        ),
        ("validar_paquete", (paquete,), {}),
        ("construir_paquete", (project_root.resolve(), paquete), {}),
        ("extraer_paquete", (paquete, destino), {}),
    ]


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
    assert picker_creados[0].save_file_args == {
        "dialog_title": "Guardar archivo del proyecto Cobra",
        "file_name": "nuevo_archivo.txt",
        "allowed_extensions": [
            "cobra",
            "co",
            "md",
            "markdown",
            "txt",
            "json",
            "yml",
            "yaml",
            "toml",
            "docker-compose.yml",
        ],
    }
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


def test_validar_y_crear_carpeta_idle_casos_validos(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    project_root = workspace_root / "proyecto"
    project_root.mkdir()

    # Caso 1: Carpeta simple dentro del proyecto
    ruta_creada = runtime.validar_y_crear_carpeta_idle(
        "docs", project_root, workspace_root
    )
    assert ruta_creada == (project_root / "docs").resolve()
    assert ruta_creada.is_dir()

    # Caso 2: Carpeta anidada
    ruta_creada = runtime.validar_y_crear_carpeta_idle(
        "config/env", project_root, workspace_root
    )
    assert ruta_creada == (project_root / "config" / "env").resolve()
    assert ruta_creada.is_dir()

    # Caso 3: Carpeta ya existente (no debe fallar)
    ruta_creada = runtime.validar_y_crear_carpeta_idle(
        "docs", project_root, workspace_root
    )
    assert ruta_creada == (project_root / "docs").resolve()
    assert ruta_creada.is_dir()


def test_validar_y_crear_carpeta_idle_bloquea_rutas_invalidas(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    project_root = workspace_root / "proyecto"
    project_root.mkdir()

    # Bloquear rutas que escapan del project_root (../)
    with pytest.raises(ValueError, match="dentro del proyecto activo"):
        runtime.validar_y_crear_carpeta_idle("../escape", project_root, workspace_root)

    # Bloquear rutas absolutas
    with pytest.raises(ValueError, match="relativa al proyecto"):
        runtime.validar_y_crear_carpeta_idle(
            str(tmp_path / "absoluta"), project_root, workspace_root
        )

    # Bloquear creación de project_root
    with pytest.raises(ValueError, match="No se puede crear la raíz del proyecto"):
        runtime.validar_y_crear_carpeta_idle("", project_root, workspace_root)
    with pytest.raises(ValueError, match="No se puede crear la raíz del proyecto"):
        runtime.validar_y_crear_carpeta_idle(".", project_root, workspace_root)

    # Bloquear creación de workspace_root
    with pytest.raises(ValueError, match="dentro del proyecto activo"):
        runtime.validar_y_crear_carpeta_idle(
            str(Path("../..").relative_to(Path("."))), project_root, workspace_root
        )

    # Bloquear si project_root no es un directorio
    (project_root / "archivo.txt").write_text("contenido")
    with pytest.raises(
        NotADirectoryError, match="La raíz del proyecto no es un directorio"
    ):
        runtime.validar_y_crear_carpeta_idle(
            "nueva_carpeta", project_root / "archivo.txt", workspace_root
        )
