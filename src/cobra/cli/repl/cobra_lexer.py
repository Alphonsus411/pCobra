"""Lexer de Pygments para el lenguaje Cobra.

Este módulo define :class:`CobraLexer`, un lexer basado en expresiones
regulares que mapea los tokens definidos en ``TipoToken`` del analizador
léxico principal a categorías de tokens de Pygments. Esto permite utilizar
Pygments para resaltar código Cobra dentro de herramientas como el REPL.
"""

from pygments.lexer import RegexLexer
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
    Whitespace,
)

from cobra.core.lexer import TipoToken

# Mapeo entre los tipos de token del lexer principal y los tokens de Pygments
# junto con la expresión regular que los reconoce. El orden es importante,
# siguiendo la especificación del lexer original para evitar conflictos.
TOKEN_REGEX_MAP = [
    # Palabras clave
    (TipoToken.VAR, r"\bvar\b", Keyword),
    (TipoToken.VARIABLE, r"\bvariable\b", Keyword),
    (TipoToken.FUNC, r"\b(func|definir)\b", Keyword),
    (TipoToken.METODO, r"\bmetodo\b", Keyword),
    (TipoToken.ATRIBUTO, r"\batributo\b", Keyword),
    (TipoToken.SI, r"\bsi\b", Keyword),
    (TipoToken.SINO, r"\bsino\b", Keyword),
    (TipoToken.MIENTRAS, r"\bmientras\b", Keyword),
    (TipoToken.PARA, r"\bpara\b", Keyword),
    (TipoToken.IMPORT, r"\bimport\b", Keyword),
    (TipoToken.USAR, r"\busar\b", Keyword),
    (TipoToken.OPTION, r"\boption\b", Keyword),
    (TipoToken.MACRO, r"\bmacro\b", Keyword),
    (TipoToken.HILO, r"\bhilo\b", Keyword),
    (TipoToken.ASINCRONICO, r"\basincronico\b", Keyword),
    (TipoToken.SWITCH, r"\b(switch|segun)\b", Keyword),
    (TipoToken.CASE, r"\b(case|caso)\b", Keyword),
    (TipoToken.CLASE, r"\bclase\b", Keyword),
    (TipoToken.ENUM, r"\benum\b", Keyword),
    (TipoToken.INTERFACE, r"\b(interface|trait)\b", Keyword),
    (TipoToken.IN, r"\bin\b", Keyword),
    (TipoToken.HOLOBIT, r"\bholobit\b", Keyword),
    (TipoToken.PROYECTAR, r"\bproyectar\b", Keyword),
    (TipoToken.TRANSFORMAR, r"\btransformar\b", Keyword),
    (TipoToken.GRAFICAR, r"\bgraficar\b", Keyword),
    (TipoToken.TRY, r"\btry\b", Keyword),
    (TipoToken.CATCH, r"\bcatch\b", Keyword),
    (TipoToken.THROW, r"\bthrow\b", Keyword),
    (TipoToken.INTENTAR, r"\bintentar\b", Keyword),
    (TipoToken.CAPTURAR, r"\bcapturar\b", Keyword),
    (TipoToken.LANZAR, r"\blanzar\b", Keyword),
    (TipoToken.IMPRIMIR, r"\bimprimir\b", Keyword),
    (TipoToken.YIELD, r"\byield\b", Keyword),
    (TipoToken.ESPERAR, r"\besperar\b", Keyword),
    (TipoToken.ROMPER, r"\bromper\b", Keyword),
    (TipoToken.CONTINUAR, r"\bcontinuar\b", Keyword),
    (TipoToken.PASAR, r"\bpasar\b", Keyword),
    (TipoToken.AFIRMAR, r"\bafirmar\b", Keyword),
    (TipoToken.ELIMINAR, r"\beliminar\b", Keyword),
    (TipoToken.GLOBAL, r"\bglobal\b", Keyword),
    (TipoToken.NOLOCAL, r"\bnolocal\b", Keyword),
    (TipoToken.LAMBDA, r"\blambda\b", Keyword),
    (TipoToken.CON, r"\bcon\b", Keyword),
    (TipoToken.WITH, r"\bwith\b", Keyword),
    (TipoToken.FINALMENTE, r"\bfinalmente\b", Keyword),
    (TipoToken.DESDE, r"\bdesde\b", Keyword),
    (TipoToken.COMO, r"\bcomo\b", Keyword),
    (TipoToken.AS, r"\bas\b", Keyword),
    (TipoToken.FLOTANTE, r"\d+\.\d+", Number.Float),
    (TipoToken.ENTERO, r"\d+", Number.Integer),
    (TipoToken.CADENA, r"'(?:\\.|[^'])*'|\"(?:\\.|[^\"])*\"", String),
    (TipoToken.BOOLEANO, r"\b(verdadero|falso)\b", Keyword.Constant),
    (TipoToken.ASIGNAR_INFERENCIA, r":=", Operator),
    (TipoToken.DOSPUNTOS, r":", Punctuation),
    (TipoToken.FIN, r"\bfin\b", Keyword),
    (TipoToken.RETORNO, r"\bretorno\b", Keyword),
    # Identificadores (se coloca después de las palabras clave para evitar conflictos)
    (TipoToken.IDENTIFICADOR, r"[^\W\d][\w]*", Name),
    # Operadores y comparaciones
    (TipoToken.MAYORIGUAL, r">=", Operator),
    (TipoToken.MENORIGUAL, r"<=", Operator),
    (TipoToken.IGUAL, r"==", Operator),
    (TipoToken.DIFERENTE, r"!=", Operator),
    (TipoToken.AND, r"&&", Operator),
    (TipoToken.OR, r"\|\|", Operator),
    (TipoToken.NOT, r"!", Operator),
    (TipoToken.MOD, r"%", Operator),
    (TipoToken.ASIGNAR, r"=", Operator),
    (TipoToken.SUMA, r"\+", Operator),
    (TipoToken.RESTA, r"-", Operator),
    (TipoToken.MULT, r"\*", Operator),
    (TipoToken.DIV, r"/", Operator),
    (TipoToken.MAYORQUE, r">", Operator),
    (TipoToken.MENORQUE, r"<", Operator),
    # Delimitadores y puntuación
    (TipoToken.LPAREN, r"\(", Punctuation),
    (TipoToken.RPAREN, r"\)", Punctuation),
    (TipoToken.LBRACE, r"\{", Punctuation),
    (TipoToken.RBRACE, r"\}", Punctuation),
    (TipoToken.LBRACKET, r"\[", Punctuation),
    (TipoToken.RBRACKET, r"\]", Punctuation),
    (TipoToken.COMA, r",", Punctuation),
    (TipoToken.DECORADOR, r"@", Name.Decorator),
]


class CobraLexer(RegexLexer):
    """Lexer de Pygments basado en expresiones regulares para Cobra."""

    name = "Cobra"
    aliases = ["cobra"]
    filenames = ["*.cobra"]

    # Construimos la lista de reglas para el estado raíz a partir del mapa
    _root_rules = [
        (r"/\*", Comment.Multiline, "comment"),
        (r"//.*?$", Comment.Single),
        (r"#.*?$", Comment.Single),
        (r"\s+", Whitespace),
    ] + [(regex, token) for _, regex, token in TOKEN_REGEX_MAP] + [
        (r".", Text),
    ]

    tokens = {
        "root": _root_rules,
        "comment": [
            (r"[^*/]+", Comment.Multiline),
            (r"/\*", Comment.Multiline, "#push"),
            (r"\*/", Comment.Multiline, "#pop"),
            (r"[*/]", Comment.Multiline),
        ],
    }
