from __future__ import annotations

"""Plugin de completado para palabras clave y funciones estándar de Cobra."""

import re
from pylsp import hookimpl, lsp
from standard_library import __all__ as STD_FUNCS

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
