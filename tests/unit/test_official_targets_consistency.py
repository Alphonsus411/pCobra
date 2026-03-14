from pathlib import Path

from pcobra.cobra.cli.commands.bench_cmd import BACKENDS as BENCH_BACKENDS
from pcobra.cobra.cli.commands.benchmarks_cmd import BACKENDS as BENCHMARKS_BACKENDS
from pcobra.cobra.cli.commands.compile_cmd import LANG_CHOICES
from pcobra.cobra.cli.commands.transpilar_inverso_cmd import EXTENSIONES_POR_LENGUAJE
from pcobra.cobra.transpilers.common.utils import STANDARD_IMPORTS
from pcobra.cobra.transpilers.feature_inspector import TRANSPILERS as FEATURE_INSPECTOR_TRANSPILERS
from pcobra.cobra.transpilers.reverse.policy import REVERSE_SCOPE_LANGUAGES
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS


def _extract_backend_from_filename(path: Path, prefix: str = "to_") -> str:
    return path.stem.removeprefix(prefix)


def test_cli_y_transpilers_no_exponen_targets_fuera_de_whitelist_oficial():
    oficiales = set(OFFICIAL_TARGETS)

    assert tuple(LANG_CHOICES) == OFFICIAL_TARGETS
    assert set(STANDARD_IMPORTS.keys()).issubset(oficiales)
    assert set(BENCH_BACKENDS.keys()).issubset(oficiales)
    assert set(BENCHMARKS_BACKENDS.keys()).issubset(oficiales)
    assert set(FEATURE_INSPECTOR_TRANSPILERS.keys()).issubset(oficiales)


def test_mapa_reverse_extensions_esta_alineado_con_scope_reverse():
    reverse_scope = set(REVERSE_SCOPE_LANGUAGES)
    extension_keys = set(EXTENSIONES_POR_LENGUAJE.keys())

    assert reverse_scope.issubset(extension_keys)
    assert {"javascript", "js"}.intersection(extension_keys)


def test_archivos_to_py_en_transpiler_oficiales():
    base = Path("src/pcobra/cobra/transpilers/transpiler")
    found = {
        _extract_backend_from_filename(path)
        for path in base.glob("to_*.py")
        if path.name != "to_js.py"
    }
    if (base / "to_js.py").exists():
        found.add("javascript")

    oficiales = set(OFFICIAL_TARGETS)
    fuera_de_scope = sorted(found - oficiales)
    assert not fuera_de_scope, (
        "Se encontraron transpilers fuera de los 8 targets oficiales: "
        f"{', '.join(fuera_de_scope)}. "
        f"Oficiales: {', '.join(OFFICIAL_TARGETS)}"
    )


def test_archivos_reverse_from_py_en_scope_reverse():
    base = Path("src/pcobra/cobra/transpilers/reverse")
    found = {
        _extract_backend_from_filename(path, prefix="from_")
        for path in base.glob("from_*.py")
        if path.name != "from_js.py"
    }
    if (base / "from_js.py").exists():
        found.add("javascript")

    reverse_scope = set(REVERSE_SCOPE_LANGUAGES)
    fuera_de_scope = sorted(found - reverse_scope)
    assert not fuera_de_scope, (
        "Se encontraron reverse transpilers fuera del alcance definido en policy.py: "
        f"{', '.join(fuera_de_scope)}. "
        f"Permitidos reverse: {', '.join(REVERSE_SCOPE_LANGUAGES)}"
    )
