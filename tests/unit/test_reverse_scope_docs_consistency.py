import re
from pathlib import Path

from pcobra.cobra.transpilers.reverse.policy import REVERSE_SCOPE_LANGUAGES


def _normalizar(token: str) -> str:
    t = token.strip().lower()
    aliases = {
        "javascript": "js",
    }
    return aliases.get(t, t)


def test_docs_lenguajes_transpiladores_inversos_alineado_con_scope():
    contenido = Path("docs/lenguajes.rst").read_text(encoding="utf-8")
    bloque = contenido.split("Transpiladores inversos", maxsplit=1)[1]
    bloque = bloque.split("Instalación de gramáticas", maxsplit=1)[0]

    encontrados = {
        _normalizar(m.group(1))
        for m in re.finditer(r"\* -\s+([A-Za-z\+]+)\s*\n\s+-\s+Experimental", bloque)
    }
    assert encontrados == set(REVERSE_SCOPE_LANGUAGES)


def test_readme_lista_de_reverse_scope_alineada_con_policy():
    contenido = Path("README.md").read_text(encoding="utf-8")
    linea = next(
        l for l in contenido.splitlines()
        if l.startswith("Actualmente es posible convertir a Cobra código escrito en")
    )
    encontrados = {
        _normalizar(token)
        for token in re.findall(r"`([^`]+)`", linea)
    }
    assert encontrados == set(REVERSE_SCOPE_LANGUAGES)
