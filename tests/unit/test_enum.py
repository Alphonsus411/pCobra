from pcobra.cobra.core import Lexer
from pcobra.cobra.core import Parser
from pcobra.core.ast_nodes import NodoAtributo, NodoEnum, NodoIdentificador
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython
from pcobra.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from pcobra.cobra.transpilers.transpiler.to_rust import TranspiladorRust
from pcobra.cobra.transpilers.import_helper import get_standard_imports

IMPORTS_PY = get_standard_imports("python")
IMPORTS_JS = "".join(f"{line}\n" for line in get_standard_imports("javascript"))


def test_parser_enumeracion_color():
    codigo = "enumeracion Color: ROJO, VERDE fin"
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    assert type(ast[0]).__name__ == "NodoEnum"
    assert ast[0].nombre == "Color"
    assert ast[0].miembros == ["ROJO", "VERDE"]


def test_parser_enum_color():
    codigo = "enum Color: ROJO, VERDE fin"
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    assert type(ast[0]).__name__ == "NodoEnum"
    assert ast[0].nombre == "Color"
    assert ast[0].miembros == ["ROJO", "VERDE"]


def test_parser_enumeracion_estado():
    codigo = "enumeracion Estado: ACTIVO, INACTIVO fin"
    parser = Parser(Lexer(codigo).analizar_token())
    ast = parser.parsear()
    assert type(ast[0]).__name__ == "NodoEnum"
    assert ast[0].nombre == "Estado"
    assert ast[0].miembros == ["ACTIVO", "INACTIVO"]


def test_transpilador_python_enum():
    nodo = NodoEnum("Color", ["ROJO", "VERDE"])
    codigo = TranspiladorPython().generate_code([nodo])
    esperado = IMPORTS_PY + "class Color:\n    ROJO = 0\n    VERDE = 1\n"
    assert codigo == esperado


def test_transpilador_python_enum_vacio():
    nodo = NodoEnum("Vacia", [])
    codigo = TranspiladorPython().generate_code([nodo])
    esperado = IMPORTS_PY + "class Vacia:\n    pass\n"
    assert codigo == esperado
    compile(codigo, "<cobra-enum-vacio>", "exec")


def test_transpilador_js_enum():
    nodo = NodoEnum("Color", ["ROJO", "VERDE"])
    codigo = TranspiladorJavaScript().generate_code([nodo])
    esperado = IMPORTS_JS + "const Color = {ROJO: 0, VERDE: 1};"
    assert codigo == esperado


def test_transpilador_rust_enum():
    nodo = NodoEnum("Color", ["ROJO", "VERDE"])
    codigo = TranspiladorRust().generate_code([nodo])
    esperado = "enum Color {\n    ROJO,\n    VERDE,\n}"
    assert codigo.endswith(esperado)


def test_transpilador_rust_enum_vacio():
    nodo = NodoEnum("Vacia", [])
    codigo = TranspiladorRust().generate_code([nodo])
    assert codigo.endswith("enum Vacia {\n}")


def test_transpilador_rust_enum_desde_fuente_canonica():
    codigo = "enumeracion Color: ROJO, VERDE fin"
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)
    assert resultado.endswith("enum Color {\n    ROJO,\n    VERDE,\n}")


def test_transpilador_rust_enum_desde_alias():
    codigo = "enum Color: ROJO, VERDE fin"
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)
    assert resultado.endswith("enum Color {\n    ROJO,\n    VERDE,\n}")


def test_transpilador_rust_enum_vacio_desde_fuente():
    codigo = "enumeracion Vacia: fin"
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)
    assert resultado.endswith("enum Vacia {\n}")


def test_transpilador_rust_acceso_variante_desde_enumeracion():
    codigo = "enumeracion Color: ROJO, VERDE fin imprimir(Color.ROJO)"
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)
    assert "Color::ROJO" in resultado
    assert "Color.ROJO" not in resultado


def test_transpilador_rust_acceso_variante_desde_alias_enum():
    codigo = "enum Color: ROJO, VERDE fin imprimir(Color.VERDE)"
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)
    assert "Color::VERDE" in resultado
    assert "Color.VERDE" not in resultado


def test_transpilador_rust_conserva_atributo_ordinario():
    atributo = NodoAtributo(NodoIdentificador("objeto"), "campo")
    assert TranspiladorRust().obtener_valor(atributo) == "objeto.campo"


def test_transpilador_rust_no_filtra_enums_entre_generaciones():
    transpilador = TranspiladorRust()
    transpilador.generate_code([NodoEnum("Color", ["ROJO"])])

    codigo = "imprimir(Color.ROJO)"
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = transpilador.generate_code(ast)

    assert 'println!("{}", Color.ROJO);' in resultado
    assert "Color::ROJO" not in resultado
