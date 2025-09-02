from cobra.transpilers.transpiler.to_java import TranspiladorJava
from core.ast_nodes import NodoAsignacion, NodoFuncion, NodoLlamadaFuncion, NodoImprimir, NodoValor


def test_transpilador_asignacion_java():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorJava()
    resultado = t.generate_code(ast)
    esperado = (
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        var x = 10;\n"
        "    }\n"
        "}"
    )
    assert resultado == esperado


def test_transpilador_funcion_java():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorJava()
    resultado = t.generate_code(ast)
    esperado = (
        "public class Main {\n"
        "    static void miFuncion(a, b) {\n"
        "        var x = a + b;\n"
        "    }\n"
        "    public static void main(String[] args) {\n"
        "    }\n"
        "}"
    )
    assert resultado == esperado


def test_transpilador_llamada_funcion_java():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorJava()
    resultado = t.generate_code(ast)
    esperado = (
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        miFuncion(a, b);\n"
        "    }\n"
        "}"
    )
    assert resultado == esperado


def test_transpilador_imprimir_java():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorJava()
    resultado = t.generate_code(ast)
    esperado = (
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        System.out.println(\"x\");\n"
        "    }\n"
        "}"
    )
    assert resultado == esperado
