from pathlib import Path
from unittest.mock import patch

import pytest

from pcobra.gui import runtime


@pytest.fixture(autouse=True)
def _ejecutar_en_tmp_path(monkeypatch, tmp_path: Path):
    """Alinea los helpers GUI con la política de sandbox de rutas Cobra."""

    monkeypatch.chdir(tmp_path)


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


def test_escribir_archivo_texto_escribe_una_sola_vez(tmp_path: Path):
    destino = tmp_path / "codigo.co"
    codigo = "imprimir('una vez')"

    with patch.object(
        Path, "write_text", autospec=True, return_value=len(codigo)
    ) as write_text:
        escrito = runtime.escribir_archivo_texto(destino, codigo)

    assert escrito == codigo
    write_text.assert_called_once_with(destino.resolve(), codigo, encoding="utf-8")


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


def test_helpers_archivo_cubren_nuevo_abrir_guardar_como_guardar_y_recargar(
    tmp_path: Path,
):
    estado = runtime.GuiFileState()
    origen = tmp_path / "origen.co"
    destino = tmp_path / "destino.cobra"
    origen.write_text("imprimir('origen')", encoding="utf-8")

    contenido, mensaje = runtime.crear_archivo_nuevo_en_editor(estado)
    assert contenido == ""
    assert mensaje == "Archivo nuevo creado en memoria."
    assert estado.ruta is None
    assert estado.contenido_cargado == ""
    assert estado.cambios_sin_guardar is False

    contenido, mensaje = runtime.abrir_archivo_desde_ruta(origen, estado)
    assert contenido == "imprimir('origen')"
    assert mensaje == f"Archivo cargado: {origen.resolve()}"
    assert estado.ruta == origen.resolve()
    assert estado.contenido_cargado == "imprimir('origen')"
    assert estado.cambios_sin_guardar is False

    contenido, mensaje = runtime.guardar_archivo_como(
        destino, "imprimir('guardar como')", estado
    )
    assert contenido == "imprimir('guardar como')"
    assert mensaje == f"Archivo guardado: {destino.resolve()}"
    assert destino.read_text(encoding="utf-8") == "imprimir('guardar como')"
    assert estado.ruta == destino.resolve()
    assert estado.contenido_cargado == "imprimir('guardar como')"
    assert estado.cambios_sin_guardar is False

    contenido, mensaje = runtime.guardar_archivo_activo(
        "imprimir('guardar activo')", estado
    )
    assert contenido == "imprimir('guardar activo')"
    assert mensaje == f"Archivo guardado: {destino.resolve()}"
    assert destino.read_text(encoding="utf-8") == "imprimir('guardar activo')"
    assert estado.contenido_cargado == "imprimir('guardar activo')"

    destino.write_text("imprimir('recargado')", encoding="utf-8")
    contenido, mensaje = runtime.recargar_archivo_activo(estado)
    assert contenido == "imprimir('recargado')"
    assert mensaje == f"Archivo cargado: {destino.resolve()}"
    assert estado.contenido_cargado == "imprimir('recargado')"
    assert estado.cambios_sin_guardar is False


def test_cargar_archivo_desde_arbol_reusa_apertura_y_valida_extension(tmp_path: Path):
    estado = runtime.GuiFileState()
    archivo_cobra = tmp_path / "desde_arbol.cobra"
    archivo_cobra.write_text("imprimir('arbol')", encoding="utf-8")
    archivo_no_cobra = tmp_path / "nota.txt"
    archivo_no_cobra.write_text("texto", encoding="utf-8")

    contenido, mensaje = runtime.cargar_archivo_desde_arbol(archivo_cobra, estado)

    assert contenido == "imprimir('arbol')"
    assert mensaje == f"Archivo cargado: {archivo_cobra.resolve()}"
    assert estado.ruta == archivo_cobra.resolve()
    assert estado.contenido_cargado == "imprimir('arbol')"

    try:
        runtime.cargar_archivo_desde_arbol(archivo_no_cobra, estado)
    except ValueError as exc:
        assert "Selecciona un archivo Cobra" in str(exc)
    else:
        raise AssertionError("El árbol solo debe cargar archivos .co/.cobra")
