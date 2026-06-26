from pathlib import Path
from textwrap import dedent

import pytest

from pcobra.cobra.core import Lexer, Parser
from pcobra.cobra.core.interpreter import InterpretadorCobra
from pcobra.cobra.usar_loader import (
    obtener_cache_ast_import_co,
    obtener_cache_modulos_cobra_proyecto,
    obtener_pila_carga_modulos_cobra_proyecto,
    usar_modulo,
)


@pytest.fixture(autouse=True)
def limpiar_caches_usar():
    obtener_cache_ast_import_co().clear()
    obtener_cache_modulos_cobra_proyecto().clear()
    obtener_pila_carga_modulos_cobra_proyecto().clear()
    yield
    obtener_cache_ast_import_co().clear()
    obtener_cache_modulos_cobra_proyecto().clear()
    obtener_pila_carga_modulos_cobra_proyecto().clear()


@pytest.fixture
def crear_modulo_cobra(tmp_path):
    def _crear_modulo(ruta_relativa: str, contenido: str) -> Path:
        ruta_abs = tmp_path / ruta_relativa
        ruta_abs.parent.mkdir(parents=True, exist_ok=True)
        ruta_abs.write_text(dedent(contenido).strip() + "\n", encoding="utf-8")
        return ruta_abs

    return _crear_modulo


def ejecutar_archivo(ruta: Path) -> InterpretadorCobra:
    codigo = ruta.read_text(encoding="utf-8")
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    interprete = InterpretadorCobra(safe_mode=False, main_file=ruta)
    interprete.ejecutar_ast(ast)
    return interprete


def test_usar_modulo_en_misma_carpeta_util(crear_modulo_cobra, tmp_path):
    crear_modulo_cobra("util.co", 'variable saludo := "Hola desde util"')
    main = crear_modulo_cobra(
        "main.co",
        """
        usar util
        """,
    )

    interprete = ejecutar_archivo(main)

    assert interprete.obtener_variable("saludo") == "Hola desde util"


def test_usar_subcarpeta_punteada_utilidades_fechas(crear_modulo_cobra, tmp_path):
    crear_modulo_cobra("utilidades/fechas.co", 'variable hoy := "2026-06-13"')
    main = crear_modulo_cobra(
        "main.co",
        """
        usar utilidades.fechas
        """,
    )

    interprete = ejecutar_archivo(main)

    assert interprete.obtener_variable("hoy") == "2026-06-13"


def test_usar_modulo_anidado_a_b_c(crear_modulo_cobra):
    crear_modulo_cobra("a/b/c.co", "variable secreto := 42")
    main = crear_modulo_cobra("main.co", "usar a.b.c")

    interprete = ejecutar_archivo(main)

    assert interprete.obtener_variable("secreto") == 42


def test_usar_desde_otro_directorio_respeta_cobra_toml(tmp_path, monkeypatch):
    proyecto = tmp_path / "proyecto"
    proyecto.mkdir()
    (proyecto / "cobra.toml").write_text("[proyecto]\nnombre = 'demo'\n", encoding="utf-8")
    (proyecto / "util.co").write_text('variable desde_root := "ok"\n', encoding="utf-8")
    app = proyecto / "app"
    app.mkdir()
    main = app / "main.co"
    main.write_text("usar util\n", encoding="utf-8")
    otro_directorio = tmp_path / "otro"
    otro_directorio.mkdir()
    monkeypatch.chdir(otro_directorio)

    interprete = ejecutar_archivo(main)

    assert interprete.obtener_variable("desde_root") == "ok"


def test_usar_carga_una_sola_vez_con_cache_y_monkeypatch(crear_modulo_cobra, monkeypatch):
    crear_modulo_cobra("util.co", "variable valor := 7")
    main = crear_modulo_cobra(
        "main.co",
        """
        usar util
        usar util
        """,
    )
    import pcobra.core.import_utils as import_utils

    cargar_original = import_utils.cargar_ast_modulo
    llamadas = []

    def cargar_contando(*args, **kwargs):
        llamadas.append(Path(args[0]).name)
        return cargar_original(*args, **kwargs)

    monkeypatch.setattr(import_utils, "cargar_ast_modulo", cargar_contando)

    interprete = ejecutar_archivo(main)

    assert interprete.obtener_variable("valor") == 7
    assert llamadas.count("util.co") == 1


