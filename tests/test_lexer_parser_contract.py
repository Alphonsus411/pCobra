import ast
from pathlib import Path

from pcobra.cobra.core.lexer import Lexer, TipoToken
from pcobra.cobra.core.parser import ClassicParser


ROOT = Path(__file__).resolve().parents[1]
PARSER_PATH = ROOT / "src/pcobra/cobra/core/parser.py"


def _tipo_token_attr(node: ast.AST) -> str | None:
    if (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "TipoToken"
    ):
        return node.attr
    return None


def test_parser_factories_no_declara_claves_duplicadas() -> None:
    """Contrato: el literal que construye _factories no debe pisar handlers."""
    tree = ast.parse(PARSER_PATH.read_text(encoding="utf-8"))
    duplicates: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Attribute) and target.attr == "_factories"
            for target in node.targets
        ):
            continue
        assert isinstance(node.value, ast.Dict)
        seen: set[str] = set()
        for key in node.value.keys:
            token_name = _tipo_token_attr(key) if key is not None else None
            if token_name is None:
                continue
            if token_name in seen:
                duplicates.append(token_name)
            seen.add(token_name)

    assert duplicates == []


def test_lexer_palabras_reservadas_con_cobertura_esperada() -> None:
    """Contrato de cobertura para palabras reservadas ya aceptadas por el lexer."""
    palabras_esperadas = {
        "var": TipoToken.VAR,
        "variable": TipoToken.VARIABLE,
        "func": TipoToken.FUNC,
        "definir": TipoToken.FUNC,
        "metodo": TipoToken.METODO,
        "atributo": TipoToken.ATRIBUTO,
        "si": TipoToken.SI,
        "sino": TipoToken.SINO,
        "elseif": TipoToken.SINO_SI,
        "garantia": TipoToken.GARANTIA,
        "guard": TipoToken.GARANTIA,
        "mientras": TipoToken.MIENTRAS,
        "para": TipoToken.PARA,
        "import": TipoToken.IMPORT,
        "usar": TipoToken.USAR,
        "exportar": TipoToken.EXPORTAR,
        "option": TipoToken.OPCION,
        "macro": TipoToken.MACRO,
        "hilo": TipoToken.HILO,
        "asincronico": TipoToken.ASINCRONICO,
        "switch": TipoToken.SWITCH,
        "segun": TipoToken.SWITCH,
        "case": TipoToken.CASE,
        "caso": TipoToken.CASE,
        "clase": TipoToken.CLASE,
        "estructura": TipoToken.ESTRUCTURA,
        "registro": TipoToken.REGISTRO,
        "enumeracion": TipoToken.ENUMERACION,
        "interface": TipoToken.INTERFACE,
        "rasgo": TipoToken.INTERFACE,
        "en": TipoToken.EN,
        "holobit": TipoToken.HOLOBIT,
        "proyectar": TipoToken.PROYECTAR,
        "transformar": TipoToken.TRANSFORMAR,
        "graficar": TipoToken.GRAFICAR,
        "try": TipoToken.INTENTAR,
        "intentar": TipoToken.INTENTAR,
        "defer": TipoToken.APLAZAR,
        "aplazar": TipoToken.APLAZAR,
        "catch": TipoToken.CAPTURAR,
        "capturar": TipoToken.CAPTURAR,
        "throw": TipoToken.LANZAR,
        "lanzar": TipoToken.LANZAR,
        "imprimir": TipoToken.IMPRIMIR,
        "yield": TipoToken.GENERAR,
        "esperar": TipoToken.ESPERAR,
        "romper": TipoToken.ROMPER,
        "continuar": TipoToken.CONTINUAR,
        "pasar": TipoToken.PASAR,
        "afirmar": TipoToken.AFIRMAR,
        "eliminar": TipoToken.ELIMINAR,
        "global": TipoToken.GLOBAL,
        "nolocal": TipoToken.NOLOCAL,
        "lambda": TipoToken.LAMBDA,
        "con": TipoToken.CON,
        "finalmente": TipoToken.FINALMENTE,
        "desde": TipoToken.DESDE,
        "como": TipoToken.COMO,
        "fin": TipoToken.FIN,
        "retorno": TipoToken.RETORNO,
    }

    for palabra, tipo in palabras_esperadas.items():
        tokens = Lexer(palabra).tokenizar()
        assert tokens[0].tipo == tipo, palabra


