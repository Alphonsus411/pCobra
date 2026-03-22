"""Parser sencillo que transforma código Hololang en nodos AST de Cobra.

El parser implementado aquí cubre el subconjunto del lenguaje Hololang que
es generado por ``TranspiladorHololang``. No pretende ser un analizador
completo, pero soporta asignaciones, funciones, condicionales, bucles,
llamadas y construcciones específicas como la creación de ``Holobit``.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterator, List, Optional

from pcobra.cobra.core import Token, TipoToken
from pcobra.core.ast_nodes import (
    NodoAsignacion,
    NodoAtributo,
    NodoBucleMientras,
    NodoCondicional,
    NodoEsperar,
    NodoFuncion,
    NodoHolobit,
    NodoIdentificador,
    NodoLlamadaFuncion,
    NodoLlamadaMetodo,
    NodoLista,
    NodoDiccionario,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoPara,
    NodoRetorno,
    NodoValor,
    NodoUsar,
)

# ---------------------------------------------------------------------------
# Definiciones de tokens léxicos internos


@dataclass
class LexToken:
    """Token simple utilizado por el parser de Hololang."""

    type: str
    value: str
    position: int


_TOKEN_SPECIFICATION = [
    ("COMMENT", r"//.*"),
    ("MULTICOMMENT", r"/\*.*?\*/"),
    ("NUMBER", r"\d+\.\d+|\d+"),
    ("STRING", r'"([^"\\]|\\.)*"'),
    ("DOUBLECOLON", r"::"),
    ("ARROW", r"->"),
    ("OP", r"==|!=|<=|>=|\|\||&&"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACKET", r"\["),
    ("RBRACKET", r"\]"),
    ("COMMA", r","),
    ("SEMICOLON", r";"),
    ("COLON", r":"),
    ("DOT", r"\."),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("STAR", r"\*"),
    ("SLASH", r"/"),
    ("PERCENT", r"%"),
    ("BANG", r"!"),
    ("LT", r"<"),
    ("GT", r">"),
    ("EQUAL", r"="),
    ("IDENT", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t\r]+"),
    ("MISMATCH", r"."),
]

_TOKEN_REGEX = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in _TOKEN_SPECIFICATION),
    flags=re.DOTALL,
)

_KEYWORDS = {
    "fn": "FN",
    "async": "ASYNC",
    "let": "LET",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "return": "RETURN",
    "await": "AWAIT",
    "for": "FOR",
    "in": "IN",
    "true": "TRUE",
    "false": "FALSE",
    "use": "USE",
}


class HololangSyntaxError(RuntimeError):
    """Excepción levantada cuando el parser encuentra una construcción inválida."""


def _tokenize(source: str) -> Iterator[LexToken]:
    """Genera los tokens léxicos internos a partir del código fuente."""

    for match in _TOKEN_REGEX.finditer(source):
        kind = match.lastgroup or "MISMATCH"
        value = match.group()
        if kind in {"COMMENT", "MULTICOMMENT", "SKIP", "NEWLINE"}:
            continue
        if kind == "IDENT":
            kind = _KEYWORDS.get(value, "IDENT")
        elif kind == "STRING":
            value = bytes(value[1:-1], "utf-8").decode("unicode_escape")
        elif kind == "MISMATCH":
            raise HololangSyntaxError(f"Símbolo inesperado: {value!r}")
        yield LexToken(kind, value, match.start())
    yield LexToken("EOF", "", len(source))


# ---------------------------------------------------------------------------
# Parser recursivo de Hololang


_OPERATOR_PRECEDENCE = {
    "OR": 1,
    "AND": 2,
    "EQ": 3,
    "NE": 3,
    "LT": 4,
    "LE": 4,
    "GT": 4,
    "GE": 4,
    "PLUS": 5,
    "MINUS": 5,
    "STAR": 6,
    "SLASH": 6,
    "PERCENT": 6,
}

_OPERATOR_MAP = {
    "PLUS": Token(TipoToken.SUMA, "+"),
    "MINUS": Token(TipoToken.RESTA, "-"),
    "STAR": Token(TipoToken.MULT, "*"),
    "SLASH": Token(TipoToken.DIV, "/"),
    "PERCENT": Token(TipoToken.MOD, "%"),
    "EQ": Token(TipoToken.IGUAL, "=="),
    "NE": Token(TipoToken.DIFERENTE, "!="),
    "LT": Token(TipoToken.MENORQUE, "<"),
    "LE": Token(TipoToken.MENORIGUAL, "<="),
    "GT": Token(TipoToken.MAYORQUE, ">"),
    "GE": Token(TipoToken.MAYORIGUAL, ">="),
    "AND": Token(TipoToken.AND, "&&"),
    "OR": Token(TipoToken.OR, "||"),
}


class HololangParser:
    """Parser recursivo descendente para el subconjunto de Hololang soportado."""

    def __init__(self, *, include_use: bool = True) -> None:
        self.include_use = include_use
        self.tokens: List[LexToken] = []
        self.position = 0

    # ------------------------------
    # Utilidades básicas
    def parse(self, source: str) -> List[Any]:
        """Analiza el código Hololang y devuelve los nodos AST equivalentes."""

        self.tokens = list(_tokenize(source))
        self.position = 0
        ast: List[Any] = []
        while not self._check("EOF"):
            if self._check("SEMICOLON"):
                self._advance()
                continue
            node = self._parse_statement()
            if node is None:
                continue
            if isinstance(node, list):
                ast.extend(node)
            else:
                ast.append(node)
        return ast

    def _current(self) -> LexToken:
        return self.tokens[self.position]

    def _advance(self) -> LexToken:
        token = self.tokens[self.position]
        if token.type != "EOF":
            self.position += 1
        return token

    def _check(self, token_type: str) -> bool:
        return self._current().type == token_type

    def _match(self, *token_types: str) -> bool:
        if self._current().type in token_types:
            self._advance()
            return True
        return False

    def _expect(self, token_type: str, message: Optional[str] = None) -> LexToken:
        if not self._check(token_type):
            actual = self._current().value
            raise HololangSyntaxError(message or f"Se esperaba {token_type} y se encontró {actual!r}")
        return self._advance()

    def _parse_statement(self) -> Optional[Any]:
        token = self._current()
        if token.type == "USE":
            return self._parse_use()
        if token.type in {"ASYNC", "FN"}:
            return self._parse_function()
        if token.type == "IF":
            return self._parse_if()
        if token.type == "WHILE":
            return self._parse_while()
        if token.type == "FOR":
            return self._parse_for()
        if token.type == "RETURN":
            return self._parse_return()
        if token.type == "AWAIT":
            return self._parse_await()
        if token.type == "LET":
            return self._parse_assignment(True)
        if token.type == "IDENT":
            # Podría ser asignación o expresión
            if self._is_assignment_start():
                return self._parse_assignment(False)
            expr = self._parse_expression()
            self._expect("SEMICOLON")
            return expr
        if token.type == "LBRACE":
            return self._parse_block()
        if token.type == "SEMICOLON":
            self._advance()
            return None
        raise HololangSyntaxError(f"Sentencia no soportada en posición {token.position}")

    # ------------------------------
    # Sentencias específicas
    def _parse_use(self) -> Optional[NodoUsar]:
        self._advance()  # consume 'use'
        modulo_tokens: List[str] = []
        while not self._check("SEMICOLON") and not self._check("EOF"):
            modulo_tokens.append(self._advance().value)
        self._expect("SEMICOLON")
        if not self.include_use:
            return None
        modulo = "".join(modulo_tokens).strip()
        return NodoUsar(modulo)

    def _parse_function(self) -> NodoFuncion:
        asincronica = self._match("ASYNC")
        self._expect("FN")
        nombre = self._expect("IDENT").value
        type_params: List[str] = []
        if self._match("LT"):
            type_params = self._parse_type_parameters()
        self._expect("LPAREN")
        parametros: List[str] = []
        if not self._check("RPAREN"):
            parametros = self._parse_parameters()
        self._expect("RPAREN")
        cuerpo = self._parse_block()
        return NodoFuncion(nombre, parametros, cuerpo, asincronica=asincronica, type_params=type_params)

    def _parse_type_parameters(self) -> List[str]:
        params: List[str] = []
        current: List[str] = []
        depth = 1
        while depth > 0 and not self._check("EOF"):
            token = self._advance()
            if token.type == "LT":
                depth += 1
            elif token.type == "GT":
                depth -= 1
                if depth == 0:
                    break
            elif token.type == "COMMA" and depth == 1:
                params.append("".join(current).strip())
                current = []
                continue
            current.append(token.value)
        if current:
            params.append("".join(current).strip())
        return params

    def _parse_parameters(self) -> List[str]:
        params: List[str] = []
        while True:
            ident = self._expect("IDENT").value
            params.append(ident)
            if not self._match("COMMA"):
                break
        return params

    def _parse_block(self) -> List[Any]:
        self._expect("LBRACE")
        nodos: List[Any] = []
        while not self._check("RBRACE"):
            if self._check("EOF"):
                raise HololangSyntaxError("Bloque sin cerrar")
            stmt = self._parse_statement()
            if stmt is None:
                continue
            if isinstance(stmt, list):
                nodos.extend(stmt)
            else:
                nodos.append(stmt)
        self._expect("RBRACE")
        return nodos

    def _parse_if(self) -> NodoCondicional:
        self._advance()
        self._expect("LPAREN")
        condicion = self._parse_expression()
        self._expect("RPAREN")
        bloque_si = self._parse_block()
        bloque_sino: List[Any] = []
        if self._match("ELSE"):
            if self._check("IF"):
                bloque_sino = [self._parse_if()]
            else:
                if self._check("LBRACE"):
                    bloque_sino = self._parse_block()
                else:
                    stmt = self._parse_statement()
                    if stmt is None:
                        bloque_sino = []
                    elif isinstance(stmt, list):
                        bloque_sino = stmt
                    else:
                        bloque_sino = [stmt]
        return NodoCondicional(condicion, bloque_si, bloque_sino)

    def _parse_while(self) -> NodoBucleMientras:
        self._advance()
        self._expect("LPAREN")
        condicion = self._parse_expression()
        self._expect("RPAREN")
        cuerpo = self._parse_block()
        return NodoBucleMientras(condicion, cuerpo)

    def _parse_for(self) -> NodoPara:
        self._advance()
        self._expect("LPAREN")
        variable_expr = self._parse_expression()
        self._expect("IN")
        iterable = self._parse_expression()
        self._expect("RPAREN")
        cuerpo = self._parse_block()
        variable = variable_expr
        if isinstance(variable_expr, NodoIdentificador):
            variable = variable_expr.nombre
        return NodoPara(variable, iterable, cuerpo)

    def _parse_return(self) -> NodoRetorno:
        self._advance()
        if self._check("SEMICOLON"):
            self._advance()
            return NodoRetorno(NodoValor(None))
        expresion = self._parse_expression()
        self._expect("SEMICOLON")
        return NodoRetorno(expresion)

    def _parse_await(self) -> NodoEsperar:
        self._advance()
        expresion = self._parse_expression()
        self._expect("SEMICOLON")
        return NodoEsperar(expresion)

    def _parse_assignment(self, has_let: bool) -> Any:
        tipo: Optional[str] = None
        nombre_id: Optional[str] = None
        if has_let:
            self._expect("LET")
        target_expr, nombre_id = self._parse_assignment_target()
        if has_let and self._match("COLON"):
            tipo = self._collect_until({"EQUAL"}).strip()
        self._expect("EQUAL")
        valor = self._parse_expression()
        self._expect("SEMICOLON")
        return self._construir_asignacion(target_expr, nombre_id, valor, tipo)

    def _parse_assignment_target(self) -> tuple[Any, Optional[str]]:
        base = self._expect("IDENT").value
        current: Any = base
        nombre_base = base
        while self._match("DOT"):
            atributo = self._expect("IDENT").value
            if isinstance(current, str):
                current = NodoIdentificador(current)
            current = NodoAtributo(current, atributo)
        return current, nombre_base

    def _collect_until(self, stop_tokens: set[str]) -> str:
        collected: List[str] = []
        while not self._check("EOF") and self._current().type not in stop_tokens:
            collected.append(self._advance().value)
        return "".join(collected)

    def _construir_asignacion(
        self,
        destino: Any,
        nombre: Optional[str],
        valor: Any,
        tipo: Optional[str],
    ) -> Any:
        if isinstance(valor, NodoLlamadaFuncion) and valor.nombre == "Holobit::new" and nombre:
            valores = []
            if valor.argumentos and isinstance(valor.argumentos[0], NodoLista):
                for elemento in valor.argumentos[0].elementos:
                    if isinstance(elemento, NodoValor):
                        valores.append(elemento.valor)
                    elif (
                        isinstance(elemento, NodoOperacionUnaria)
                        and elemento.operador.tipo == TipoToken.RESTA
                        and isinstance(elemento.operando, NodoValor)
                    ):
                        valores.append(-elemento.operando.valor)
                    else:
                        valores.append(elemento)
            return NodoHolobit(nombre, valores)
        asignacion = NodoAsignacion(destino, valor)
        if tipo is not None:
            setattr(asignacion, "tipo", tipo)
        return asignacion

    def _is_assignment_start(self) -> bool:
        lookahead = self.tokens[self.position + 1]
        if lookahead.type == "EQUAL":
            return True
        if lookahead.type == "DOT":
            idx = self.position + 2
            while idx < len(self.tokens):
                tkn = self.tokens[idx]
                if tkn.type == "IDENT":
                    idx += 1
                    continue
                if tkn.type == "DOT":
                    idx += 1
                    continue
                return tkn.type == "EQUAL"
            return False
        return False

    # ------------------------------
    # Expresiones
    def _parse_expression(self, precedence: int = 0) -> Any:
        expr = self._parse_unary()
        while True:
            token = self._current()
            op_type = self._binary_operator_type(token)
            if op_type is None:
                break
            op_prec = _OPERATOR_PRECEDENCE[op_type]
            if op_prec < precedence:
                break
            self._advance()
            right = self._parse_expression(op_prec + 1)
            expr = NodoOperacionBinaria(expr, _OPERATOR_MAP[op_type], right)
        return expr

    def _binary_operator_type(self, token: LexToken) -> Optional[str]:
        if token.type in {"PLUS", "MINUS", "STAR", "SLASH", "PERCENT"}:
            return token.type
        if token.type == "OP":
            if token.value == "==":
                return "EQ"
            if token.value == "!=":
                return "NE"
            if token.value == "<=":
                return "LE"
            if token.value == ">=":
                return "GE"
            if token.value == "||":
                return "OR"
            if token.value == "&&":
                return "AND"
        if token.type == "LT":
            return "LT"
        if token.type == "GT":
            return "GT"
        return None

    def _parse_unary(self) -> Any:
        token = self._current()
        if token.type in {"BANG", "MINUS"}:
            self._advance()
            operador = Token(TipoToken.NOT, "!") if token.type == "BANG" else Token(TipoToken.RESTA, "-")
            if token.type == "MINUS":
                operador = Token(TipoToken.RESTA, "-")
            right = self._parse_unary()
            return NodoOperacionUnaria(operador, right)
        return self._parse_postfix()

    def _parse_postfix(self) -> Any:
        expr = self._parse_primary()
        while True:
            if self._match("LPAREN"):
                argumentos = []
                if not self._check("RPAREN"):
                    argumentos = self._parse_argument_list()
                self._expect("RPAREN")
                if isinstance(expr, NodoAtributo):
                    expr = NodoLlamadaMetodo(expr.objeto, expr.nombre, argumentos)
                elif isinstance(expr, NodoIdentificador):
                    expr = NodoLlamadaFuncion(expr.nombre, argumentos)
                elif isinstance(expr, str):
                    expr = NodoLlamadaFuncion(expr, argumentos)
                else:
                    expr = NodoLlamadaFuncion(expr, argumentos)
                continue
            if self._match("DOT"):
                nombre = self._expect("IDENT").value
                if isinstance(expr, str):
                    expr = NodoIdentificador(expr)
                expr = NodoAtributo(expr, nombre)
                continue
            if self._match("DOUBLECOLON"):
                nombre = self._expect("IDENT").value
                if isinstance(expr, str):
                    expr = f"{expr}::{nombre}"
                elif isinstance(expr, NodoIdentificador):
                    expr = f"{expr.nombre}::{nombre}"
                else:
                    expr = f"{expr}.{nombre}"
                continue
            break
        return expr

    def _parse_argument_list(self) -> List[Any]:
        args: List[Any] = []
        while True:
            args.append(self._parse_expression())
            if not self._match("COMMA"):
                break
        return args

    def _parse_primary(self) -> Any:
        token = self._advance()
        if token.type == "NUMBER":
            if "." in token.value:
                return NodoValor(float(token.value))
            return NodoValor(int(token.value))
        if token.type == "STRING":
            return NodoValor(token.value)
        if token.type == "TRUE":
            return NodoValor(True)
        if token.type == "FALSE":
            return NodoValor(False)
        if token.type == "IDENT":
            return NodoIdentificador(token.value)
        if token.type == "LPAREN":
            expr = self._parse_expression()
            self._expect("RPAREN")
            return expr
        if token.type == "LBRACKET":
            elementos: List[Any] = []
            if not self._check("RBRACKET"):
                while True:
                    elementos.append(self._parse_expression())
                    if not self._match("COMMA"):
                        break
            self._expect("RBRACKET")
            return NodoLista(elementos)
        if token.type == "LBRACE":
            pares = []
            if not self._check("RBRACE"):
                while True:
                    clave = self._parse_expression()
                    self._expect("COLON")
                    valor = self._parse_expression()
                    pares.append((clave, valor))
                    if not self._match("COMMA"):
                        break
            self._expect("RBRACE")
            return NodoDiccionario(pares)
        raise HololangSyntaxError(f"Expresión no soportada en posición {token.position}")


def parse_hololang(source: str, *, include_use: bool = True) -> List[Any]:
    """Función de conveniencia que devuelve el AST para el código dado."""

    return HololangParser(include_use=include_use).parse(source)
