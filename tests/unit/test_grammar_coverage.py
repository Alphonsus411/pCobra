"""Pruebas unitarias para el reporte de cobertura de la gramática."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from lark import Lark


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts/grammar_coverage.py"
SPEC = importlib.util.spec_from_file_location("grammar_coverage", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
grammar_coverage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(grammar_coverage)


def test_iter_sample_files_descubre_archivos_cobra_anidados(tmp_path: Path) -> None:
    muestra = tmp_path / "nivel" / "interno" / "muestra.cobra"
    muestra.parent.mkdir(parents=True)
    muestra.write_text("variable respuesta = 1\n", encoding="utf-8")

    assert set(grammar_coverage.iter_sample_files([tmp_path])) == {muestra}


def test_iter_sample_files_ignora_otras_extensiones_sin_depender_del_cwd(
    tmp_path: Path, monkeypatch
) -> None:
    muestras = tmp_path / "muestras"
    muestras.mkdir()
    archivo_cobra = muestras / "valido.cobra"
    archivo_cobra.write_text("imprimir(1)\n", encoding="utf-8")
    (muestras / "ignorado.txt").write_text("imprimir(2)\n", encoding="utf-8")
    otro_cwd = tmp_path / "otro-cwd"
    otro_cwd.mkdir()
    monkeypatch.chdir(otro_cwd)

    assert list(grammar_coverage.iter_sample_files([muestras])) == [archivo_cobra]


def test_muestra_cobra_minima_utiliza_reglas(tmp_path: Path) -> None:
    muestra = tmp_path / "minima.cobra"
    muestra.write_text("variable respuesta = 1\n", encoding="utf-8")
    parser = Lark.open(grammar_coverage.GRAMMAR_PATH, parser="earley")
    reglas_usadas: set[str] = set()

    arbol = parser.parse(muestra.read_text(encoding="utf-8"))
    grammar_coverage.visit_tree(arbol, reglas_usadas)

    assert reglas_usadas


def _configurar_cobertura_controlada(tmp_path: Path, monkeypatch) -> float:
    gramatica = tmp_path / "gramatica.ebnf"
    gramatica.write_text(
        'start: asignacion | impresion\n'
        'asignacion: "variable" IDENTIFICADOR "=" ENTERO\n'
        'impresion: "imprimir" "(" ENTERO ")"\n'
        'IDENTIFICADOR: /[^\\W\\d][\\w]*/\n'
        'ENTERO: /[0-9]+/\n'
        '%ignore /\\s+/\n',
        encoding="utf-8",
    )
    muestras = tmp_path / "muestras"
    muestras.mkdir()
    muestra = muestras / "asignacion.cobra"
    muestra.write_text("variable respuesta = 1\n", encoding="utf-8")
    monkeypatch.setattr(grammar_coverage, "GRAMMAR_PATH", gramatica)
    monkeypatch.setattr(grammar_coverage, "SAMPLE_DIRS", [muestras])

    parser = Lark.open(gramatica, parser="earley")
    todas = grammar_coverage.collect_rule_names(parser)
    usadas: set[str] = set()
    grammar_coverage.visit_tree(parser.parse(muestra.read_text()), usadas)
    return 100.0 * len(usadas) / len(todas)


def test_main_devuelve_uno_bajo_el_umbral_controlado(
    tmp_path: Path, monkeypatch
) -> None:
    cobertura = _configurar_cobertura_controlada(tmp_path, monkeypatch)

    assert grammar_coverage.main(cobertura + 1.0) == 1


def test_main_devuelve_cero_al_superar_el_umbral_controlado(
    tmp_path: Path, monkeypatch
) -> None:
    cobertura = _configurar_cobertura_controlada(tmp_path, monkeypatch)

    assert grammar_coverage.main(cobertura - 1.0) == 0
