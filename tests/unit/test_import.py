import pytest
from io import StringIO
from unittest.mock import patch

from pcobra.core.lexer import Lexer
from pcobra.core.parser import Parser
from pcobra.core.interpreter import (
    InterpretadorCobra,
    MODULES_PATH,
    IMPORT_WHITELIST,
)
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.import_helper import get_standard_imports

IMPORTS = get_standard_imports("python")


@pytest.mark.timeout(5)
def test_import_rechaza_archivo_co_de_texto_antes_de_ejecutarlo(tmp_path):
    modulo = tmp_path / "modulo.co"
    modulo.write_text("var ejecutado = verdadero", encoding="utf-8")
    IMPORT_WHITELIST.add(str(modulo))

    ruta = str(modulo).replace("\\", "/")
    codigo = f"import '{ruta}'"
    ast = Parser(Lexer(codigo).analizar_token()).parsear()

    try:
        with pytest.raises(ValueError, match=r"extensión \.cobra"):
            InterpretadorCobra().ejecutar_ast(ast)
    finally:
        IMPORT_WHITELIST.remove(str(modulo))


@pytest.mark.timeout(5)
def test_import_interpreter(tmp_path):
    mod = tmp_path / "mod.cobra"
    mod.write_text("var dato = 5")

    IMPORT_WHITELIST.add(str(mod))

    mod_path_str = str(mod).replace('\\', '/')
    codigo = f"import '{mod_path_str}'\nimprimir(dato)"
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    interp = InterpretadorCobra()

    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        interp.ejecutar_ast(ast)

    IMPORT_WHITELIST.remove(str(mod))

    assert mock_stdout.getvalue().strip() == "5"


@pytest.mark.timeout(5)
def test_import_co_carga_unica(tmp_path):
    mod_path = tmp_path / "mod_contador.cobra"
    # Cambiar el contenido para evitar la auto-referencia
    mod_path.write_text("var _contador_interno = 0\nfunc incrementar_contador() { _contador_interno = _contador_interno + 1 }\nincrementar_contador()")

    IMPORT_WHITELIST.add(str(mod_path))

    mod_path_str = str(mod_path).replace('\\', '/')
    codigo = f"import '{mod_path_str}'\nimport '{mod_path_str}'\nimprimir(_contador_interno)" # Ahora imprimimos _contador_interno
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    interp = InterpretadorCobra()

    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        interp.ejecutar_ast(ast)

    IMPORT_WHITELIST.remove(str(mod_path))

    assert mock_stdout.getvalue().strip() == "1"


@pytest.mark.timeout(5)
def test_import_co_ciclo_directo(tmp_path):
    mod_a_path = tmp_path / "mod_a.cobra"
    mod_b_path = tmp_path / "mod_b.cobra"

    mod_b_path_str = str(mod_b_path).replace('\\', '/')
    mod_a_path.write_text(f"import '{mod_b_path_str}'")
    mod_a_path_str = str(mod_a_path).replace('\\', '/')
    mod_b_path.write_text(f"import '{mod_a_path_str}'")

    IMPORT_WHITELIST.add(str(mod_a_path))
    IMPORT_WHITELIST.add(str(mod_b_path))

    codigo = f"import '{mod_a_path_str}'"
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    interp = InterpretadorCobra()

    with pytest.raises(ImportError, match="Ciclo de módulos detectado en import"):
        interp.ejecutar_ast(ast)

    IMPORT_WHITELIST.remove(str(mod_a_path))
    IMPORT_WHITELIST.remove(str(mod_b_path))


@pytest.mark.timeout(5)
def test_import_co_compatibilidad_ambito(tmp_path):
    mod_path = tmp_path / "mod_vars.cobra"
    mod_path.write_text("var x = 10\nvar y = 20")

    IMPORT_WHITELIST.add(str(mod_path))

    mod_path_str = str(mod_path).replace('\\', '/')
    codigo = f"import '{mod_path_str}'\nimprimir(x + y)"
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    interp = InterpretadorCobra()

    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        interp.ejecutar_ast(ast)

    IMPORT_WHITELIST.remove(str(mod_path))

    assert mock_stdout.getvalue().strip() == "30"


@pytest.mark.timeout(5)
def test_import_cobra_proteccion_path_traversal(tmp_path):
    # Crear un archivo fuera del directorio temporal para simular un intento de traversal
    malicious_file = tmp_path.parent / "malicious.cobra"
    malicious_file.write_text("var secreto = 'informacion_sensible'")

    # Intentar importar usando ../
    malicious_file_str = str(malicious_file).replace('\\', '/')
    codigo = f"import '{malicious_file_str}'"
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    interp = InterpretadorCobra()

    with pytest.raises(PermissionError, match="Módulo fuera de la lista blanca"):
        interp.ejecutar_ast(ast)

    # Limpiar el archivo malicioso
    malicious_file.unlink()


@pytest.mark.timeout(5)
def test_import_transpiler(tmp_path):
    mod = tmp_path / "m.cobra"
    mod.write_text("var valor = 3")

    codigo = f"import '{mod}'\nimprimir(valor)"
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()

    py_code = TranspiladorPython().generate_code(ast)
    expected = IMPORTS + "valor = 3\nprint(valor)\n"
    assert py_code == expected
