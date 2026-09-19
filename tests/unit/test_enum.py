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


def test_transpilador_rust_acceso_variante_enum_en_funcion():
    codigo = """func principal():
    enumeracion Color: ROJO, VERDE fin
    imprimir(Color.ROJO)
fin"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)

    assert "enum Color {\n        ROJO,\n        VERDE,\n    }" in resultado
    assert "Color::ROJO" in resultado
    assert "Color.ROJO" not in resultado


def test_transpilador_rust_acceso_variante_alias_enum_en_funcion():
    codigo = """func principal():
    enum Estado: ACTIVO, INACTIVO fin
    imprimir(Estado.ACTIVO)
fin"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)

    assert "Estado::ACTIVO" in resultado
    assert "Estado.ACTIVO" not in resultado


def test_transpilador_rust_enum_local_no_contamina_funcion_hermana():
    codigo = """func uno():
    enumeracion Color: ROJO fin
    imprimir(Color.ROJO)
fin

func dos():
    imprimir(Color.ROJO)
fin"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)
    funcion_uno, funcion_dos = resultado.split("fn dos()")

    assert 'println!("{}", Color::ROJO);' in funcion_uno
    assert 'println!("{}", Color.ROJO);' in funcion_dos
    assert "Color::ROJO" not in funcion_dos


def test_transpilador_rust_enum_global_visible_en_funcion():
    codigo = """enumeracion Color: ROJO fin

func principal():
    imprimir(Color.ROJO)
fin"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)

    assert 'println!("{}", Color::ROJO);' in resultado
    assert "Color.ROJO" not in resultado


def test_transpilador_rust_combina_enums_global_y_local_en_funcion():
    codigo = """enumeracion Global: A fin

func principal():
    enumeracion Local: B fin
    imprimir(Global.A)
    imprimir(Local.B)
fin"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)

    assert 'println!("{}", Global::A);' in resultado
    assert 'println!("{}", Local::B);' in resultado


def test_transpilador_rust_acceso_variante_enum_en_metodo():
    codigo = """clase Gestor:
    metodo uno():
        enumeracion Estado: ACTIVO, INACTIVO fin
        imprimir(Estado.ACTIVO)
    fin
fin"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)

    assert 'println!("{}", Estado::ACTIVO);' in resultado
    assert "Estado.ACTIVO" not in resultado


def test_transpilador_rust_acceso_variante_alias_enum_en_metodo():
    codigo = """clase Gestor:
    metodo uno():
        enum Estado: ACTIVO fin
        imprimir(Estado.ACTIVO)
    fin
fin"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)

    assert 'println!("{}", Estado::ACTIVO);' in resultado
    assert "Estado.ACTIVO" not in resultado


def test_transpilador_rust_enum_local_no_contamina_metodo_hermano():
    codigo = """clase Gestor:
    metodo uno():
        enumeracion Estado: ACTIVO fin
        imprimir(Estado.ACTIVO)
    fin

    metodo dos():
        imprimir(Estado.ACTIVO)
    fin
fin"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)
    metodo_uno, metodo_dos = resultado.split("fn dos()")

    assert 'println!("{}", Estado::ACTIVO);' in metodo_uno
    assert 'println!("{}", Estado.ACTIVO);' in metodo_dos
    assert "Estado::ACTIVO" not in metodo_dos


def test_transpilador_rust_enum_global_visible_en_metodo():
    codigo = """enumeracion Global: A fin

clase Gestor:
    metodo uno():
        imprimir(Global.A)
    fin
fin"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)

    assert 'println!("{}", Global::A);' in resultado
    assert "Global.A" not in resultado


def test_transpilador_rust_combina_enums_global_y_local_en_metodo():
    codigo = """enumeracion Global: A fin

clase Gestor:
    metodo uno():
        enumeracion Local: B fin
        imprimir(Global.A)
        imprimir(Local.B)
    fin
fin"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)

    assert 'println!("{}", Global::A);' in resultado
    assert 'println!("{}", Local::B);' in resultado


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


def test_transpilador_rust_enum_local_en_mientras_y_no_fuga():
    codigo = """func principal():
    mientras verdadero:
        enumeracion Color: ROJO, VERDE fin
        imprimir(Color.ROJO)
    fin

    imprimir(Color.ROJO)
fin"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)
    dentro, despues = resultado.split('println!("{}", Color::ROJO);')

    assert "while true {" in dentro
    assert 'println!("{}", Color.ROJO);' in despues
    assert "Color::ROJO" not in despues


def test_transpilador_rust_enum_local_aislado_entre_si_y_sino():
    codigo = """func principal():
    si verdadero:
        enumeracion Estado: ACTIVO fin
        imprimir(Estado.ACTIVO)
    sino:
        imprimir(Estado.ACTIVO)
    fin
fin"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)
    rama_si, rama_sino = resultado.split("} else {")

    assert 'println!("{}", Estado::ACTIVO);' in rama_si
    assert 'println!("{}", Estado.ACTIVO);' in rama_sino
    assert "Estado::ACTIVO" not in rama_sino


def test_transpilador_rust_enum_local_aislado_entre_try_y_catch():
    codigo = """intentar:
    enumeracion Error: FALLO fin
    imprimir(Error.FALLO)
capturar e:
    imprimir(Error.FALLO)
fin"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)
    bloque_try, bloque_catch = resultado.split("Err(e) => {")

    assert 'println!("{}", Error::FALLO);' in bloque_try
    assert 'println!("{}", Error.FALLO);' in bloque_catch
    assert "Error::FALLO" not in bloque_catch


def test_transpilador_rust_enum_local_aislado_entre_casos_switch():
    codigo = """segun opcion:
    caso 1:
        enumeracion Estado: ACTIVO fin
        imprimir(Estado.ACTIVO)
    caso 2:
        imprimir(Estado.ACTIVO)
fin"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)
    primer_caso, segundo_caso = resultado.split("2 => {")

    assert 'println!("{}", Estado::ACTIVO);' in primer_caso
    assert 'println!("{}", Estado.ACTIVO);' in segundo_caso
    assert "Estado::ACTIVO" not in segundo_caso


def test_transpilador_rust_enum_local_en_with_y_no_fuga():
    codigo = """con recurso como r:
    enumeracion Estado: ACTIVO fin
    imprimir(Estado.ACTIVO)
fin
imprimir(Estado.ACTIVO)"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)
    dentro, despues = resultado.split('println!("{}", Estado::ACTIVO);')

    assert "{" in dentro
    assert 'println!("{}", Estado.ACTIVO);' in despues
    assert "Estado::ACTIVO" not in despues


def test_transpilador_rust_enum_exterior_heredado_en_bloque():
    codigo = """enumeracion Global: A fin
func principal():
    mientras verdadero:
        imprimir(Global.A)
        romper
    fin
fin"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    resultado = TranspiladorRust().generate_code(ast)

    assert 'println!("{}", Global::A);' in resultado
    assert "Global.A" not in resultado
