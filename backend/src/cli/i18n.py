import gettext
import os
import traceback

# Traducciones mínimas para mensajes del traceback.
_TRACEBACK_TRANSLATIONS = {
    "es": {
        "header": "Rastreo (llamadas más recientes al final):",
        "file": "Archivo",
        "line": "línea",
    },
    "en": {
        "header": "Traceback (most recent call last):",
        "file": "File",
        "line": "line",
    },
}

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
LOCALE_DIR = os.path.join(ROOT_DIR, "frontend", "docs", "locale")

_ = gettext.gettext


def setup_gettext(lang: str | None = None):
    """Inicializa gettext y devuelve la función de traducción."""
    selected = lang or os.environ.get("COBRA_LANG", "es")
    translation = gettext.translation(
        "cobra", localedir=LOCALE_DIR, languages=[selected], fallback=True
    )
    global _
    _ = translation.gettext
    return _


def format_traceback(exc: BaseException, lang: str | None = None) -> str:
    """Devuelve el traceback formateado en el idioma indicado."""
    selected = lang or os.environ.get("COBRA_LANG", "es")
    tr = _TRACEBACK_TRANSLATIONS.get(selected, _TRACEBACK_TRANSLATIONS["es"])

    lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
    out: list[str] = []
    for line in lines:
        if line.startswith("Traceback (most recent call last):"):
            out.append(tr["header"] + "\n")
            continue
        if line.strip().startswith("File "):
            line = line.replace("File", tr["file"]).replace("line", tr["line"])
        out.append(line)
    return "".join(out)


__all__ = ["_", "setup_gettext", "format_traceback"]