def test_usar_modulo_proyecto_preserva_usar_oficial_texto(crear_modulo_cobra):
    crear_modulo_cobra(
        "util.co",
        """
        usar texto
        variable saludo_mayusculas := mayusculas("hola")
        """,
    )
    main = crear_modulo_cobra("main.co", "usar util")

    interprete = ejecutar_archivo(main)

    assert interprete.obtener_variable("saludo_mayusculas") == "HOLA"

def test_usar_detecta_ciclo_directo(crear_modulo_cobra):
    crear_modulo_cobra("a.co", """
        usar a
        variable valor_a := 1
        """)
    main = crear_modulo_cobra("main.co", "usar a")

    with pytest.raises(ImportError, match=r"Ciclo de módulos detectado en usar: .*a\.co"):
        ejecutar_archivo(main)


def test_usar_detecta_ciclo_indirecto(crear_modulo_cobra):
    crear_modulo_cobra("a.co", "usar b\nvariable valor_a := 1")
    crear_modulo_cobra("b.co", "usar c\nvariable valor_b := 2")
    crear_modulo_cobra("c.co", "usar a\nvariable valor_c := 3")
    main = crear_modulo_cobra("main.co", "usar a")

    with pytest.raises(ImportError, match=r"Ciclo de módulos detectado en usar: .*a\.co.*b\.co.*c\.co.*a\.co"):
        ejecutar_archivo(main)


def test_usar_modulo_inexistente_muestra_error_claro(crear_modulo_cobra, tmp_path):
    main = crear_modulo_cobra("main.co", "usar modulo_que_no_existe")

    with pytest.raises(FileNotFoundError, match=r"Módulo no encontrado: modulo_que_no_existe\. Ruta buscada: .*modulo_que_no_existe\.co"):
        ejecutar_archivo(main)


def test_compatibilidad_import_archivo_co_relativo_al_main(crear_modulo_cobra):
    crear_modulo_cobra("archivo.co", 'variable legacy_var := "Soy legacy"')
    main = crear_modulo_cobra(
        "main.co",
        """
        import 'archivo.co'
        """,
    )

    interprete = ejecutar_archivo(main)

    assert interprete.obtener_variable("legacy_var") == "Soy legacy"


def test_import_archivo_co_no_delega_en_usar_modulo(crear_modulo_cobra, monkeypatch):
    """`import 'archivo.co'` debe conservar el flujo legacy de `NodoImport`."""

    crear_modulo_cobra("archivo.co", 'variable legacy_var := "Soy legacy"')
    main = crear_modulo_cobra("main.co", "import 'archivo.co'")

    def fail_usar_modulo(*_args, **_kwargs):
        raise AssertionError("import 'archivo.co' no debe delegar en usar_modulo")

    monkeypatch.setattr("pcobra.core.interpreter.usar_modulo", fail_usar_modulo)

    interprete = ejecutar_archivo(main)

    assert interprete.obtener_variable("legacy_var") == "Soy legacy"


@pytest.mark.parametrize("nombre", ["dir/modulo", r"dir\\modulo", r"C:\\tmp\\modulo"])
def test_usar_strings_windows_posix_son_rechazados(tmp_path, nombre):
    with pytest.raises((ValueError, PermissionError), match="ruta|separadores|Windows|fuera"):
        usar_modulo(nombre, project_root=tmp_path, current_file=tmp_path / "main.co")


def test_usar_bloquea_traversal_con_puntos_dobles(tmp_path):
    with pytest.raises((ValueError, PermissionError), match="traversal|inválido|fuera"):
        usar_modulo("../secreto", project_root=tmp_path, current_file=tmp_path / "main.co")
