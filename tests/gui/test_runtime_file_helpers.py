from pathlib import Path

from pcobra.gui import runtime


def test_es_archivo_cobra_prioriza_extensiones_documentadas():
    assert runtime.es_archivo_cobra("programa.co")
    assert runtime.es_archivo_cobra("paquete.COBRA")
    assert not runtime.es_archivo_cobra("README.md")


def test_listar_directorio_cobra_filtra_y_ordena(tmp_path: Path):
    (tmp_path / "zeta").mkdir()
    (tmp_path / "beta.co").write_text("", encoding="utf-8")
    (tmp_path / "alfa.cobra").write_text("", encoding="utf-8")
    (tmp_path / "ignorado.py").write_text("", encoding="utf-8")

    assert [path.name for path in runtime.listar_directorio_cobra(tmp_path)] == [
        "zeta",
        "alfa.cobra",
        "beta.co",
    ]


def test_escribir_archivo_texto_no_parsea_ni_modifica_contenido(tmp_path: Path):
    (tmp_path / "sub").mkdir()
    destino = tmp_path / "sub" / "codigo.co"
    codigo = "var x = 1\ntexto inválido para parser ???\n"

    escrito = runtime.escribir_archivo_texto(destino, codigo)

    assert escrito == codigo
    assert destino.read_text(encoding="utf-8") == codigo


def test_escribir_archivo_texto_propaga_ruta_inexistente(tmp_path: Path):
    destino = tmp_path / "no_existe" / "codigo.co"

    try:
        runtime.escribir_archivo_texto(destino, "contenido")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("La escritura debe fallar si el directorio no existe")


def test_parse_missing_target_detecta_modulo_faltante_con_accion_dependencia():
    exc = ModuleNotFoundError("No module named 'flet'", name="flet")

    missing_target, action = runtime._parse_missing_target(exc)

    assert missing_target == "flet"
    assert "instala la dependencia" in action
    assert "flet" in action


def test_parse_missing_target_detecta_simbolo_faltante_en_import_local():
    exc = ImportError(
        "cannot import name 'Lexer' from 'pcobra.cobra.gui.deps' "
        "(/tmp/pcobra/cobra/gui/deps.py)"
    )

    missing_target, action = runtime._parse_missing_target(exc)

    assert missing_target == "pcobra.cobra.gui.deps.Lexer"
    assert "corrige el import local" in action
    assert "pcobra.cobra.gui.deps.Lexer" in action


def test_ejecutar_codigo_usa_dependencias_gui_y_captura_stdout_stderr(monkeypatch):
    calls = []

    class FakeLexer:
        def __init__(self, codigo: str) -> None:
            calls.append(("lexer_init", codigo))

        def tokenizar(self) -> list[str]:
            print("salida desde lexer")
            calls.append(("tokenizar",))
            return ["TOKEN"]

    class FakeParser:
        def __init__(self, tokens: list[str]) -> None:
            calls.append(("parser_init", tokens))

        def parsear(self) -> str:
            calls.append(("parsear",))
            return "AST"

    class FakeInterpretadorCobra:
        def ejecutar_ast(self, ast: str) -> None:
            import sys

            print(f"stdout ast={ast}")
            print("stderr capturado", file=sys.stderr)
            calls.append(("ejecutar_ast", ast))

    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {
            "Lexer": FakeLexer,
            "Parser": FakeParser,
            "InterpretadorCobra": FakeInterpretadorCobra,
        },
    )

    salida = runtime.ejecutar_codigo("mostrar 1")

    assert calls == [
        ("lexer_init", "mostrar 1"),
        ("tokenizar",),
        ("parser_init", ["TOKEN"]),
        ("parsear",),
        ("ejecutar_ast", "AST"),
    ]
    assert "salida desde lexer" in salida
    assert "stdout ast=AST" in salida
    assert "stderr capturado" in salida
