import pytest
from pathlib import Path
from textwrap import dedent

from pcobra.cobra.core.interpreter import InterpretadorCobra
from pcobra.cobra.usar_loader import (
    obtener_cache_ast_import_co,
    obtener_cache_modulos_cobra_proyecto,
    obtener_pila_carga_modulos_cobra_proyecto,
)
from pcobra.cobra.core import Lexer, Parser # Importar Lexer y Parser

# Fixture para un intérprete limpio y aislado para cada test
@pytest.fixture
def interprete_limpio(tmp_path):
    # Asegurarse de que los cachés estén limpios para cada test
    obtener_cache_ast_import_co().clear()
    obtener_cache_modulos_cobra_proyecto().clear()
    obtener_pila_carga_modulos_cobra_proyecto().clear()
    return InterpretadorCobra(main_file=tmp_path / "main.co")

# Fixture para crear un archivo de módulo Cobra
@pytest.fixture
def crear_modulo_cobra(tmp_path):
    def _crear_modulo(ruta_relativa, contenido):
        ruta_abs = tmp_path / ruta_relativa
        ruta_abs.parent.mkdir(parents=True, exist_ok=True)
        ruta_abs.write_text(dedent(contenido))
        return ruta_abs
    return _crear_modulo

def test_usar_modulo_en_misma_carpeta(interprete_limpio, crear_modulo_cobra, tmp_path):
    crear_modulo_cobra(
        "mi_modulo.co",
        """
        variable saludo = "Hola desde mi_modulo"
        """
    )
    crear_modulo_cobra(
        "main.co",
        """
        usar mi_modulo
        imprimir(saludo)
        """
    )
    source_code = (tmp_path / "main.co").read_text()
    lexer = Lexer(source_code)
    tokens = lexer.tokens
    parser = Parser(tokens)
    ast = parser.parsear()
    interprete_limpio.ejecutar_ast(ast)
    assert interprete_limpio.obtener_variable("saludo") == "Hola desde mi_modulo"

def test_usar_modulo_en_subcarpeta_con_puntos(interprete_limpio, crear_modulo_cobra, tmp_path):
    crear_modulo_cobra(
        "utilidades/fechas.co",
        """
        variable hoy = "2026-06-13"
        """
    )
    crear_modulo_cobra(
        "main.co",
        """
        usar utilidades.fechas
        imprimir(hoy)
        """
    )
    source_code = (tmp_path / "main.co").read_text()
    lexer = Lexer(source_code)
    tokens = lexer.tokens
    parser = Parser(tokens)
    ast = parser.parsear()
    interprete_limpio.ejecutar_ast(ast)
    assert interprete_limpio.obtener_variable("hoy") == "2026-06-13"

def test_usar_modulo_anidado(interprete_limpio, crear_modulo_cobra, tmp_path):
    crear_modulo_cobra(
        "utilidades/sub/modulo_anidado.co",
        """
        variable secreto = 42
        """
    )
    crear_modulo_cobra(
        "main.co",
        """
        usar utilidades.sub.modulo_anidado
        imprimir(secreto)
        """
    )
    source_code = (tmp_path / "main.co").read_text()
    lexer = Lexer(source_code)
    tokens = lexer.tokens
    parser = Parser(tokens)
    ast = parser.parsear()
    interprete_limpio.ejecutar_ast(ast)
    assert interprete_limpio.obtener_variable("secreto") == 42

def test_modulo_se_carga_una_sola_vez(interprete_limpio, crear_modulo_cobra, tmp_path):
    crear_modulo_cobra(
        "contador.co",
        """
        variable cuenta = 0
        funcion incrementar():
            cuenta = cuenta + 1
        """
    )
    crear_modulo_cobra(
        "main.co",
        """
        usar contador
        incrementar()
        usar contador
        incrementar()
        """
    )
    source_code = (tmp_path / "main.co").read_text()
    lexer = Lexer(source_code)
    tokens = lexer.tokens
    parser = Parser(tokens)
    ast = parser.parsear()
    interprete_limpio.ejecutar_ast(ast)
    assert interprete_limpio.obtener_variable("cuenta") == 1

