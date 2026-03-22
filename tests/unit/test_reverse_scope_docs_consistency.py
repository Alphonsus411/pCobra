import re
from pathlib import Path

from pcobra.cobra.transpilers.reverse.policy import (
    REVERSE_SCOPE_CLASS_NAMES,
    REVERSE_SCOPE_LANGUAGES,
    REVERSE_SCOPE_MODULES,
)


def _normalizar(token: str) -> str:
    return token.strip().lower()


def test_docs_lenguajes_transpiladores_inversos_alineado_con_scope():
    contenido = Path("docs/lenguajes.rst").read_text(encoding="utf-8")
    bloque = contenido.split(
        "Orígenes reverse de entrada (no targets de salida)", maxsplit=1
    )[1]
    bloque = bloque.split("Instalación de gramáticas", maxsplit=1)[0]

    encontrados = {
        _normalizar(m.group(1))
        for m in re.finditer(r"\* -\s+([A-Za-z\+]+)\s*\n\s+-\s+Experimental", bloque)
    }
    assert encontrados == set(REVERSE_SCOPE_LANGUAGES)


def test_readme_lista_de_reverse_scope_alineada_con_policy():
    contenido = Path("README.md").read_text(encoding="utf-8")
    linea = next(
        l
        for l in contenido.splitlines()
        if "Actualmente la transpilación inversa soportada por política acepta código de entrada" in l
    )
    prefix = linea.split(". Esos tres nombres", maxsplit=1)[0]
    encontrados = {
        _normalizar(token)
        for token in re.findall(r"`([^`]+)`", prefix)
    }
    assert encontrados == set(REVERSE_SCOPE_LANGUAGES)


def test_contributing_checklist_reverse_scope_alineada_con_policy():
    contenido = Path("CONTRIBUTING.md").read_text(encoding="utf-8")
    linea = next(
        l
        for l in contenido.splitlines()
        if "transpilar-inverso" in l and "orígenes oficiales" in l
    )
    encontrados = {
        _normalizar(token)
        for token in re.findall(r"`([^`]+)`", linea)
        if _normalizar(token) in set(REVERSE_SCOPE_LANGUAGES)
    }
    assert encontrados == set(REVERSE_SCOPE_LANGUAGES)


def test_docs_reverse_no_confunden_origenes_con_targets_oficiales_de_salida():
    contenido = Path("docs/lenguajes.rst").read_text(encoding="utf-8")
    assert "Orígenes reverse de entrada (no targets de salida)" in contenido
    assert "runtime oficial" in contenido
    assert "transpilación" in contenido


def test_policy_reverse_define_solo_modulos_y_clases_canonicas():
    assert REVERSE_SCOPE_LANGUAGES == ("python", "javascript", "java")
    assert REVERSE_SCOPE_MODULES == {
        "python": "pcobra.cobra.transpilers.reverse.from_python",
        "javascript": "pcobra.cobra.transpilers.reverse.from_js",
        "java": "pcobra.cobra.transpilers.reverse.from_java",
    }
    assert REVERSE_SCOPE_CLASS_NAMES == {
        "python": "ReverseFromPython",
        "javascript": "ReverseFromJS",
        "java": "ReverseFromJava",
    }
