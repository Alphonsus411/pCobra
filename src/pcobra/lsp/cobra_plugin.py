from __future__ import annotations

"""Plugin de completado para palabras clave y funciones estándar de Cobra."""

import logging
import re
from pylsp import hookimpl, lsp
from standard_library import __all__ as STD_FUNCS
from pcobra.cobra.core import Lexer, LexerError
from pcobra.cobra.core import Parser, ParserError
from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand

# Palabras reservadas más comunes de Cobra
KEYWORDS = [
    "func",
    "clase",
    "metodo",
    "atributo",
    "si",
    "sino",
    "para",
    "mientras",
    "romper",
    "continuar",
    "regresar",
    "importar",
    "intentar",
    "excepto",
    "fin",
]

# Funciones incluidas en la biblioteca estándar
BUILTINS = list(STD_FUNCS) + ["imprimir"]


def lint_lines(lines: list[str]):
    """Devuelve diagnósticos básicos de estilo."""
    diagnostics: list[dict] = []
    for idx, line in enumerate(lines):
        if line.rstrip() != line:
            diagnostics.append(
                {
                    "source": "cobra-lint",
                    "range": {
                        "start": {"line": idx, "character": len(line.rstrip())},
                        "end": {"line": idx, "character": len(line)},
                    },
                    "message": "Espacios en blanco al final de la línea",
                    "severity": lsp.DiagnosticSeverity.Warning,
                }
            )
        if "\t" in line:
            col = line.index("\t")
            diagnostics.append(
                {
                    "source": "cobra-lint",
                    "range": {
                        "start": {"line": idx, "character": col},
                        "end": {"line": idx, "character": col + 1},
                    },
                    "message": "Usa espacios en lugar de tabulaciones",
                    "severity": lsp.DiagnosticSeverity.Warning,
                }
            )
        if len(line) > 79:
            diagnostics.append(
                {
                    "source": "cobra-lint",
                    "range": {
                        "start": {"line": idx, "character": 79},
                        "end": {"line": idx, "character": len(line)},
                    },
                    "message": "Línea supera los 79 caracteres",
                    "severity": lsp.DiagnosticSeverity.Warning,
                }
            )
    return diagnostics


@hookimpl
def pylsp_settings():
    """Activa el plugin por defecto."""
    return {"plugins": {"cobra": {"enabled": True}}}


@hookimpl
def pylsp_completions(config, workspace, document, position):
    """Devuelve sugerencias de autocompletado para Cobra."""
    line = document.lines[position["line"]]
    prefix_match = re.search(r"\w*$", line[: position["character"]])
    prefix = prefix_match.group(0) if prefix_match else ""

    items = []
    for word in KEYWORDS:
        if word.startswith(prefix):
            items.append(
                {
                    "label": word,
                    "kind": lsp.CompletionItemKind.Keyword,
                    "detail": "Palabra clave Cobra",
                }
            )
    for func in BUILTINS:
        if func.startswith(prefix):
            items.append(
                {
                    "label": func,
                    "kind": lsp.CompletionItemKind.Function,
                    "detail": "Función estándar Cobra",
                }
            )
    return items or None


@hookimpl
def pylsp_diagnostics(config, workspace, document, **_args):
    """Valida el documento y reporta errores de sintaxis."""
    codigo = document.source
    diagnostics = []
    parser: Parser | None = None
    try:
        tokens = Lexer(codigo).tokenizar()
        parser = Parser(tokens)
        parser.parsear()
    except LexerError as exc:
        line = getattr(exc, "linea", 1) - 1
        col = getattr(exc, "columna", 1) - 1
        diagnostics.append(
            {
                "source": "cobra",
                "range": {
                    "start": {"line": line, "character": col},
                    "end": {"line": line, "character": col + 1},
                },
                "message": str(exc),
                "severity": lsp.DiagnosticSeverity.Error,
            }
        )
    except ParserError as exc:
        token = parser.token_actual() if parser is not None else None
        line = getattr(token, "linea", 1) - 1 if token else 0
        col = getattr(token, "columna", 1) - 1 if token else 0
        diagnostics.append(
            {
                "source": "cobra",
                "range": {
                    "start": {"line": line, "character": col},
                    "end": {"line": line, "character": col + 1},
                },
                "message": str(exc),
                "severity": lsp.DiagnosticSeverity.Error,
            }
        )

    diagnostics.extend(lint_lines(document.lines))
    return diagnostics


@hookimpl
def pylsp_format_document(config, workspace, document):
    """Formatea el archivo actual utilizando el formateador de Cobra."""
    path = document.path
    try:
        ExecuteCommand._formatear_codigo(path)
        with open(path, "r", encoding="utf-8") as fh:
            formatted = fh.read()
    except Exception as exc:
        logging.exception("Error al formatear el documento %s", path)
        raise RuntimeError(
            f"No se pudo formatear el documento {path}: {exc}"
        ) from exc
    return [
        {
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": len(document.lines), "character": 0},
            },
            "newText": formatted,
        }
    ]