def test_deteccion_ciclo_directo(interprete_limpio, crear_modulo_cobra, tmp_path):
    crear_modulo_cobra(
        "modulo_a.co",
        """
        usar modulo_b
        variable valor_a = 1
        """
    )
    crear_modulo_cobra(
        "modulo_b.co",
        """
        usar modulo_a
        variable valor_b = 2
        """
    )
    crear_modulo_cobra(
        "main.co",
        """
        usar modulo_a
        """
    )
    source_code = (tmp_path / "main.co").read_text()
    lexer = Lexer(source_code)
    tokens = lexer.tokens
    parser = Parser(tokens)
    ast = parser.parsear()
    with pytest.raises(ImportError, match="Ciclo de módulos detectado en usar:"):
        interprete_limpio.ejecutar_ast(ast)

def test_deteccion_ciclo_indirecto(interprete_limpio, crear_modulo_cobra, tmp_path):
    crear_modulo_cobra(
        "modulo_x.co",
        """
        usar modulo_y
        variable val_x = 10
        """
    )
    crear_modulo_cobra(
        "modulo_y.co",
        """
        usar modulo_z
        variable val_y = 20
        """
    )
    crear_modulo_cobra(
        "modulo_z.co",
        """
        usar modulo_x
        variable val_z = 30
        """
    )
    crear_modulo_cobra(
        "main.co",
        """
        usar modulo_x
        """
    )
    source_code = (tmp_path / "main.co").read_text()
    lexer = Lexer(source_code)
    tokens = lexer.tokens
    parser = Parser(tokens)
    ast = parser.parsear()
    with pytest.raises(ImportError, match="Ciclo de módulos detectado en usar:"):
        interprete_limpio.ejecutar_ast(ast)

def test_modulo_inexistente(interprete_limpio, crear_modulo_cobra, tmp_path):
    crear_modulo_cobra(
        "main.co",
        """
        usar modulo_que_no_existe
        """
    )
    source_code = (tmp_path / "main.co").read_text()
    lexer = Lexer(source_code)
    tokens = lexer.tokens
    parser = Parser(tokens)
    ast = parser.parsear()
    with pytest.raises(FileNotFoundError, match="Módulo no encontrado: modulo_que_no_existe"):
        interprete_limpio.ejecutar_ast(ast)

def test_compatibilidad_import_archivo_co(interprete_limpio, crear_modulo_cobra, tmp_path):
    crear_modulo_cobra(
        "legacy_module.co",
        """
        variable legacy_var = "Soy legacy"
        """
    )
    crear_modulo_cobra(
        "main.co",
        """
        import 'legacy_module.co'
        imprimir(legacy_var)
        """
    )
    source_code = (tmp_path / "main.co").read_text()
    lexer = Lexer(source_code)
    tokens = lexer.tokens
    parser = Parser(tokens)
    ast = parser.parsear()
    interprete_limpio.ejecutar_ast(ast)
    assert interprete_limpio.obtener_variable("legacy_var") == "Soy legacy"

def test_bloqueo_rutas_escape_con_puntos_dobles(interprete_limpio, crear_modulo_cobra, tmp_path):
    # Crear un archivo fuera de la raíz del proyecto simulada por tmp_path
    ruta_fuera_proyecto = interprete_limpio._project_root.parent / "modulo_secreto.co"
    ruta_fuera_proyecto.write_text(dedent("variable secreto_externo = 'Acceso denegado'"))

    crear_modulo_cobra(
        "sub/main.co",
        """
        usar ../modulo_secreto
        """
    )
    source_code = (tmp_path / "sub/main.co").read_text()
    lexer = Lexer(source_code)
    tokens = lexer.tokens
    parser = Parser(tokens)
    ast = parser.parsear()
    # La detección de rutas de escape se realiza en resolver_ruta_canonica_modulo_cobra_proyecto
    # que es llamada por _ejecutar_usar_modulo_proyecto.
    # Por lo tanto, esperamos un FileNotFoundError o PermissionError si la ruta es bloqueada.
    with pytest.raises((FileNotFoundError, PermissionError), match="Módulo fuera de la raíz del proyecto"):
        interprete_limpio.ejecutar_ast(ast)