def test_lexer_no_tiene_especificaciones_reservadas_exactas_duplicadas() -> None:
    especificaciones = Lexer("").especificacion_tokens
    vistas: set[tuple[TipoToken | None, str, int]] = set()
    duplicadas: list[tuple[TipoToken | None, str, int]] = []

    for tipo, patron in especificaciones:
        clave = (tipo, patron.pattern, patron.flags)
        if tipo is not None and clave in vistas:
            duplicadas.append(clave)
        vistas.add(clave)

    assert duplicadas == []


def test_humo_lexer_parser_acepta_ejemplos_del_libro_programacion() -> None:
    ejemplos_documentados = [
        'imprimir("Hola, Cobra")',
        'var x = 10\nimprimir(x)',
    ]

    for codigo in ejemplos_documentados:
        tokens = Lexer(codigo).tokenizar()
        ast_resultado = ClassicParser(tokens).parsear()
        assert ast_resultado


def test_nueva_palabra_clave_del_lexer_exige_actualizaciones_de_contrato() -> None:
    """Toda palabra clave nueva debe aterrizar en Parser y en el checklist público."""

    tokens_declaracion_con_handler = set(ClassicParser([])._factories)
    tokens_contextuales_soportados = {
        TipoToken.CAPTURAR,
        TipoToken.CASE,
        TipoToken.COMO,
        TipoToken.EN,
        TipoToken.FIN,
        TipoToken.FINALMENTE,
        TipoToken.METODO,
        TipoToken.ATRIBUTO,
        TipoToken.RETORNO,
        TipoToken.SINO,
        TipoToken.SINO_SI,
    }
    tokens_expresion_soportados = {TipoToken.LAMBDA}
    tokens_reservados_sin_declaracion_propia = (
        tokens_declaracion_con_handler
        | tokens_contextuales_soportados
        | tokens_expresion_soportados
    )

    palabras_reservadas = {
        token.tipo
        for palabra in [
            "var",
            "variable",
            "func",
            "definir",
            "metodo",
            "atributo",
            "si",
            "sino",
            "elseif",
            "garantia",
            "guard",
            "mientras",
            "para",
            "import",
            "usar",
            "exportar",
            "option",
            "macro",
            "hilo",
            "asincronico",
            "switch",
            "segun",
            "case",
            "caso",
            "clase",
            "estructura",
            "registro",
            "enumeracion",
            "interface",
            "rasgo",
            "en",
            "holobit",
            "proyectar",
            "transformar",
            "graficar",
            "try",
            "intentar",
            "defer",
            "aplazar",
            "catch",
            "capturar",
            "throw",
            "lanzar",
            "imprimir",
            "yield",
            "esperar",
            "romper",
            "continuar",
            "pasar",
            "afirmar",
            "eliminar",
            "global",
            "nolocal",
            "lambda",
            "con",
            "finalmente",
            "desde",
            "como",
            "fin",
            "retorno",
        ]
        for token in [Lexer(palabra).tokenizar()[0]]
    }

    faltantes = palabras_reservadas - tokens_reservados_sin_declaracion_propia
    assert {token.name for token in faltantes} == set()
    checklist = (ROOT / "docs/tareas_implementacion_libro_cobra.md").read_text(
        encoding="utf-8"
    )
    for requisito in [
        "Parser",
        "AST",
        "transpiladores oficiales",
        "documentación del Libro",
        "pruebas de contrato Lexer/Parser",
    ]:
        assert requisito in checklist
